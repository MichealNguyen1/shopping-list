from __future__ import annotations
# models.py — DB document shapes cho price tracker

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TrackedProduct(BaseModel):
    """Sản phẩm đang được theo dõi giá.

    Lưu trong collection 'tracked_products'.
    """

    # URL gốc user nhập vào: https://shopee.vn/xxx-i.123456.789
    shopee_url: str

    # Tách ra từ URL để gọi Shopee API
    # URL format: https://shopee.vn/{slug}-i.{shop_id}.{item_id}
    shop_id: int
    item_id: int

    # Thông tin sản phẩm — fetch từ Shopee lần đầu track
    product_name: str = ""
    shop_name: str = ""

    # True = Shopee Mall hoặc Official Shop
    is_official: bool = False

    # Giá hiện tại (đơn vị: VNĐ)
    current_price: float = 0.0

    # Ngưỡng cảnh báo: mặc định 5% — thông báo khi giá thay đổi >= 5%
    alert_threshold_pct: float = 5.0

    last_checked: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PriceSnapshot(BaseModel):
    """Lưu lịch sử giá theo thời gian.

    Lưu trong collection 'price_snapshots'.
    Mỗi lần cron check giá → insert 1 document vào đây.
    """

    # Trỏ về TrackedProduct._id (dạng string)
    product_id: str

    price: float
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
