"""🤖 Chatbot API Endpoints"""
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import DBSession, CurrentUserPayload
from app.models.chatbot import Chatbot, BotStatus
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate, ChatbotOut, ChatMessage, ChatResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/chatbots", tags=["Chatbot"])


# ── Helpers ────────────────────────────────────────────────
async def get_bot_or_404(bot_id: str, org_id: str, db: AsyncSession) -> Chatbot:
    result = await db.execute(
        select(Chatbot).where(Chatbot.id == bot_id, Chatbot.org_id == org_id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="الروبوت غير موجود")
    return bot


# ── LIST ───────────────────────────────────────────────────
@router.get("", response_model=dict)
async def list_chatbots(
    payload: CurrentUserPayload,
    db: DBSession,
):
    """قائمة روبوتات المنظمة"""
    result = await db.execute(
        select(Chatbot)
        .where(Chatbot.org_id == payload["org_id"], Chatbot.is_active == True)
        .order_by(Chatbot.created_at.desc())
    )
    bots = result.scalars().all()
    return {
        "success": True,
        "data": [
            {
                "id": b.id, "name": b.name, "description": b.description,
                "avatar_emoji": b.avatar_emoji, "platform": b.platform,
                "status": b.status, "model": b.model,
                "total_messages": b.total_messages,
                "total_sessions": b.total_sessions,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in bots
        ],
        "total": len(bots),
    }


# ── CREATE ─────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_chatbot(
    data: ChatbotCreate,
    payload: CurrentUserPayload,
    db: DBSession,
):
    """إنشاء روبوت جديد"""
    # Count existing bots (plan limit check — simplified)
    count_res = await db.execute(
        select(func.count()).where(
            Chatbot.org_id == payload["org_id"], Chatbot.is_active == True
        )
    )
    count = count_res.scalar_one()
    if count >= 10:
        raise HTTPException(status_code=400, detail="وصلت للحد الأقصى من الروبوتات في خطتك")

    bot = Chatbot(
        org_id        = payload["org_id"],
        name          = data.name,
        description   = data.description,
        avatar_emoji  = data.avatar_emoji,
        system_prompt = data.system_prompt,
        model         = data.model,
        temperature   = data.temperature,
        max_tokens    = data.max_tokens,
        language      = data.language,
        platform      = data.platform,
        widget_config = data.widget_config,
        status        = BotStatus.DRAFT,
        api_key       = uuid.uuid4().hex,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)

    logger.info("chatbot_created", bot_id=bot.id, org=payload["org_id"])
    return {"success": True, "data": {"id": bot.id, "name": bot.name, "api_key": bot.api_key}}


# ── GET ONE ────────────────────────────────────────────────
@router.get("/{bot_id}", response_model=dict)
async def get_chatbot(bot_id: str, payload: CurrentUserPayload, db: DBSession):
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)
    return {"success": True, "data": {
        "id": bot.id, "name": bot.name, "description": bot.description,
        "avatar_emoji": bot.avatar_emoji, "system_prompt": bot.system_prompt,
        "model": bot.model, "temperature": bot.temperature,
        "max_tokens": bot.max_tokens, "language": bot.language,
        "platform": bot.platform, "status": bot.status,
        "widget_config": bot.widget_config,
        "total_messages": bot.total_messages, "total_sessions": bot.total_sessions,
        "webhook_url": bot.webhook_url, "api_key": bot.api_key,
        "created_at": bot.created_at.isoformat() if bot.created_at else None,
    }}


# ── UPDATE ─────────────────────────────────────────────────
@router.put("/{bot_id}", response_model=dict)
async def update_chatbot(
    bot_id: str, data: ChatbotUpdate,
    payload: CurrentUserPayload, db: DBSession,
):
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(bot, field, value)
    await db.commit()
    await db.refresh(bot)
    return {"success": True, "data": {"id": bot.id, "name": bot.name, "status": bot.status}}


