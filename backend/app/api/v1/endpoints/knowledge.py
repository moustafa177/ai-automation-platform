"""🧠 Knowledge Base API — CRUD + Document Upload + RAG Query"""
import uuid
import re

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import DBSession, CurrentUserPayload
from app.models.knowledge import KnowledgeBase, Document, DocStatus, DocType
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseOut,
    DocumentOut, QueryRequest, QueryResult,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

ALLOWED_EXTENSIONS = {"pdf","docx","txt","md","csv","xlsx","pptx"}
MAX_FILE_MB = 20


# ── Helpers ────────────────────────────────────────────────
def make_collection_name(org_id: str, kb_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]", "_", org_id[:8])
    return f"kb_{safe}_{kb_id.replace('-','')[:12]}"

async def get_kb_or_404(kb_id: str, org_id: str, db: AsyncSession) -> KnowledgeBase:
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.org_id == org_id,
            KnowledgeBase.is_active == True,
        )
    )
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(404, "قاعدة المعرفة غير موجودة")
    return kb


# ══════════════════════════════════════════════════════════
# KNOWLEDGE BASES
# ══════════════════════════════════════════════════════════

@router.get("", response_model=dict)
async def list_knowledge_bases(payload: CurrentUserPayload, db: DBSession):
    """قائمة قواعد المعرفة للمنظمة"""
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.org_id == payload["org_id"], KnowledgeBase.is_active == True)
        .order_by(KnowledgeBase.created_at.desc())
    )
    kbs = result.scalars().all()
    return {
        "success": True,
        "data": [KnowledgeBaseOut.model_validate(kb).model_dump() for kb in kbs],
        "total": len(kbs),
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_knowledge_base(
    data: KnowledgeBaseCreate,
    payload: CurrentUserPayload,
    db: DBSession,
):
    """إنشاء قاعدة معرفة جديدة"""
    kb_id = str(uuid.uuid4())
    collection = make_collection_name(payload["org_id"], kb_id)

    kb = KnowledgeBase(
        id=kb_id,
        org_id=payload["org_id"],
        name=data.name,
        description=data.description,
        icon=data.icon,
        color=data.color,
        collection_name=collection,
        embedding_model=data.embedding_model,
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)

    logger.info("knowledge_base_created", kb_id=kb.id, org=payload["org_id"])
    return {"success": True, "data": KnowledgeBaseOut.model_validate(kb).model_dump()}


@router.get("/{kb_id}", response_model=dict)
async def get_knowledge_base(kb_id: str, payload: CurrentUserPayload, db: DBSession):
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)
    # Load documents
    doc_result = await db.execute(
        select(Document).where(Document.knowledge_base_id == kb_id)
        .order_by(Document.created_at.desc())
    )
    docs = doc_result.scalars().all()
    data = KnowledgeBaseOut.model_validate(kb).model_dump()
    data["documents"] = [DocumentOut.model_validate(d).model_dump() for d in docs]
    return {"success": True, "data": data}


@router.put("/{kb_id}", response_model=dict)
async def update_knowledge_base(
    kb_id: str, data: KnowledgeBaseUpdate,
    payload: CurrentUserPayload, db: DBSession,
):
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(kb, field, value)
    await db.commit()
    await db.refresh(kb)
    return {"success": True, "data": KnowledgeBaseOut.model_validate(kb).model_dump()}


@router.delete("/{kb_id}", response_model=dict)
async def delete_knowledge_base(kb_id: str, payload: CurrentUserPayload, db: DBSession):
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)
    kb.is_active = False
    await db.commit()
    return {"success": True, "message": "تم حذف قاعدة المعرفة"}


# ══════════════════════════════════════════════════════════
# DOCUMENTS
# ══════════════════════════════════════════════════════════

