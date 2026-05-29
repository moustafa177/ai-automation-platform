"""
🔐 Schemas للمصادقة — تسجيل، دخول، tokens
"""
import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


def _strip_html(value: str) -> str:
    """إزالة وسوم HTML/JS من النصوص لمنع XSS"""
    value = re.sub(r"<[^>]*>", "", value)   # أزل وسوم HTML
    value = re.sub(r"javascript:", "", value, flags=re.IGNORECASE)
    value = re.sub(r"on\w+\s*=", "", value, flags=re.IGNORECASE)
    return value.strip()


class RegisterRequest(BaseModel):
    """بيانات إنشاء حساب جديد"""
    name: str = Field(..., min_length=2, max_length=255, examples=["مصطفى أحمد"])
    email: EmailStr = Field(..., examples=["mustafa@company.com"])
    password: str = Field(..., min_length=8, max_length=100)
    org_name: str = Field(..., min_length=2, max_length=255, examples=["شركة الأنظمة الذكية"])
    org_slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$",
                          examples=["smart-systems"])

    @field_validator("name", "org_name", mode="before")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """تعقيم حقول النصوص لمنع XSS"""
        cleaned = _strip_html(str(v))
        if len(cleaned) < 2:
            raise ValueError("النص يحتوي على محتوى غير مسموح به")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
        if not any(c.isdigit() for c in v):
            raise ValueError("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل (!@#$%...)")
        return v


class LoginRequest(BaseModel):
    """بيانات تسجيل الدخول"""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """الـ tokens بعد المصادقة"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # بالثواني


class RefreshRequest(BaseModel):
    """طلب تجديد الـ access token"""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
        if not any(c.isdigit() for c in v):
            raise ValueError("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
        return v


class UserInToken(BaseModel):
    """بيانات المستخدم المضمنة في الـ token"""
    user_id: UUID
    org_id: UUID | None
    email: str
    role: str