# ── DELETE (soft) ──────────────────────────────────────────
@router.delete("/{bot_id}", response_model=dict)
async def delete_chatbot(bot_id: str, payload: CurrentUserPayload, db: DBSession):
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)
    bot.is_active = False
    await db.commit()
    return {"success": True, "message": "تم حذف الروبوت"}


# ── CHAT (Gemini / Claude API) ─────────────────────────────
@router.post("/{bot_id}/chat", response_model=dict)
async def chat_with_bot(
    bot_id: str, msg: ChatMessage,
    payload: CurrentUserPayload, db: DBSession,
):
    """إرسال رسالة للروبوت والحصول على رد من Gemini أو Claude"""
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)

    if bot.status == BotStatus.INACTIVE:
        raise HTTPException(status_code=400, detail="الروبوت غير نشط")

    session_id    = msg.session_id or uuid.uuid4().hex
    gemini_key    = settings.GEMINI_API_KEY
    anthropic_key = settings.ANTHROPIC_API_KEY
    gemini_model  = settings.GEMINI_DEFAULT_MODEL

    reply = ""
    input_tok = output_tok = 0

    # ── 1. Try Gemini ──────────────────────────────────────
    if gemini_key:
        try:
            from google import genai as gai
            from google.genai import types as gtypes
            gclient = gai.Client(api_key=gemini_key)

            # Use bot's model if it's a gemini model, else use default
            model_to_use = bot.model if bot.model.startswith("models/gemini") else gemini_model

            response = gclient.models.generate_content(
                model=model_to_use,
                contents=msg.message,
                config=gtypes.GenerateContentConfig(
                    system_instruction=bot.system_prompt,
                    max_output_tokens=bot.max_tokens,
                    temperature=bot.temperature,
                ),
            )
            reply      = response.text
            input_tok  = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
            output_tok = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
            logger.info("gemini_response", bot_id=bot.id, tokens=output_tok)

        except Exception as e:
            logger.error("gemini_error", error=str(e))
            # Fall through to Claude or mock

    # ── 2. Try Claude if Gemini unavailable ────────────────
    if not reply and anthropic_key:
        try:
            import anthropic
            aclient = anthropic.Anthropic(api_key=anthropic_key)
            response = aclient.messages.create(
                model=bot.model,
                max_tokens=bot.max_tokens,
                system=bot.system_prompt,
                messages=[{"role": "user", "content": msg.message}],
            )
            reply      = response.content[0].text
            input_tok  = response.usage.input_tokens
            output_tok = response.usage.output_tokens
        except Exception as e:
            logger.error("claude_error", error=str(e))

    # ── 3. Mock fallback ───────────────────────────────────
    if not reply:
        reply = (
            f"مرحباً! أنا {bot.name}. "
            f"تلقيت رسالتك. "
            "يبدو أن خدمة الذكاء الاصطناعي غير متاحة حالياً، يرجى المحاولة لاحقاً."
        )
        input_tok, output_tok = 0, 0

    # Update stats
    bot.total_messages += 1
    await db.commit()

    return {
        "success": True,
        "data": {
            "reply": reply,
            "session_id": session_id,
            "input_tokens": input_tok,
            "output_tokens": output_tok,
        }
    }


# ── ACTIVATE / DEACTIVATE ──────────────────────────────────
@router.post("/{bot_id}/activate", response_model=dict)
async def activate_bot(bot_id: str, payload: CurrentUserPayload, db: DBSession):
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)
    bot.status = BotStatus.ACTIVE
    await db.commit()
    return {"success": True, "data": {"status": bot.status}}


@router.post("/{bot_id}/deactivate", response_model=dict)
async def deactivate_bot(bot_id: str, payload: CurrentUserPayload, db: DBSession):
    bot = await get_bot_or_404(bot_id, payload["org_id"], db)
    bot.status = BotStatus.INACTIVE
    await db.commit()
    return {"success": True, "data": {"status": bot.status}}
