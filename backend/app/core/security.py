"""
🔐 أدوات الأمان — JWT + تشفير كلمات المرور
"""
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── تشفير كلمات المرور (bcrypt مباشرة) ────────────────────

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من كلمة المرور"""
    try:
        return _bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ── JWT Tokens ────────────────────────────────────────────
def create_access_token(
    subject: str | Any,
    org_id: str | None = None,
    role: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    إنشاء Access Token (صلاحية قصيرة — 15 دقيقة)

    Args:
        subject:      معرف المستخدم (user_id)
        org_id:       معرف المنظمة للـ multi-tenancy
        role:         دور المستخدم (owner, admin, member, viewer)
        expires_delta: مدة الصلاحية (اختياري)
    """
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }

    if org_id:
        payload["org_id"] = str(org_id)
    if role:
        payload["role"] = role

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """
    إنشاء Refresh Token (صلاحية طويلة — 30 يوم)
    يُخزن في HttpOnly Cookie
    """
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    فك تشفير وتحقق من JWT Token

    Raises:
        JWTError: إذا كان الـ token غير صالح أو منتهي الصلاحية
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_access_token(token: str) -> dict[str, Any] | None:
    """
    التحقق من Access Token وإرجاع البيانات
    يُرجع None إذا كان الـ token غير صالح
    """
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    """
    التحقق من Refresh Token
    """
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
