"""📋 Pydantic Schemas — Chatbot"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.models.chatbot import BotPlatform, BotStatus


# ── Request Schemas ────────────────────────────────────────
class ChatbotCreate(BaseModel):
    name: str                    = Field(..., min_length=2, max_length=100)
    description: str | None      = None
    avatar_emoji: str            = "🤖"
    system_prompt: str           = "أنت مساعد ذكي ومفيد. أجب بشكل واضح ومختصر."
    model: str                   = "claude-3-5-sonnet-20241022"
    temperature: float           = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int              = Field(1024, ge=100, le=8192)
    language: str                = "ar"
    platform: BotPlatform        = BotPlatform.WEBSITE
    widget_config: dict[str,Any] = {}


class ChatbotUpdate(BaseModel):
    name: str | None             = None
    description: str | None      = None
    avatar_emoji: str | None     = None
    system_prompt: str | None    = None
    model: str | None            = None
    temperature: float | None    = None
    max_tokens: int | None       = None
    language: str | None         = None
    platform: BotPlatform | None = None
    status: BotStatus | None     = None
    widget_config: dict | None   = None
    webhook_url: str | None      = None


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None


# ── Response Schemas ───────────────────────────────────────
class ChatbotOut(BaseModel):
    id: str
    name: str
    description: str | None
    avatar_emoji: str
    system_prompt: str
    model: str
    temperature: float
    max_tokens: int
    language: str
    platform: BotPlatform
    status: BotStatus
    widget_config: dict
    total_messages: int
    total_sessions: int
    webhook_url: str | None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    input_tokens: int
    output_tokens: int
