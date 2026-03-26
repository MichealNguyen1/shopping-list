# config.py — Quản lý tất cả environment variables của app
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Pydantic BaseSettings tự động đọc từ file .env
# Ưu điểm: nếu biến bắt buộc mà thiếu → app crash ngay lúc khởi động,
# không phải đợi đến lúc dùng mới phát hiện lỗi.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Tên app — hiện trong Swagger UI (/docs)
    app_name: str = "Shopping List API"

    # MongoDB connection string
    # Format: mongodb+srv://user:pass@cluster.mongodb.net (Atlas)
    #      or mongodb://localhost:27017 (local)
    mongodb_uri: str

    # Tên database trong MongoDB
    # Một MongoDB server có thể chứa nhiều database
    mongodb_db: str = "shopping_list"

    # CORS origin — URL của frontend được phép gọi API
    # Ví dụ: https://my-app.vercel.app
    # Dùng "*" khi dev local cho tiện, production phải set cụ thể
    frontend_url: str = "*"

    class Config:
        # Pydantic sẽ đọc file .env ở thư mục chạy uvicorn
        env_file = ".env"


# Tạo 1 instance duy nhất, dùng chung toàn app (Singleton pattern)
# Import từ file khác: from app.core.config import settings
settings = Settings()
