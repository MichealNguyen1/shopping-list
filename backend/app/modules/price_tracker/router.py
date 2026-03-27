from __future__ import annotations
# router.py — HTTP endpoints cho price tracker

from fastapi import APIRouter, Depends, HTTPException, Header, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database
from app.modules.price_tracker import services
from app.modules.price_tracker.schemas import (
    TrackProductRequest,
    TrackedProductResponse,
    CheckResultResponse,
    PriceSnapshotResponse,
)

router = APIRouter(prefix="/price-tracker", tags=["price-tracker"])


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


@router.post(
    "/products",
    response_model=TrackedProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm sản phẩm Shopee cần theo dõi giá",
)
async def track_product(
    data: TrackProductRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        return await services.add_product(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Không thể fetch từ Shopee: {str(e)}",
        )


@router.get(
    "/products",
    response_model=list[TrackedProductResponse],
    summary="Danh sách sản phẩm đang theo dõi",
)
async def list_products(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await services.list_products(db)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ngừng theo dõi sản phẩm",
)
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    deleted = await services.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")


@router.get(
    "/products/{product_id}/history",
    response_model=list[PriceSnapshotResponse],
    summary="Lịch sử giá của 1 sản phẩm",
)
async def get_price_history(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await services.get_price_history(db, product_id)


@router.post(
    "/cron/check-prices",
    response_model=CheckResultResponse,
    summary="Trigger check giá (gọi bởi cron job)",
)
async def check_prices(
    db: AsyncIOMotorDatabase = Depends(get_db),
    # Bảo vệ endpoint bằng secret token — chỉ cron job biết token này
    # Header: Authorization: Bearer {CRON_SECRET}
    authorization: str = Header(default=""),
):
    """Endpoint này được cron-job.org gọi mỗi 1 giờ.

    Bảo vệ bằng CRON_SECRET để tránh bị gọi tùy tiện.
    """
    expected = f"Bearer {settings.cron_secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await services.check_all_prices(db)
