from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# from app.schemas.response import PaginationInfo


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, pattern=r"^\d{10}|\d{13}$")
    year: int = Field(..., ge=1000, le=2100)
    description: Optional[str] = Field(None, max_length=2000)
    is_available: bool = Field(default=True)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, pattern=r"^\d{10}|\d{13}$")
    year: Optional[int] = Field(None, ge=1000, le=2100)
    description: Optional[str] = Field(None, max_length=2000)
    is_available: Optional[bool] = None


class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BookSuccessResponse(BaseModel):
    success: bool = True
    data: BookResponse
    message: str
    timestamp: datetime


# class BooksPaginatedResponse(BaseModel):
# success: bool = True
# data: List[BookResponse]
# pagination: PaginationInfo
# timestamp: datetime
