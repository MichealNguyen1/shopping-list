# schemas.py — Định nghĩa JSON shape cho API request và response
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Tại sao tách schemas khỏi models?
# Ví dụ thực tế: client không được tự set "created_at" hay "_id" khi tạo item mới.
# Nếu dùng chung 1 class, phải mark các field đó là Optional rồi validate thủ công.
# Tách ra thì mỗi class có đúng 1 trách nhiệm, dễ đọc hơn nhiều.

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema cho POST /items — tạo item mới.

    Chỉ gồm những field CLIENT được phép gửi lên.
    id, created_at không có ở đây vì server tự tạo.
    """
    name: str = Field(..., min_length=1, max_length=200, examples=["bình sữa Dr Brown"])
    category: str = Field(default="Khác", max_length=100, examples=["1. Đồ cho bé ăn"])
    brand: str = Field(default="", max_length=100, examples=["Dr Brown"])
    quantity: int = Field(default=1, ge=1, examples=[1])
    price: float = Field(default=0.0, ge=0, examples=[0])
    shopee_url: str = Field(default="", examples=["https://s.shopee.vn/xxx"])
    note: str = Field(default="", max_length=500, examples=[""])


class ItemUpdate(BaseModel):
    """Schema cho PATCH /items/{id} — cập nhật item.

    Tất cả field đều Optional vì PATCH chỉ update field được gửi lên.
    Khác với PUT (replace toàn bộ document), PATCH chỉ thay đổi field có trong request.
    """
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    brand: str | None = Field(default=None, max_length=100)
    quantity: int | None = Field(default=None, ge=1)
    price: float | None = Field(default=None, ge=0)
    is_purchased: bool | None = Field(default=None)
    shopee_url: str | None = Field(default=None)
    note: str | None = Field(default=None, max_length=500)


class ItemResponse(BaseModel):
    """Schema cho response trả về client — shape của JSON client nhận được."""

    # id là string (đã convert từ ObjectId), không phải "_id"
    id: str
    name: str
    category: str
    brand: str
    quantity: int
    price: float
    is_purchased: bool
    shopee_url: str
    note: str
    created_at: str


class ItemListResponse(BaseModel):
    """Schema cho GET /items — trả về danh sách + metadata."""

    items: list[ItemResponse]
    total: int  # Tổng số items — hữu ích cho pagination sau này
