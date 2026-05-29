"""💬 Internal Chat Models — قنوات الشات الداخلي"""
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization


class ChannelType(str, enum.Enum):
    GENERAL    = "general"
    DEPARTMENT = "department"
    DIRECT     = "direct"


class ChatChannel(BaseModel):
    __tablename__ = "chat_channels"

    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str]  = mapped_column(String(100), nullable=False)
    icon: Mapped[str]  = mapped_column(String(10), default="💬", nullable=False)
    type: Mapped[ChannelType] = mapped_column(
        Enum(ChannelType), default=ChannelType.GENERAL, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="channel", cascade="all, delete-orphan"
    )


class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    channel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat_channels.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    user_id:     Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_name:   Mapped[str] = mapped_column(String(255), nullable=False)
    user_avatar: Mapped[str] = mapped_column(String(10), default="👤", nullable=False)
    content:     Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default="text", nullable=False)

    channel: Mapped["ChatChannel"] = relationship("ChatChannel", back_populates="messages")
