"""
🧠 Schemas لقاعدة المعرفة
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── KnowledgeBase ─────────────────────────────────────────

class KnowledgeBaseCreate(BaseModel):
    name:             str = Field(..., min_length=2, max_length=255)
    description:      str | None = None
    icon:             str = "📚"
    color:            str = "purple"
    embedding_model:  str = "models/text-embedding-004"


class KnowledgeBaseUpdate(BaseModel):
    name:        str | None = None
    description: str | None = None
    icon:        str | None = None
    color:       str | None = None


class KnowledgeBaseOut(BaseModel):
    id:               str
    name:             str
    description:      str | None
    icon:             str
    color:            str
    collection_name:  str
    embedding_model:  str
    total_documents:  int
    total_chunks:     int
    total_queries:    int
    is_active:        bool
    created_at:       datetime | None

    model_config = {"from_attributes": True}


# ── Document ──────────────────────────────────────────────

class DocumentOut(BaseModel):
    id:                str
    name:              str
    doc_type:          str
    status:            str
    file_size:         int
    chunk_count:       int
    page_count:        int | None
    word_count:        int | None
    error_message:     str | None
    created_at:        datetime | None

    model_config = {"from_attributes": True}


# ── Query ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query:   str = Field(..., min_length=1, max_length=2000)
    top_k:   int = Field(default=5, ge=1, le=20)
    use_ai:  bool = True   # هل نُجيب بالذكاء الاصطناعي؟


class QueryResult(BaseModel):
    answer:   str
    sources:  list[dict[str, Any]] = []
    tokens:   int = 0
