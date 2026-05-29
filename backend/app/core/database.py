"""
🗄️ إعداد قاعدة البيانات — SQLAlchemy Async
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ── إنشاء المحرك Async ───────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,   # طباعة SQL في بيئة التطوير
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,             # التحقق من الاتصال قبل الاستخدام
    pool_recycle=3600,              # تجديد الاتصالات كل ساعة
)

# ── مصنع الجلسات ─────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── الـ Base لجميع الـ Models ─────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency لحقن الجلسة في الـ endpoints ──────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — توفر جلسة قاعدة بيانات لكل request
    تُغلق الجلسة تلقائياً عند انتهاء الـ request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager للاستخدام خارج FastAPI (مثل Celery tasks)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
