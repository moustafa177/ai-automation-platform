"""
🔐 Auth Endpoints — تسجيل، دخول، تجديد، خروج
"""
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUserPayload, DBSession
from app.core.security import verify_refresh_token
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import APIResponse, MessageResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["🔐 المصادقة"])

# ── استيراد المحدّد ───────────────────────────────────────
try:
    from app.main import limiter
except ImportError:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)


def _secure_cookie(response: Response, key: str, value: str, max_age: int,
                   path: str, is_production: bool) -> None:
    """دالة مساعدة لضبط Cookie بإعدادات أمان صحيحة"""
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=is_production,   # True في الإنتاج مع HTTPS
        samesite="lax",
        max_age=max_age,
        path=path,
    )


# ── ① تسجيل حساب جديد ────────────────────────────────────
@router.post(
    "/register",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء حساب جديد مع منظمة",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    response: Response,
    db: DBSession,
):
    """
    إنشاء حساب مستخدم جديد مع منظمة جديدة (Tenant).
    يُرجع access_token ويضع refresh_token في HttpOnly Cookie.
    محدود: 5 محاولات / دقيقة لكل IP
    """
    from app.core.config import settings as _s
    service = AuthService(db)
    try:
        user, (token_response, refresh_token) = await service.register(data)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    _secure_cookie(response, "refresh_token", refresh_token,
                   max_age=30 * 24 * 60 * 60,
                   path="/api/v1/auth",
                   is_production=_s.is_production)

    return APIResponse(
        success=True,
        message="تم إنشاء الحساب بنجاح! تحقق من بريدك الإلكتروني لتأكيد الحساب.",
        data={
            "user": user.model_dump(),
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
        },
    )


# ── ② تسجيل الدخول ───────────────────────────────────────
@router.post(
    "/login",
    response_model=APIResponse[dict],
    summary="تسجيل الدخول",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: DBSession,
):
    """
    تسجيل الدخول بالبريد الإلكتروني وكلمة المرور.
    محدود: 10 محاولات / دقيقة لكل IP لمنع Brute Force
    """
    from app.core.config import settings as _s
    service = AuthService(db)
    try:
        user, (token_response, refresh_token) = await service.login(data)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    _secure_cookie(response, "refresh_token", refresh_token,
                   max_age=30 * 24 * 60 * 60,
                   path="/api/v1/auth",
                   is_production=_s.is_production)

    return APIResponse(
        success=True,
        message="مرحباً بعودتك!",
        data={
            "user": user.model_dump(),
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
        },
    )


# ── ③ تجديد الـ Access Token ──────────────────────────────
@router.post(
    "/refresh",
    response_model=APIResponse[dict],
    summary="تجديد Access Token",
)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    response: Response,
    db: DBSession,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    body: RefreshRequest | None = None,
):
    """
    تجديد الـ access token باستخدام refresh token.
    يقرأ من الـ Cookie أولاً، ثم من الـ body.
    """
    from app.core.config import settings as _s
    token = refresh_token_cookie or (body.refresh_token if body else None)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="لا يوجد refresh token",
        )

    payload = verify_refresh_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token غير صالح أو منتهي الصلاحية",
        )

    from uuid import UUID
    service = AuthService(db)
    try:
        token_response, new_refresh_token = await service.refresh_token(
            UUID(payload["sub"])
        )
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Token Rotation — تحديث الـ refresh token
    _secure_cookie(response, "refresh_token", new_refresh_token,
                   max_age=30 * 24 * 60 * 60,
                   path="/api/v1/auth",
                   is_production=_s.is_production)

    return APIResponse(
        data={
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
        }
    )


# ── ④ تسجيل الخروج ───────────────────────────────────────
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="تسجيل الخروج",
)
async def logout(response: Response):
    """
    تسجيل الخروج — حذف الـ refresh token من الـ Cookie.
    """
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return MessageResponse(message="تم تسجيل الخروج بنجاح")


# ── ⑤ بيانات المستخدم الحالي ─────────────────────────────
@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="بيانات المستخدم الحالي",
)
async def get_me(
    payload: CurrentUserPayload,
    db: DBSession,
):
    """
    إرجاع بيانات المستخدم المسجل حالياً.
    """
    from uuid import UUID
    from sqlalchemy import select
    from app.models.user import User

    user = await db.get(User, UUID(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    return APIResponse(data=UserResponse.model_validate(user))


# ── ⑥ نسيان كلمة المرور ──────────────────────────────────
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="طلب إعادة تعيين كلمة المرور",
)
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: DBSession):
    """
    إرسال بريد إلكتروني لإعادة تعيين كلمة المرور.
    يُرجع نفس الرسالة دائماً لمنع تخمين البريد الإلكتروني (Anti-enumeration).
    محدود: 3 محاولات / دقيقة لكل IP
    """
    # TODO: إرسال بريد إلكتروني بالرابط
    return MessageResponse(
        message="إذا كان البريد مسجلاً، ستصلك رسالة خلال دقائق"
    )
