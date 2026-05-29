"""
📐 Schemas المشتركة — Pagination، Responses
"""
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class APIResponse(BaseModel, Generic[T]):
    """الاستجابة الموحدة لجميع الـ endpoints"""
    success: bool = True
    data: T | None = None
    message: str | None = None
    meta: PaginationMeta | None = None


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class APIError(BaseModel):
    success: bool = False
    error: dict[str, Any]


class MessageResponse(BaseModel):
    message: str
    success: bool = True
