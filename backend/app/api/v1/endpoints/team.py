"""
👥 Team Endpoints — إدارة أعضاء الفريق
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func

from app.core.dependencies import (
    AdminOrOwner,
    CurrentOrgId,
    CurrentUserPayload,
    DBSession,
    OwnerOnly,
    require_roles,
)
from app.models.user import User, UserRole
from app.schemas.common import APIResponse

router = APIRouter(prefix="/team", tags=["👥 الفريق"])


# ── Schemas محلية ─────────────────────────────────────────

class MemberOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class InviteRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class UpdateRoleRequest(BaseModel):
    role: UserRole


# ── ① قائمة أعضاء الفريق ──────────────────────────────────
@router.get(
    "/members",
    response_model=APIResponse[list[MemberOut]],
    summary="قائمة أعضاء الفريق",
)
async def list_members(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    result = await db.execute(
        select(User)
        .where(User.org_id == str(org_id))
        .order_by(User.created_at.asc())
    )
    members = result.scalars().all()

    out = [
        MemberOut(
            id=str(m.id),
            name=m.name,
            email=m.email,
            role=m.role.value,
            is_active=m.is_active,
            is_verified=m.is_verified,
            last_login=m.last_login,
            created_at=m.created_at,
        )
        for m in members
    ]
    return APIResponse(data=out)


# ── ② إحصائيات الفريق ─────────────────────────────────────
@router.get(
    "/stats",
    response_model=APIResponse[dict],
    summary="إحصائيات الفريق",
)
async def team_stats(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    result = await db.execute(
        select(User).where(User.org_id == str(org_id))
    )
    members = result.scalars().all()

    total      = len(members)
    active     = sum(1 for m in members if m.is_active)
    admins     = sum(1 for m in members if m.role in (UserRole.ADMIN, UserRole.OWNER))
    verified   = sum(1 for m in members if m.is_verified)
    by_role    = {}
    for role in UserRole:
        by_role[role.value] = sum(1 for m in members if m.role == role)

    return APIResponse(data={
        "total": total,
        "active": active,
        "admins": admins,
        "verified": verified,
        "pending": total - verified,
        "by_role": by_role,
    })


# ── ③ دعوة عضو جديد (إنشاء مستخدم) ───────────────────────
@router.post(
    "/invite",
    response_model=APIResponse[MemberOut],
    status_code=status.HTTP_201_CREATED,
    summary="دعوة عضو جديد للفريق",
)
async def invite_member(
    data: InviteRequest,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
    db: DBSession,
):
    # تحقق من عدم تكرار البريد
    existing = await db.execute(
        select(User).where(User.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="البريد الإلكتروني مسجّل بالفعل",
        )

    # لا يمكن دعوة Owner
    if data.role == UserRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="لا يمكن تعيين دور المالك من خلال الدعوة",
        )

    from app.core.security import hash_password
    import secrets

    temp_password = secrets.token_urlsafe(16)

    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(temp_password),
        role=data.role,
        org_id=str(org_id),
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # TODO: إرسال بريد دعوة مع كلمة المرور المؤقتة

    out = MemberOut(
        id=str(new_user.id),
        name=new_user.name,
        email=new_user.email,
        role=new_user.role.value,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        last_login=new_user.last_login,
        created_at=new_user.created_at,
    )
    return APIResponse(
        success=True,
        message=f"تمت دعوة {data.name} بنجاح",
        data=out,
    )


# ── ④ تحديث دور عضو ───────────────────────────────────────
@router.put(
    "/members/{member_id}/role",
    response_model=APIResponse[MemberOut],
    summary="تغيير دور عضو",
)
async def update_member_role(
    member_id: UUID,
    data: UpdateRoleRequest,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
    db: DBSession,
):
    member = await db.get(User, member_id)
    if not member or member.org_id != str(org_id):
        raise HTTPException(status_code=404, detail="العضو غير موجود")

    # لا يمكن تغيير دور المالك الأصلي
    if member.role == UserRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="لا يمكن تغيير دور المالك",
        )

    # فقط Owner يمكنه ترقية إلى Admin
    if data.role == UserRole.ADMIN and payload.get("role") != "owner":
        raise HTTPException(
            status_code=403,
            detail="فقط المالك يمكنه تعيين المشرفين",
        )

    member.role = data.role
    await db.commit()
    await db.refresh(member)

    out = MemberOut(
        id=str(member.id),
        name=member.name,
        email=member.email,
        role=member.role.value,
        is_active=member.is_active,
        is_verified=member.is_verified,
        last_login=member.last_login,
        created_at=member.created_at,
    )
    return APIResponse(
        success=True,
        message="تم تحديث الدور",
        data=out,
    )


# ── ⑤ تعطيل / تفعيل عضو ──────────────────────────────────
@router.patch(
    "/members/{member_id}/toggle",
    response_model=APIResponse[dict],
    summary="تفعيل أو تعطيل عضو",
)
async def toggle_member(
    member_id: UUID,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
    db: DBSession,
):
    member = await db.get(User, member_id)
    if not member or member.org_id != str(org_id):
        raise HTTPException(status_code=404, detail="العضو غير موجود")

    if member.role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="لا يمكن تعطيل المالك")

    member.is_active = not member.is_active
    await db.commit()

    status_label = "مفعّل" if member.is_active else "معطّل"
    return APIResponse(
        success=True,
        message=f"تم {status_label} الحساب",
        data={"member_id": str(member_id), "is_active": member.is_active},
    )


# ── ⑥ حذف عضو من الفريق ───────────────────────────────────
@router.delete(
    "/members/{member_id}",
    response_model=APIResponse[dict],
    summary="إزالة عضو من الفريق",
)
async def remove_member(
    member_id: UUID,
    payload: OwnerOnly,
    org_id: CurrentOrgId,
    db: DBSession,
):
    member = await db.get(User, member_id)
    if not member or member.org_id != str(org_id):
        raise HTTPException(status_code=404, detail="العضو غير موجود")

    if member.role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="لا يمكن حذف المالك")

    await db.delete(member)
    await db.commit()

    return APIResponse(
        success=True,
        message=f"تم إزالة {member.name} من الفريق",
        data={"deleted_id": str(member_id)},
    )
