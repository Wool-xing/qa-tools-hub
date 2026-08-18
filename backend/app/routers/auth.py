import re
import time
import uuid
import secrets
import hashlib
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
import bcrypt
import jwt
from jwt import InvalidTokenError
from app.database import get_db
from app.models.user import User
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX, PASSWORD_MIN_LEN, BASE_URL as CONFIG_BASE_URL, TRUST_PROXY
from app.mail import send_password_reset

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ==================== Rate Limiter ====================

_rate_store: dict[str, list[float]] = {}


def _check_rate_limit(key: str, response: "Response | None" = None) -> None:
    now = time.time()
    _cleanup_stale_entries()  # Amortized cleanup on each check
    attempts = [t for t in _rate_store.get(key, []) if now - t < RATE_LIMIT_WINDOW]
    remaining = max(0, RATE_LIMIT_MAX - len(attempts))
    if response:
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + RATE_LIMIT_WINDOW))
    if len(attempts) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)},
        )
    attempts.append(now)
    _rate_store[key] = attempts


def reset_rate_limits():
    _rate_store.clear()


def _client_ip(request: Request) -> str:
    # Only trust XFF behind a proxy that appends the real peer LAST
    # (nginx $proxy_add_x_forwarded_for). Taking the FIRST value lets any
    # client forge the header and bypass rate limiting (QA-2026-08-18 HIGH #4).
    if TRUST_PROXY:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


# ==================== Token Blacklist ====================

_token_blacklist: dict[str, float] = {}  # token → expiry_timestamp


