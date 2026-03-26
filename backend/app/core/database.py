# database.py — Quản lý kết nối MongoDB
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Tại sao dùng Motor thay vì PyMongo?
# PyMongo là synchronous — mỗi query DB sẽ BLOCK thread cho đến khi có kết quả.
# Motor là async — trong lúc chờ DB trả về, Python có thể xử lý request khác.
# FastAPI là async framework, nên phải dùng Motor để tận dụng tối đa.

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


# Biến module-level lưu MongoDB client
# Dùng global như này vì client được tạo 1 lần lúc startup, tái sử dụng mãi
# (tạo client mới cho mỗi request rất tốn tài nguyên)
_client: AsyncIOMotorClient | None = None


def connect_db() -> None:
    """Tạo kết nối MongoDB. Gọi 1 lần lúc app khởi động."""
    global _client
    # AsyncIOMotorClient tự quản lý connection pool
    # Connection pool = tập hợp các kết nối sẵn sàng, không cần tạo mới mỗi lần query
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"✅ Connected to MongoDB: {settings.mongodb_db}")


def disconnect_db() -> None:
    """Đóng kết nối MongoDB. Gọi lúc app tắt."""
    global _client
    if _client:
        _client.close()
        print("🔌 Disconnected from MongoDB")


def get_database() -> AsyncIOMotorDatabase:
    """Trả về database instance để dùng trong các service.

    Tại sao return database chứ không return client?
    Vì 99% thời gian chúng ta chỉ làm việc với 1 database cụ thể.
    Client cần thiết khi muốn switch database (hiếm khi cần).
    """
    if _client is None:
        raise RuntimeError("Database chưa được kết nối. Gọi connect_db() trước.")
    return _client[settings.mongodb_db]
