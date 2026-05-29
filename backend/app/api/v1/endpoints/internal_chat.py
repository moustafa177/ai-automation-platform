"""
💬 Internal Chat API — شات داخلي بين أعضاء الفريق
WebSocket للرسائل الفورية + REST للتاريخ
"""
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select

from app.core.database import get_db
from app.core.dependencies import (
    CurrentOrgId,
    CurrentUserPayload,
    CurrentUserId,
    DBSession,
)
from app.core.security import verify_access_token
from app.models.internal_chat import ChannelType, ChatChannel, ChatMessage
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/chat", tags=["💬 الشات الداخلي"])


# ══════════════════════════════════════════════════════════════════
#  WebSocket Connection Manager
# ══════════════════════════════════════════════════════════════════

class ConnectionManager:
    """يدير اتصالات WebSocket مجمّعة حسب (org_id, channel_id)"""

    def __init__(self):
        # {org_id: {channel_id: [WebSocket, ...]}}
        self._rooms: dict[str, dict[str, list[WebSocket]]] = defaultdict(
            lambda: defaultdict(list)
        )

    async def connect(self, ws: WebSocket, org_id: str, channel_id: str):
        await ws.accept()
        self._rooms[org_id][channel_id].append(ws)

    def disconnect(self, ws: WebSocket, org_id: str, channel_id: str):
        try:
            self._rooms[org_id][channel_id].remove(ws)
        except ValueError:
            pass

    async def broadcast(self, payload: dict, org_id: str, channel_id: str):
        dead = []
        for ws in list(self._rooms[org_id].get(channel_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, org_id, channel_id)


manager = ConnectionManager()


# ══════════════════════════════════════════════════════════════════
#  القنوات الافتراضية لكل منظمة جديدة
# ══════════════════════════════════════════════════════════════════

_DEFAULT_CHANNELS = [
    {"name": "عام",           "icon": "🏠", "type": ChannelType.GENERAL},
    {"name": "روبوتات المحادثة", "icon": "🤖", "type": ChannelType.DEPARTMENT},
    {"name": "قاعدة المعرفة",  "icon": "🧠", "type": ChannelType.DEPARTMENT},
    {"name": "مراقبة الشبكة",  "icon": "📡", "type": ChannelType.DEPARTMENT},
    {"name": "الإجراءات",      "icon": "⚡", "type": ChannelType.DEPARTMENT},
    {"name": "إدارة الفريق",   "icon": "👥", "type": ChannelType.DEPARTMENT},
]


async def _ensure_default_channels(org_id: str, db) -> None:
    result = await db.execute(
        select(func.count(ChatChannel.id)).where(ChatChannel.org_id == org_id)
    )
    if (result.scalar() or 0) == 0:
        for ch in _DEFAULT_CHANNELS:
            db.add(ChatChannel(org_id=org_id, **ch))
        await db.commit()


# ══════════════════════════════════════════════════════════════════
#  Schemas
# ══════════════════════════════════════════════════════════════════

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    icon: str = Field("💬", max_length=10)
    type: ChannelType = ChannelType.DEPARTMENT


# ══════════════════════════════════════════════════════════════════
#  REST Endpoints
# ══════════════════════════════════════════════════════════════════

@router.get("/channels", response_model=APIResponse[list], summary="قائمة القنوات")
async def list_channels(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    await _ensure_default_channels(str(org_id), db)
    result = await db.execute(
        select(ChatChannel)
        .where(ChatChannel.org_id == str(org_id), ChatChannel.is_active == True)
        .order_by(ChatChannel.created_at)
    )
    channels = result.scalars().all()
    return APIResponse(data=[
        {"id": c.id, "name": c.name, "icon": c.icon, "type": c.type.value}
        for c in channels
    ])


@router.post("/channels", response_model=APIResponse[dict], summary="إنشاء قناة جديدة")
async def create_channel(
    data: ChannelCreate,
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    ch = ChatChannel(org_id=str(org_id), name=data.name, icon=data.icon, type=data.type)
    db.add(ch)
    await db.commit()
    await db.refresh(ch)
    return APIResponse(
        success=True, message="تم إنشاء القناة",
        data={"id": ch.id, "name": ch.name, "icon": ch.icon, "type": ch.type.value}
    )


@router.get(
    "/channels/{channel_id}/messages",
    response_model=APIResponse[list],
    summary="رسائل قناة",
)
async def get_messages(
    channel_id: str,
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
    limit: int = Query(50, ge=1, le=100),
):
    ch = await db.get(ChatChannel, channel_id)
    if not ch or ch.org_id != str(org_id):
        raise HTTPException(status_code=404, detail="القناة غير موجودة")

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.channel_id == channel_id, ChatMessage.org_id == str(org_id))
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    msgs = list(reversed(result.scalars().all()))
    return APIResponse(data=[
        {
            "id":           m.id,
            "user_id":      m.user_id,
            "user_name":    m.user_name,
            "user_avatar":  m.user_avatar,
            "content":      m.content,
            "message_type": m.message_type,
            "created_at":   m.created_at.isoformat(),
        }
        for m in msgs
    ])


@router.post(
    "/channels/{channel_id}/messages",
    response_model=APIResponse[dict],
    summary="إرسال رسالة",
)
async def send_message(
    channel_id: str,
    data: MessageCreate,
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    user_id: CurrentUserId,
    db: DBSession,
):
    ch = await db.get(ChatChannel, channel_id)
    if not ch or ch.org_id != str(org_id):
        raise HTTPException(status_code=404, detail="القناة غير موجودة")

    user = await db.get(User, str(user_id))
    u_name   = user.name        if user else payload.get("name", "مستخدم")
    u_avatar = (user.avatar_url or "👤") if user else "👤"

    msg = ChatMessage(
        channel_id=channel_id,
        org_id=str(org_id),
        user_id=str(user_id),
        user_name=u_name,
        user_avatar=u_avatar,
        content=data.content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    msg_dict = {
        "id":           msg.id,
        "user_id":      msg.user_id,
        "user_name":    msg.user_name,
        "user_avatar":  msg.user_avatar,
        "content":      msg.content,
        "message_type": msg.message_type,
        "created_at":   msg.created_at.isoformat(),
    }

    # بث الرسالة لجميع المتصلين في هذه القناة
    await manager.broadcast(
        {"type": "message", "channel_id": channel_id, "message": msg_dict},
        str(org_id), channel_id,
    )

    return APIResponse(success=True, message="تم الإرسال", data=msg_dict)


@router.get("/stats", response_model=APIResponse[dict], summary="إحصاءات الشات")
async def chat_stats(
    payload: CurrentUserPayload,
    org_id: CurrentOrgId,
    db: DBSession,
):
    result = await db.execute(
        select(func.count(ChatMessage.id))
        .where(ChatMessage.org_id == str(org_id))
    )
    total = result.scalar() or 0

    ch_result = await db.execute(
        select(func.count(ChatChannel.id))
        .where(ChatChannel.org_id == str(org_id))
    )
    channels = ch_result.scalar() or 0

    return APIResponse(data={"total_messages": total, "total_channels": channels})


# ══════════════════════════════════════════════════════════════════
#  WebSocket
# ══════════════════════════════════════════════════════════════════

@router.websocket("/ws/{channel_id}")
async def websocket_chat(
    ws: WebSocket,
    channel_id: str,
    token: str = Query(...),
):
    """
    اتصال WebSocket للرسائل الفورية.
    المصادقة عبر query param: ?token=<access_token>
    """
    payload = verify_access_token(token)
    if not payload:
        await ws.close(code=4001)
        return

    org_id = payload.get("org_id")
    if not org_id:
        await ws.close(code=4003)
        return

    await manager.connect(ws, org_id, channel_id)
    try:
        while True:
            # نستقبل ping أو typing events — لكن الرسائل تُرسل عبر REST
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws, org_id, channel_id)
