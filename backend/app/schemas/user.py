"""
👤 Schemas المستخدمين والمنظمات
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


# ── User Schemas ──────────────────────────────────────────
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    avatar_url: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    org_id: UUID | None
    is_active: bool
    is_verified: bool
    avatar_url: str | None
    last_login: datetime | None
    created_at: datetime


class UserListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    last_login: datetime | None
    created_at: datetime


# ── Organization Schemas ──────────────────────────────────
class OrgBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None


class OrgCreate(OrgBase):
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrgUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    logo_url: str | None = None
    settings: dict | None = None


class OrgResponse(OrgBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    logo_url: str | None
    is_active: bool
    settings: dict
    created_at: datetime


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER
    name: str = Field(..., min_length=2, max_length=255)