def _revoke_token(token: str):
    """Mark a token as invalid (logout). Tokens auto-expire after their JWT expiry."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp", time.time() + 3600)
        _token_blacklist[token] = exp
    except Exception:
        return


def _cleanup_stale_entries():
    """Remove expired entries from token blacklist and rate store."""
    now = time.time()
    for token, expiry in list(_token_blacklist.items()):
        if now > expiry:
            del _token_blacklist[token]
    for key, timestamps in list(_rate_store.items()):
        _rate_store[key] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if not _rate_store[key]:
            del _rate_store[key]


def _is_token_revoked(token: str) -> bool:
    if token not in _token_blacklist:
        return False
    # Auto-cleanup expired entries
    _cleanup_stale_entries()
    if time.time() > _token_blacklist[token]:
        del _token_blacklist[token]
        return False
    return True


def reset_token_blacklist():
    _token_blacklist.clear()


# ==================== Schemas ====================

_PASSWORD_MIN_LEN = PASSWORD_MIN_LEN
_PASSWORD_PATTERN = re.compile(r'^(?=.*[a-zA-Z])(?=.*\d)')


def _validate_password_strength(v: str) -> str:
    if len(v) < _PASSWORD_MIN_LEN:
        raise ValueError(f"Password must be at least {_PASSWORD_MIN_LEN} characters")
    if not _PASSWORD_PATTERN.search(v):
        raise ValueError("Password must contain at least 1 letter and 1 digit")
    return v


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not (3 <= len(v) <= 32):
            raise ValueError("Username must be 3-32 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must be letters, numbers, or underscore")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', v):
            raise ValueError("Invalid email format")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: int


# ==================== Helpers ====================

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, username: str, is_admin: bool = False) -> str:
    payload = {
        "sub": str(user_id), "username": username,
        "is_admin": is_admin,
        "jti": uuid.uuid4().hex,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    if _is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(user_id_str)
    except (InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


# ==================== Endpoints ====================

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    _check_rate_limit(f"register:{_client_ip(request)}", response)
    r = await db.execute(select(User).where(User.username == data.username))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username taken")
    r = await db.execute(select(User).where(User.email == data.email.strip()))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    # to_thread: bcrypt is CPU-bound (~100-300ms) (QA-2026-08-18 HIGH #6)
    u = User(username=data.username, email=data.email,
             hashed_password=await asyncio.to_thread(hash_password, data.password))
    db.add(u); await db.commit(); await db.refresh(u)
    return TokenResponse(access_token=create_token(u.id, u.username, u.is_admin), username=u.username, user_id=u.id)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    _check_rate_limit(f"login:{_client_ip(request)}", response)
    r = await db.execute(select(User).where(User.username == data.username))
    u = r.scalar_one_or_none()
    if not u or not await asyncio.to_thread(verify_password, data.password, u.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not u.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return TokenResponse(access_token=create_token(u.id, u.username, u.is_admin), username=u.username, user_id=u.id)


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    _revoke_token(token)
    return {"message": "Logged out"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


@router.patch("/me")
async def update_profile(data: ChangePasswordRequest,
                         user: User = Depends(get_current_user),
                         token: str = Depends(oauth2_scheme),
                         db: AsyncSession = Depends(get_db)):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(data.new_password)
    _revoke_token(token)
    await db.commit()
    return {"message": "Password updated"}


# ==================== Account Deletion & Data Export ====================

class DeleteAccountRequest(BaseModel):
    password: str


@router.delete("/me")
async def delete_account(data: DeleteAccountRequest,
                         user: User = Depends(get_current_user),
                         token: str = Depends(oauth2_scheme),
                         db: AsyncSession = Depends(get_db)):
    """Permanently delete account and all associated data."""
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password incorrect")
    # Delete child rows explicitly: test_case/test_run/achievement FKs lack
    # ondelete, and legacy DB files predate the FK PRAGMA (QA-2026-08-18 HIGH #5).
    from app.models.test_case import TestCase
    from app.models.test_run import TestRun
    from app.models.level import UserLevelProgress
    from app.models.achievement import UserAchievement
    from app.models.team import TeamMember
    await db.execute(sa_delete(TestRun).where(TestRun.user_id == user.id))
    await db.execute(sa_delete(TestCase).where(TestCase.user_id == user.id))
    await db.execute(sa_delete(UserLevelProgress).where(UserLevelProgress.user_id == user.id))
    await db.execute(sa_delete(UserAchievement).where(UserAchievement.user_id == user.id))
    await db.execute(sa_delete(TeamMember).where(TeamMember.user_id == user.id))
    await db.delete(user)
    _revoke_token(token)
    await db.commit()
    return {"message": "Account permanently deleted"}


@router.get("/me/export")
async def export_my_data(user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """Export all personal data (GDPR data portability)."""
    from app.models.level import UserLevelProgress, Level
    from app.models.test_case import TestCase
    from app.models.team import TeamMember, Team
    from app.models.achievement import UserAchievement

    progress = (await db.execute(
        select(UserLevelProgress).where(UserLevelProgress.user_id == user.id)
    )).scalars().all()

    testcases = (await db.execute(
        select(TestCase).where(TestCase.user_id == user.id)
    )).scalars().all()

    teams = (await db.execute(
        select(TeamMember, Team.name).join(Team).where(TeamMember.user_id == user.id)
    )).all()

    achievements = (await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )).scalars().all()

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "progress": [{
            "level_id": p.level_id,
            "status": p.status,
            "score": p.score,
            "attempts": p.attempts,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        } for p in progress],
        "testcases": len(testcases),
        "teams": [{"team": name, "role": tm.role} for tm, name in teams],
        "achievements": [a.achievement_key for a in achievements],
    }


# ==================== Password Reset ====================

class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request, response: Response,
                          db: AsyncSession = Depends(get_db)):
    _check_rate_limit(f"forgot:{_client_ip(request)}", response)
    r = await db.execute(select(User).where(User.email == data.email.strip()))
    u = r.scalar_one_or_none()
    if not u:
        return {"message": "If the email is registered, a reset link has been sent."}

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    u.reset_token = token_hash
    u.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    await db.commit()

    base_url = CONFIG_BASE_URL if CONFIG_BASE_URL else str(request.base_url).rstrip("/")
    # to_thread: smtplib blocks up to SMTP_TIMEOUT (QA-2026-08-18 HIGH #6)
    await asyncio.to_thread(send_password_reset, email=u.email, username=u.username, token=token, base_url=base_url)

    return {"message": "If the email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, request: Request, response: Response,
                         db: AsyncSession = Depends(get_db)):
    _check_rate_limit(f"reset:{_client_ip(request)}", response)
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    r = await db.execute(select(User).where(User.reset_token == token_hash))
    u = r.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    expires = u.reset_token_expires
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires and expires < datetime.now(timezone.utc):
        u.reset_token = None
        u.reset_token_expires = None
        await db.commit()
        raise HTTPException(status_code=400, detail="Reset token has expired")

    u.hashed_password = hash_password(data.new_password)
    u.reset_token = None
    u.reset_token_expires = None
    await db.commit()

    return {"message": "Password has been reset. You can now log in."}
