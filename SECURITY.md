# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ Active |

## Reporting a Vulnerability

**Do not open a public issue.**

Email: security@qatools.local (placeholder — update for your deployment)

We respond within 72 hours. Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

## Security Design

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with configurable algorithm (HS256 default)
- CSRF: token-in-header pattern (no cookies)
- SQL: parameterized queries via SQLAlchemy ORM
- Sandbox: AST validation + subprocess isolation for code execution
- Rate limiting on auth endpoints

## Known Considerations

- JWT stored in localStorage (not HttpOnly cookies) — any XSS = account takeover
- In-memory rate limiter not shared across workers — use Redis for multi-worker
- SQL sandbox uses keyword blocklist — defense-in-depth via subprocess isolation
