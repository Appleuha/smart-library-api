from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class ErrorCodes(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: ErrorCodes
    details: Optional[dict] = None


class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class BookListResponse(BaseModel):
    success: bool = True
    data: List[Any]
    pagination: PaginationInfo
    timestamp: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()  # ← Сериализует datetime в ISO строку
        }
    )