@router.post("/{kb_id}/documents/upload", response_model=dict)
async def upload_document(
    kb_id: str,
    payload: CurrentUserPayload,
    db: DBSession,
    file: UploadFile = File(...),
):
    """رفع مستند وإضافته لقاعدة المعرفة"""
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)

    # Validate extension
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"نوع الملف غير مدعوم. المدعوم: {', '.join(ALLOWED_EXTENSIONS)}")

    # Read content (up to MAX_FILE_MB)
    content = await file.read(MAX_FILE_MB * 1024 * 1024 + 1)
    if len(content) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(413, f"حجم الملف يتجاوز {MAX_FILE_MB} ميغابايت")

    # Create document record
    doc = Document(
        knowledge_base_id=kb_id,
        org_id=payload["org_id"],
        name=file.filename or "مستند",
        doc_type=DocType(ext) if ext in DocType._value2member_map_ else DocType.TXT,
        status=DocStatus.PROCESSING,
        file_size=len(content),
    )
    db.add(doc)
    kb.total_documents += 1
    await db.commit()
    await db.refresh(doc)

    # Process in background (simplified: extract text + embed)
    try:
        text = _extract_text(content, ext)
        chunks = _chunk_text(text)
        await _store_in_chroma(kb.collection_name, doc.id, chunks)

        doc.raw_text   = text[:10000]  # keep first 10k chars
        doc.chunk_count = len(chunks)
        doc.word_count  = len(text.split())
        doc.status      = DocStatus.READY
        kb.total_chunks += len(chunks)
        await db.commit()
        await db.refresh(doc)

        logger.info("document_processed", doc_id=doc.id, chunks=len(chunks))
    except Exception as e:
        doc.status = DocStatus.FAILED
        doc.error_message = str(e)[:500]
        await db.commit()
        logger.error("document_failed", doc_id=doc.id, error=str(e))

    return {"success": True, "data": DocumentOut.model_validate(doc).model_dump()}


@router.post("/{kb_id}/documents/url", response_model=dict)
async def add_url_document(
    kb_id: str,
    payload: CurrentUserPayload,
    db: DBSession,
    url: str = Form(...),
    name: str = Form(default=""),
):
    """إضافة مستند من URL"""
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)

    doc = Document(
        knowledge_base_id=kb_id,
        org_id=payload["org_id"],
        name=name or url[:100],
        doc_type=DocType.URL,
        status=DocStatus.PROCESSING,
        source_url=url,
    )
    db.add(doc)
    kb.total_documents += 1
    await db.commit()
    await db.refresh(doc)

    # Fetch URL content
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read(2 * 1024 * 1024).decode("utf-8", errors="ignore")
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s{2,}", " ", text).strip()[:50000]
        chunks = _chunk_text(text)
        await _store_in_chroma(kb.collection_name, doc.id, chunks)

        doc.raw_text    = text[:10000]
        doc.chunk_count = len(chunks)
        doc.word_count  = len(text.split())
        doc.status      = DocStatus.READY
        kb.total_chunks += len(chunks)
        await db.commit()
        await db.refresh(doc)
    except Exception as e:
        doc.status = DocStatus.FAILED
        doc.error_message = str(e)[:500]
        await db.commit()

    return {"success": True, "data": DocumentOut.model_validate(doc).model_dump()}


@router.delete("/{kb_id}/documents/{doc_id}", response_model=dict)
async def delete_document(
    kb_id: str, doc_id: str,
    payload: CurrentUserPayload, db: DBSession,
):
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.knowledge_base_id == kb_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "المستند غير موجود")

    kb.total_documents = max(0, kb.total_documents - 1)
    kb.total_chunks    = max(0, kb.total_chunks - doc.chunk_count)
    await db.delete(doc)
    await db.commit()
    return {"success": True, "message": "تم حذف المستند"}


# ══════════════════════════════════════════════════════════
# RAG QUERY
# ══════════════════════════════════════════════════════════

