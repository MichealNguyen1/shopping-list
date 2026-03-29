# main.py — Entry point của FastAPI app
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# File này làm 3 việc:
# 1. Tạo FastAPI app instance
# 2. Cấu hình CORS (cho phép frontend gọi API)
# 3. Đăng ký router và quản lý lifecycle (startup/shutdown)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.modules.shopping_list.router import router as shopping_router
from app.modules.price_tracker.router import router as price_tracker_router
from app.modules.pregnancy_calendar.router import router as pregnancy_calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý lifecycle của app: chạy code khi start và khi stop.

    Tại sao dùng lifespan thay vì @app.on_event("startup")?
    lifespan là cách mới hơn (FastAPI 0.95+), dùng context manager rõ ràng hơn.
    Code trước `yield` chạy khi startup, code sau `yield` chạy khi shutdown.
    """
    # STARTUP: kết nối DB trước khi nhận request
    connect_db()
    yield
    # SHUTDOWN: đóng kết nối DB sau khi server dừng
    disconnect_db()


app = FastAPI(
    title=settings.app_name,
    description="API quản lý danh sách mua sắm",
    version="1.0.0",
    # lifespan hook để manage DB connection
    lifespan=lifespan,
)

# CORS — Cross-Origin Resource Sharing
# Vấn đề: browser chặn request từ domain A (frontend) đến domain B (backend) theo mặc định.
# Giải pháp: backend phải khai báo domain nào được phép gọi API.
#
# Ví dụ:
# Frontend chạy ở: https://my-app.vercel.app
# Backend chạy ở:  https://my-api.render.com
# → Browser sẽ chặn request nếu không có CORS header
app.add_middleware(
    CORSMiddleware,
    # allow_origins: danh sách domain được phép gọi API
    # ["*"] = cho phép tất cả (chỉ dùng khi dev, production phải set cụ thể)
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers=["*"],   # Content-Type, Authorization, ...
)

# Đăng ký router với prefix /api
# Tất cả endpoint trong shopping_router sẽ có path: /api/items/...
app.include_router(shopping_router, prefix="/api")
app.include_router(price_tracker_router, prefix="/api")
app.include_router(pregnancy_calendar_router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint — dùng để verify server đang chạy."""
    return {"status": "ok", "app": settings.app_name}
