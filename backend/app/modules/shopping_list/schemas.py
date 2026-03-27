# schemas.py — Định nghĩa JSON shape cho API request và response
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Tại sao tách schemas khỏi models?
# Ví dụ thực tế: client không được tự set "created_at" hay "_id" khi tạo item mới.
# Nếu dùng chung 1 class, phải mark các field đó là Optional rồi validate thủ công.
# Tách ra thì mỗi class có đúng 1 trách nhiệm, dễ đọc hơn nhiều.

from typing import Literal
from pydantic import BaseModel, Field

# 4 trạng thái của mỗi item trong quá trình ra quyết định
# considering → đang xem xét, chưa quyết định
# will_buy    → đã quyết định sẽ mua
# purchased   → đã mua rồi
# skipped     → quyết định không mua (có thể kèm lý do)
ItemStatus = Literal["considering", "will_buy", "purchased", "skipped"]


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["bình sữa Dr Brown"])
    category: str = Field(default="Khác", max_length=100, examples=["1. Đồ cho bé ăn"])
    shopee_url: str = Field(default="", examples=["https://s.shopee.vn/xxx"])
    note: str = Field(default="", max_length=500)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    shopee_url: str | None = Field(default=None)
    note: str | None = Field(default=None, max_length=500)
    # Trạng thái mới sau khi user ra quyết định
    status: ItemStatus | None = Field(default=None)
    # Lý do không mua — chỉ dùng khi status = "skipped"
    skip_reason: str | None = Field(default=None, max_length=500)


class ItemResponse(BaseModel):
    id: str
    name: str
    category: str
    shopee_url: str
    note: str
    status: ItemStatus
    skip_reason: str
    created_at: str


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
