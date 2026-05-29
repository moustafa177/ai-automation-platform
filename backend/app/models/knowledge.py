"""
🧠 نماذج قاعدة المعرفة — KnowledgeBase + Document
"""
import enum

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class DocStatus(str, enum.Enum):
    PENDING    = "pending"      # في الانتظار
    PROCESSING = "processing"   # جارٍ المعالجة
    READY      = "ready"        # جاهز
    FAILED     = "failed"       # فشل


class DocType(str, enum.Enum):
    PDF      = "pdf"
    DOCX     = "docx"
    TXT      = "txt"
    MD       = "md"
    URL      = "url"
    CSV      = "csv"
    XLSX     = "xlsx"
    PPTX     = "pptx"


class KnowledgeBase(BaseModel):
    """
    مجموعة مستندات خاصة بمنظمة واحدة
    تُخزَّن vectors في ChromaDB بـ collection_name فريد
    """
    __tablename__ = "knowledge_bases"

    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name:        Mapped[str]         = mapped_column(String(255), nullable=False)
    description: Mapped[str | None]  = mapped_column(Text)
    icon:        Mapped[str]         = mapped_column(String(10), default="📚")
    color:       Mapped[str]         = mapped_column(String(20), default="purple")

    # ChromaDB collection identifier
    collection_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Embedding model
    embedding_model: Mapped[str] = mapped_column(
        String(100), default="models/text-embedding-004"
    )

    # Stats
    total_documents: Mapped[int] = mapped_column(Integer, default=0)
    total_chunks:    Mapped[int] = mapped_column(Integer, default=0)
    total_queries:   Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relations
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="knowledge_base",
        cascade="all, delete-orphan", lazy="select",
    )


class Document(BaseModel):
    """مستند فردي داخل قاعدة معرفة"""
    __tablename__ = "knowledge_documents"

    knowledge_base_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    name:     Mapped[str]        = mapped_column(String(512), nullable=False)
    doc_type: Mapped[DocType]    = mapped_column(String(10),  default=DocType.TXT)
    status:   Mapped[DocStatus]  = mapped_column(String(20),  default=DocStatus.PENDING)

    # File info
    file_path:  Mapped[str | None] = mapped_column(Text)       # local / MinIO path
    source_url: Mapped[str | None] = mapped_column(Text)       # for URL type
    file_size:  Mapped[int]        = mapped_column(Integer, default=0)  # bytes

    # Processing result
    raw_text:      Mapped[str | None] = mapped_column(Text)
    chunk_count:   Mapped[int]        = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    # Metadata
    page_count: Mapped[int | None]    = mapped_column(Integer)
    word_count: Mapped[int | None]    = mapped_column(Integer)

    # Relations
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase", back_populates="documents"
    )
