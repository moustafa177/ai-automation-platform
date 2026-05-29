"""
⚙️ Settings Endpoints — إعدادات الحساب والمنظمة
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.core.dependencies import (
    AdminOrOwner,
    CurrentOrgId,
    CurrentUserPayload,
    CurrentUserId,
    DBSession,
    OwnerOnly,
)
from app.core.security import hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/settings", tags=["⚙️ الإعدادات"])


# ── Schemas ───────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    avatar_url: str | None = None


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str     = Field(..., min_length=8)


class OrgUpdate(BaseModel):
    name:        str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    logo_url:    str | None = None
    settings:    dict | None = None


class NotifPrefs(BaseModel):
    email_bot_activity:  bool = True
    email_team_updates:  bool = True
    email_weekly_report: bool = False
    push_alerts:         bool = True


# ── ① بيانات الحساب الكاملة ───────────────────────────────
@router.get(
    "/profile",
    response_model=APIResponse[dict],
    summary="بيانات الحساب والمنظمة",
)
async def get_profile(
    payload: CurrentUserPayload,
    user_id: CurrentUserId,
    org_id: CurrentOrgId,
    db: DBSession,
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    org = await db.get(Organization, str(org_id))

    return APIResponse(data={
        "user": {
            "id":          str(user.id),
            "name":        user.name,
            "email":       user.email,
            "role":        user.role.value,
            "avatar_url":  user.avatar_url,
            "is_verified": user.is_verified,
            "is_active":   user.is_active,
            "last_login":  user.last_login.isoformat() if user.last_login else None,
            "created_at":  user.created_at.isoformat() if user.created_at else None,
        },
        "org": {
            "id":          str(org.id) if org else None,
            "name":        org.name if org else None,
            "slug":        org.slug if org else None,
            "description": org.description if org else None,
            "logo_url":    org.logo_url if org else None,
            "settings":    org.settings if org else {},
            "is_active":   org.is_active if org else None,
        } if org else None,
    })


# ── ② تحديث الملف الشخصي ─────────────────────────────────
@router.put(
    "/profile",
    response_model=APIResponse[dict],
    summary="تحديث الاسم والصورة الشخصية",
)
async def update_profile(
    data: ProfileUpdate,
    payload: CurrentUserPayload,
    user_id: CurrentUserId,
    db: DBSession,
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    user.name       = data.name
    user.avatar_url = data.avatar_url
    await db.commit()
    await db.refresh(user)

    return APIResponse(
        success=True,
        message="تم تحديث الملف الشخصي",
        data={"name": user.name, "avatar_url": user.avatar_url},
    )


# ── ③ تغيير كلمة المرور ──────────────────────────────────
@router.post(
    "/change-password",
    response_model=APIResponse[dict],
    summary="تغيير كلمة المرور",
)
async def change_password(
    data: PasswordChange,
    payload: CurrentUserPayload,
    user_id: CurrentUserId,
    db: DBSession,
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="كلمة المرور الحالية غير صحيحة",
        )

    user.password_hash = hash_password(data.new_password)
    await db.commit()

    return APIResponse(
        success=True,
        message="تم تغيير كلمة المرور بنجاح",
        data={},
    )


# ── ④ تحديث إعدادات المنظمة ──────────────────────────────
@router.put(
    "/organization",
    response_model=APIResponse[dict],
    summary="تحديث بيانات المنظمة",
)
async def update_org(
    data: OrgUpdate,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
    db: DBSession,
):
    org = await db.get(Organization, str(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="المنظمة غير موجودة")

    if data.name        is not None: org.name        = data.name
    if data.description is not None: org.description = data.description
    if data.logo_url    is not None: org.logo_url    = data.logo_url
    if data.settings    is not None:
        org.settings = {**org.settings, **data.settings}

    await db.commit()
    await db.refresh(org)

    return APIResponse(
        success=True,
        message="تم تحديث إعدادات المنظمة",
        data={
            "name":        org.name,
            "description": org.description,
            "logo_url":    org.logo_url,
            "settings":    org.settings,
        },
    )


# ── ⑤ قراءة / تحديث تفضيلات الإشعارات ──────────────────
@router.get(
    "/notifications",
    response_model=APIResponse[dict],
    summary="تفضيلات الإشعارات",
)
async def get_notif_prefs(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    org = await db.get(Organization, str(org_id))
    prefs = (org.settings or {}).get("notifications", {
        "email_bot_activity":  True,
        "email_team_updates":  True,
        "email_weekly_report": False,
        "push_alerts":         True,
    })
    return APIResponse(data=prefs)


@router.put(
    "/notifications",
    response_model=APIResponse[dict],
    summary="تحديث تفضيلات الإشعارات",
)
async def update_notif_prefs(
    data: NotifPrefs,
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    org = await db.get(Organization, str(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="المنظمة غير موجودة")

    org.settings = {
        **(org.settings or {}),
        "notifications": data.model_dump(),
    }
    await db.commit()

    return APIResponse(
        success=True,
        message="تم حفظ تفضيلات الإشعارات",
        data=data.model_dump(),
    )


# ── ⑥ تحديث إعدادات الذكاء الاصطناعي ───────────────────
@router.put(
    "/ai",
    response_model=APIResponse[dict],
    summary="تحديث إعدادات الذكاء الاصطناعي",
)
async def update_ai_settings(
    data: dict,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
    db: DBSession,
):
    org = await db.get(Organization, str(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="المنظمة غير موجودة")

    allowed_keys = {"default_model", "default_language", "max_tokens_default",
                    "temperature_default", "enable_rag"}
    filtered = {k: v for k, v in data.items() if k in allowed_keys}

    org.settings = {
        **(org.settings or {}),
        "ai": {**(org.settings or {}).get("ai", {}), **filtered},
    }
    await db.commit()

    return APIResponse(
        success=True,
        message="تم حفظ إعدادات الذكاء الاصطناعي",
        data=org.settings.get("ai", {}),
    )


# ── ⑦ سجل الجلسات النشطة (demo) ──────────────────────────
@router.get(
    "/sessions",
    response_model=APIResponse[list],
    summary="الجلسات النشطة",
)
async def get_sessions(payload: CurrentUserPayload):
    # في الإنتاج: جلب من Redis / session table
    from datetime import datetime, timezone
    return APIResponse(data=[
        {"id":"s1","device":"Chrome / Windows","ip":"197.x.x.1",
         "location":"الرياض، السعودية","current":True,
         "last_active": datetime.now(timezone.utc).isoformat()},
        {"id":"s2","device":"Safari / iPhone","ip":"197.x.x.2",
         "location":"جدة، السعودية","current":False,
         "last_active":"2026-05-27T14:22:00Z"},
    ])
