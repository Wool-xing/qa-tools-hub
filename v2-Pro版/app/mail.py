"""Email service for QA通关. Uses SMTP configured via env vars."""

import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
from app import __version__

logger = logging.getLogger("qa-tools")


def is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASS)


def send(recipient: str, subject: str, body_html: str):
    """Send HTML email. Silently no-ops if SMTP not configured."""
    if not is_configured():
        logger.warning("Email skipped (SMTP not configured): %s", subject)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls(context=ctx)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [recipient], msg.as_string())
        logger.info("Email sent: %s → %s", subject, recipient)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", recipient)
        return False


def send_password_reset(email: str, username: str, token: str, base_url: str = "http://localhost:8005"):
    """Send password reset email with reset link."""
    link = f"{base_url}/reset-password?token={token}"
    subject = "QA通关 - 重置密码"
    body = f"""\
<html><body style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
<h2 style="color:#6366f1">QA通关</h2>
<p>{username} 你好，</p>
<p>我们收到了重置密码的请求。点击下方按钮重置密码（30分钟内有效）：</p>
<p style="text-align:center;margin:24px 0">
  <a href="{link}" style="display:inline-block;padding:12px 28px;background:#6366f1;color:#fff;border-radius:6px;text-decoration:none;font-weight:600">重置密码</a>
</p>
<p style="color:#9ca3af;font-size:14px">如果你没有请求重置密码，请忽略此邮件。</p>
<p style="color:#9ca3af;font-size:12px">此链接30分钟后过期 | QA通关 {__version__}</p>
</body></html>"""
    return send(recipient=email, subject=subject, body_html=body)
