"""
🗺️ الـ Router الرئيسي — يجمع جميع الـ endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, chatbot, knowledge, network, team, settings, internal_chat, reports, billing
)

api_router = APIRouter()

# ── Auth ──────────────────────────────────────────────────
api_router.include_router(auth.router)

# ── Chatbot ───────────────────────────────────────────────
api_router.include_router(chatbot.router)

# ── Knowledge Base ────────────────────────────────────────
api_router.include_router(knowledge.router)

# ── Network Intelligence ──────────────────────────────────
api_router.include_router(network.router)

# ── Team Management ───────────────────────────────────────
api_router.include_router(team.router)

# ── Settings ──────────────────────────────────────────────
api_router.include_router(settings.router)

# ── Internal Chat ─────────────────────────────────────────
api_router.include_router(internal_chat.router)

# ── Reports ───────────────────────────────────────────────
api_router.include_router(reports.router)

# ── Billing & Subscriptions ────────────────────────────────
api_router.include_router(billing.router)
