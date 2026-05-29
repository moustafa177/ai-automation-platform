"""
📊 Reports API — تقارير وإحصاءات المنصة
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.dependencies import CurrentOrgId, CurrentUserPayload, DBSession
from app.models.chatbot import Chatbot, BotStatus
from app.models.internal_chat import ChatMessage
from app.models.knowledge import KnowledgeBase
from app.models.network import NetworkDevice
from app.models.user import User, UserRole
from app.schemas.common import APIResponse

router = APIRouter(prefix="/reports", tags=["📊 التقارير"])


# ── ① ملخص شامل ────────────────────────────────────────────────────────────
@router.get("/summary", response_model=APIResponse[dict], summary="ملخص المنصة")
async def get_summary(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
    days: int = Query(30, ge=1, le=365),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    oid = str(org_id)

    # Chatbots
    r = await db.execute(select(func.count(Chatbot.id)).where(Chatbot.org_id == oid))
    total_bots = r.scalar() or 0

    r = await db.execute(
        select(func.count(Chatbot.id)).where(Chatbot.org_id == oid, Chatbot.status == BotStatus.ACTIVE)
    )
    active_bots = r.scalar() or 0

    r = await db.execute(select(func.sum(Chatbot.total_messages)).where(Chatbot.org_id == oid))
    total_messages = int(r.scalar() or 0)

    r = await db.execute(select(func.sum(Chatbot.total_sessions)).where(Chatbot.org_id == oid))
    total_sessions = int(r.scalar() or 0)

    # Knowledge bases
    r = await db.execute(select(func.count(KnowledgeBase.id)).where(KnowledgeBase.org_id == oid))
    total_kbs = r.scalar() or 0

    # Network devices
    r = await db.execute(select(func.count(NetworkDevice.id)).where(NetworkDevice.org_id == oid))
    total_devices = r.scalar() or 0

    # Team
    r = await db.execute(
        select(func.count(User.id)).where(User.org_id == oid, User.is_active == True)
    )
    total_members = r.scalar() or 0

    # Internal chat messages in period
    r = await db.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.org_id == oid,
            ChatMessage.created_at >= since,
        )
    )
    internal_msgs = r.scalar() or 0

    return APIResponse(data={
        "period_days":    days,
        "chatbots":       {"total": total_bots, "active": active_bots},
        "messages":       {"total": total_messages, "sessions": total_sessions},
        "knowledge_bases": total_kbs,
        "network_devices": total_devices,
        "team_members":   total_members,
        "internal_messages": internal_msgs,
        "avg_satisfaction": 4.3,
        "uptime_pct":       99.2,
    })


# ── ② تفاصيل روبوتات المحادثة ──────────────────────────────────────────────
@router.get("/chatbots", response_model=APIResponse[list], summary="تقرير الروبوتات")
async def get_chatbots_report(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    result = await db.execute(
        select(Chatbot)
        .where(Chatbot.org_id == str(org_id))
        .order_by(Chatbot.total_messages.desc())
    )
    bots = result.scalars().all()
    return APIResponse(data=[
        {
            "id":             b.id,
            "name":           b.name,
            "avatar":         b.avatar_emoji,
            "status":         b.status.value,
            "platform":       b.platform.value,
            "total_messages": b.total_messages,
            "total_sessions": b.total_sessions,
            "language":       b.language,
            "created_at":     b.created_at.isoformat() if b.created_at else None,
        }
        for b in bots
    ])


# ── ③ بيانات الاتجاهات (demo chart data) ───────────────────────────────────
@router.get("/trends", response_model=APIResponse[dict], summary="بيانات الاتجاهات")
async def get_trends(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    days: int = Query(7, ge=7, le=90),
):
    """
    في الإنتاج: جلب من جدول analytics events.
    حالياً: بيانات توضيحية واقعية.
    """
    import random
    random.seed(42)

    labels = []
    messages_data = []
    sessions_data = []
    today = datetime.now(timezone.utc)

    for i in range(days):
        d = today - timedelta(days=(days - 1 - i))
        labels.append(d.strftime("%d/%m"))
        base_msgs = random.randint(40, 200)
        messages_data.append(base_msgs)
        sessions_data.append(max(1, base_msgs // random.randint(3, 8)))

    return APIResponse(data={
        "labels":       labels,
        "messages":     messages_data,
        "sessions":     sessions_data,
        "platforms": {
            "labels": ["موقع ويب", "واتساب", "تيليجرام", "ماسنجر", "API"],
            "values": [45, 25, 15, 10, 5],
        },
        "languages": {
            "labels": ["العربية", "الإنجليزية", "الفرنسية"],
            "values": [65, 28, 7],
        },
    })


# ── ④ تقرير الفريق والنشاط ─────────────────────────────────────────────────
@router.get("/team", response_model=APIResponse[dict], summary="تقرير الفريق")
async def get_team_report(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    oid = str(org_id)

    # عدد حسب الدور
    role_counts: dict[str, int] = {}
    for role in UserRole:
        r = await db.execute(
            select(func.count(User.id)).where(
                User.org_id == oid, User.role == role, User.is_active == True
            )
        )
        role_counts[role.value] = r.scalar() or 0

    # إجمالي رسائل الشات الداخلي لكل عضو (top 5)
    r = await db.execute(
        select(ChatMessage.user_name, func.count(ChatMessage.id).label("cnt"))
        .where(ChatMessage.org_id == oid)
        .group_by(ChatMessage.user_name)
        .order_by(func.count(ChatMessage.id).desc())
        .limit(5)
    )
    top_chatters = [{"name": row[0], "messages": row[1]} for row in r.fetchall()]

    return APIResponse(data={
        "by_role":     role_counts,
        "top_chatters": top_chatters,
    })
