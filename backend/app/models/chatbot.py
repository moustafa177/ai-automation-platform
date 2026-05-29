"""🤖 نماذج الـ Chatbot"""
import enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization


class BotPlatform(str, enum.Enum):
    WEBSITE   = "website"
    WHATSAPP  = "whatsapp"
    TELEGRAM  = "telegram"
    MESSENGER = "messenger"
    API       = "api"


class BotStatus(str, enum.Enum):
    ACTIVE   = "active"
    INACTIVE = "inactive"
    DRAFT    = "draft"


class Chatbot(BaseModel):
    __tablename__ = "chatbots"

    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str]        = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_emoji: Mapped[str] = mapped_column(String(10), default="🤖", nullable=False)

    # AI Config
    system_prompt: Mapped[str] = mapped_column(
        Text,
        default="أنت مساعد ذكي ومفيد. أجب بشكل واضح ومختصر.",
        nullable=False
    )
    model: Mapped[str]       = mapped_column(String(50), default="claude-3-5-sonnet-20241022", nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.7, nullable=False)
    max_tokens: Mapped[int]  = mapped_column(Integer, default=1024, nullable=False)
    language: Mapped[str]    = mapped_column(String(10), default="ar", nullable=False)

    # Platform
    platform: Mapped[BotPlatform] = mapped_column(
        Enum(BotPlatform), default=BotPlatform.WEBSITE, nullable=False
    )
    status: Mapped[BotStatus] = mapped_column(
        Enum(BotStatus), default=BotStatus.DRAFT, nullable=False
    )

    # Widget settings (JSON)
    widget_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Stats (denormalized for speed)
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Webhook / Integration
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_key: Mapped[str | None]     = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool]         = mapped_column(Boolean, default=True, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")