@router.post("/{kb_id}/query", response_model=dict)
async def query_knowledge_base(
    kb_id: str,
    req: QueryRequest,
    payload: CurrentUserPayload,
    db: DBSession,
):
    """استعلام RAG — يبحث في المستندات ويُجيب بالذكاء الاصطناعي"""
    kb = await get_kb_or_404(kb_id, payload["org_id"], db)
    kb.total_queries += 1

    # 1. Retrieve relevant chunks from ChromaDB
    sources = []
    context = ""
    try:
        sources, context = await _retrieve_chunks(
            kb.collection_name, req.query, req.top_k
        )
    except Exception as e:
        logger.warning("chroma_retrieve_failed", error=str(e))
        # Fallback: search raw_text of ready docs
        doc_result = await db.execute(
            select(Document).where(
                Document.knowledge_base_id == kb_id,
                Document.status == DocStatus.READY,
            ).limit(5)
        )
        docs = doc_result.scalars().all()
        context = "\n\n".join(
            f"[{d.name}]: {d.raw_text[:500]}" for d in docs if d.raw_text
        )

    # 2. Generate answer with Gemini
    answer = ""
    tokens = 0
    if req.use_ai and settings.GEMINI_API_KEY:
        try:
            from google import genai as gai
            from google.genai import types as gtypes

            system = (
                "أنت مساعد ذكي متخصص في الإجابة على الأسئلة بناءً على المستندات المُقدَّمة. "
                "أجب بالعربية فقط بناءً على السياق التالي. إذا لم تجد إجابة، قل ذلك بوضوح.\n\n"
                f"السياق:\n{context[:4000]}"
            )
            gclient = gai.Client(api_key=settings.GEMINI_API_KEY)
            resp = gclient.models.generate_content(
                model=settings.GEMINI_DEFAULT_MODEL,
                contents=req.query,
                config=gtypes.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=800,
                    temperature=0.3,
                ),
            )
            answer = resp.text
            tokens = (resp.usage_metadata.candidates_token_count
                      if resp.usage_metadata else 0)
        except Exception as e:
            logger.error("rag_gemini_error", error=str(e))
            answer = f"وُجدت {len(sources)} نتيجة ذات صلة. يرجى المراجعة اليدوية."

    if not answer:
        answer = (context[:600] + "...") if context else "لم يُعثر على معلومات ذات صلة في قاعدة المعرفة."

    await db.commit()
    return {
        "success": True,
        "data": {"answer": answer, "sources": sources, "tokens": tokens},
    }


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════

def _extract_text(content: bytes, ext: str) -> str:
    """استخراج النص من الملف"""
    if ext in ("txt", "md", "csv"):
        return content.decode("utf-8", errors="ignore")

    if ext == "pdf":
        try:
            import io
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content))
                return "\n".join(p.extract_text() or "" for p in reader.pages)
            except ImportError:
                pass
            # Try pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    return "\n".join(p.extract_text() or "" for p in pdf.pages)
            except ImportError:
                pass
        except Exception:
            pass
        return content.decode("utf-8", errors="ignore")

    if ext == "docx":
        try:
            import io
            from docx import Document as DocxDoc
            doc = DocxDoc(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            pass

    # Fallback
    return content.decode("utf-8", errors="ignore")


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """تقطيع النص إلى chunks"""
    text = text.strip()
    if not text:
        return []
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks[:200]  # max 200 chunks per doc


async def _store_in_chroma(collection_name: str, doc_id: str, chunks: list[str]):
    """تخزين الـ chunks في ChromaDB"""
    if not chunks:
        return
    try:
        import chromadb
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, port=settings.CHROMA_PORT
        )
        collection = client.get_or_create_collection(collection_name)
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=[{"doc_id": doc_id, "chunk": i} for i in range(len(chunks))],
        )
    except Exception as e:
        logger.warning("chroma_store_failed", error=str(e))
        # ChromaDB unavailable — skip silently in dev


async def _retrieve_chunks(
    collection_name: str, query: str, top_k: int
) -> tuple[list[dict], str]:
    """استرجاع الـ chunks الأقرب من ChromaDB"""
    try:
        import chromadb
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, port=settings.CHROMA_PORT
        )
        collection = client.get_or_create_collection(collection_name)
        results = collection.query(query_texts=[query], n_results=top_k)
        docs    = results.get("documents", [[]])[0]
        metas   = results.get("metadatas", [[]])[0]
        sources = [{"text": d, "doc_id": m.get("doc_id", ""), "chunk": m.get("chunk", 0)}
                   for d, m in zip(docs, metas)]
        context = "\n\n".join(docs)
        return sources, context
    except Exception:
        raise
