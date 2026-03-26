# models.py — Định nghĩa cấu trúc dữ liệu lưu trong MongoDB
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Phân biệt models.py vs schemas.py:
# - models.py: shape của document trong DATABASE (có _id, created_at, ...)
# - schemas.py: shape của JSON trong REQUEST/RESPONSE (client gửi lên / nhận về)
# Tách ra để có thể thay đổi API contract mà không đụng đến DB structure và ngược lại.

from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(str):
    """Custom type để handle MongoDB ObjectId trong Pydantic.

    MongoDB dùng ObjectId (12-byte binary) làm primary key thay vì UUID hay integer.
    Vấn đề: ObjectId không phải string, Pydantic không biết cách serialize.
    Giải pháp: tạo custom type kế thừa str, override validation để convert tự động.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)


class ShoppingItem(BaseModel):
    """Document shape trong MongoDB collection 'items'.

    Field(...) = required field (không có default)
    Field(default=...) = optional field với giá trị mặc định
    """

    # _id trong MongoDB — dùng alias vì Python không cho biến tên "_id"
    # Field(alias="_id") nói với Pydantic: khi đọc từ DB, field "_id" map vào "id"
    id: PyObjectId | None = Field(default=None, alias="_id")

    name: str = Field(..., min_length=1, max_length=100)
    brand: str = Field(default="", max_length=100)  # Không bắt buộc
    quantity: int = Field(default=1, ge=1)           # ge=1: greater or equal 1
    price: float = Field(default=0.0, ge=0)          # ge=0: không âm
    is_purchased: bool = Field(default=False)

    # Tự động set thời gian tạo, không cần client gửi lên
    # timezone.utc đảm bảo luôn lưu UTC, tránh timezone bug
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        # Cho phép dùng alias ("_id") khi parse từ dict MongoDB
        populate_by_name = True
        # Cho phép Pydantic hiểu ObjectId (type không phải built-in Python)
        arbitrary_types_allowed = True
