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
    frontend_url: str = "*"

    # Telegram Bot — lấy từ @BotFather
    # Để trống nếu chưa setup, app vẫn chạy bình thường
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Cron secret — bảo vệ endpoint /cron/check-prices
    # Tạo bằng: python -c "import secrets; print(secrets.token_hex(32))"
    cron_secret: str = "change-me-in-production"

    class Config:
        # Pydantic sẽ đọc file .env ở thư mục chạy uvicorn
        env_file = ".env"


# Tạo 1 instance duy nhất, dùng chung toàn app (Singleton pattern)
# Import từ file khác: from app.core.config import settings
settings = Settings()
