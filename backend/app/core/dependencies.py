"""
🔗 FastAPI Dependencies — حقن المستخدم والمنظمة في كل request
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_access_token

# نوع الـ Bearer token
bearer_scheme = HTTPBearer(auto_error=False)


# ── استخراج المستخدم الحالي من الـ Token ─────────────────
async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict:
    """
    يستخرج بيانات المستخدم من JWT Token
    يُستخدم كـ dependency في الـ endpoints المحمية
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="لم يتم توفير رمز المصادقة",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز المصادقة غير صالح أو منتهي الصلاحية",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# ── الـ Dependencies الجاهزة للاستخدام ───────────────────

# مستخدم مصادق عليه (أي role)
CurrentUserPayload = Annotated[dict, Depends(get_current_user_payload)]

# جلسة قاعدة البيانات
DBSession = Annotated[AsyncSession, Depends(get_db)]


def require_roles(*roles: str):
    """
    Dependency مخصص للتحقق من الـ role
    مثال: Depends(require_roles("owner", "admin"))
    """
    async def check_role(payload: CurrentUserPayload) -> dict:
        user_role = payload.get("role", "")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"هذه العملية تتطلب صلاحية: {', '.join(roles)}",
            )
        return payload
    return check_role


def get_current_org_id(payload: CurrentUserPayload) -> UUID:
    """استخراج معرف المنظمة من الـ token"""
    org_id = payload.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="لم يتم ربط الحساب بمنظمة",
        )
    return UUID(org_id)


def get_current_user_id(payload: CurrentUserPayload) -> UUID:
    """استخراج معرف المستخدم من الـ token"""
    return UUID(payload["sub"])


# Typed dependencies جاهزة
CurrentOrgId = Annotated[UUID, Depends(get_current_org_id)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]

# صلاحيات جاهزة
AdminOrOwner = Annotated[dict, Depends(require_roles("owner", "admin"))]
OwnerOnly = Annotated[dict, Depends(require_roles("owner"))]
