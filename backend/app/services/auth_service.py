"""
🔐 خدمة المصادقة — Register, Login, Refresh, Tenant Creation
"""
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.organization import Organization
from app.models.subscription import Plan, PlanName, Subscription, SubscriptionStatus
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthError(Exception):
    """أخطاء المصادقة"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthService:
    """
    يُدير جميع عمليات المصادقة وإنشاء المستأجرين
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── التسجيل (Register) ────────────────────────────────
    async def register(self, data: RegisterRequest) -> tuple[UserResponse, TokenResponse]:
        """
        تسجيل مستخدم جديد وإنشاء منظمة جديدة (Tenant)
        """
        # ① التحقق من البريد الإلكتروني
        existing_user = await self.db.scalar(
            select(User).where(User.email == data.email.lower())
        )
        if existing_user:
            raise AuthError("البريد الإلكتروني مسجل مسبقاً", 409)

        # ② التحقق من الـ slug
        existing_org = await self.db.scalar(
            select(Organization).where(Organization.slug == data.org_slug.lower())
        )
        if existing_org:
            raise AuthError("اسم الرابط الخاص بالمنظمة مستخدم، اختر اسماً آخر", 409)

        # ③ إنشاء المنظمة (Tenant)
        schema_name = f"tenant_{str(uuid.uuid4()).replace('-', '_')[:8]}"
        org = Organization(
            name=data.org_name,
            slug=data.org_slug.lower(),
            schema_name=schema_name,
            settings={
                "language": "ar",
                "timezone": "Asia/Riyadh",
                "theme": "light",
            },
        )
        self.db.add(org)
        await self.db.flush()  # للحصول على org.id

        # ④ ربط المنظمة بخطة Starter (تجريبية)
        starter_plan = await self.db.scalar(
            select(Plan).where(Plan.name == PlanName.STARTER)
        )
        if starter_plan:
            from datetime import timedelta
            subscription = Subscription(
                org_id=org.id,
                plan_id=starter_plan.id,
                status=SubscriptionStatus.TRIALING,
                current_period_start=datetime.now(UTC),
                current_period_end=datetime.now(UTC) + timedelta(days=14),
            )
            self.db.add(subscription)

        # ⑤ إنشاء المستخدم (Owner)
        user = User(
            name=data.name,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role=UserRole.OWNER,
            org_id=org.id,
            is_active=True,
            is_verified=False,  # يحتاج تأكيد البريد
        )
        self.db.add(user)
        await self.db.flush()

        # ⑥ توليد الـ Tokens
        tokens = self._generate_tokens(user, org)

        return UserResponse.model_validate(user), tokens

    # ── تسجيل الدخول (Login) ─────────────────────────────
    async def login(self, data: LoginRequest) -> tuple[UserResponse, TokenResponse]:
        """
        تسجيل الدخول وإرجاع الـ tokens
        """
        # البحث عن المستخدم
        user = await self.db.scalar(
            select(User).where(User.email == data.email.lower())
        )

        if not user or not verify_password(data.password, user.password_hash):
            raise AuthError("البريد الإلكتروني أو كلمة المرور غير صحيحة", 401)

        if not user.is_active:
            raise AuthError("الحساب موقوف، تواصل مع الدعم الفني", 403)

        # تحديث وقت آخر تسجيل دخول
        user.last_login = datetime.now(UTC)

        # جلب المنظمة
        org = None
        if user.org_id:
            org = await self.db.get(Organization, user.org_id)

        tokens = self._generate_tokens(user, org)

        return UserResponse.model_validate(user), tokens

    # ── تجديد الـ Token (Refresh) ─────────────────────────
    async def refresh_token(self, user_id: uuid.UUID) -> TokenResponse:
        """
        تجديد Access Token باستخدام Refresh Token صالح
        """
        user = await self.db.get(User, user_id)

        if not user or not user.is_active:
            raise AuthError("المستخدم غير موجود أو موقوف", 401)

        org = None
        if user.org_id:
            org = await self.db.get(Organization, user.org_id)

        return self._generate_tokens(user, org)

    # ── توليد الـ Tokens ──────────────────────────────────
    def _generate_tokens(
        self,
        user: User,
        org: Organization | None,
    ) -> TokenResponse:
        """توليد Access + Refresh tokens"""
        from app.core.config import settings

        access_token = create_access_token(
            subject=str(user.id),
            org_id=str(org.id) if org else None,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            # refresh_token يُرسل في HttpOnly Cookie (يُعالج في الـ endpoint)
        ), refresh_token

    # الإعادة التوافقية
    def _generate_tokens(self, user: User, org: Organization | None):
        from app.core.config import settings
        access_token = create_access_token(
            subject=str(user.id),
            org_id=str(org.id) if org else None,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return token_response, refresh_token
