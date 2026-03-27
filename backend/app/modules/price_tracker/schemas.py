from __future__ import annotations
# schemas.py — Request/Response shapes cho Price Tracker API

from pydantic import BaseModel, Field, field_validator
import re


class TrackProductRequest(BaseModel):
    """POST /price-tracker/products — Thêm sản phẩm cần theo dõi."""

    shopee_url: str = Field(..., examples=["https://shopee.vn/San-pham-i.123456.789"])

    # Ngưỡng cảnh báo, mặc định 5%
    alert_threshold_pct: float = Field(default=5.0, ge=1.0, le=50.0)

    @field_validator("shopee_url")
    @classmethod
    def validate_shopee_url(cls, v: str) -> str:
        """Kiểm tra URL đúng format Shopee. Hỗ trợ 2 format:
        - https://shopee.vn/ten-san-pham-i.{shop_id}.{item_id}
        - https://shopee.vn/product/{shop_id}/{item_id}
        """
        pattern_slug = r"shopee\.vn/.+-i\.(\d+)\.(\d+)"
        pattern_product = r"shopee\.vn/product/(\d+)/(\d+)"
        if not re.search(pattern_slug, v) and not re.search(pattern_product, v):
            raise ValueError(
                "URL không hợp lệ. Cần format: "
                "https://shopee.vn/ten-sp-i.{shop_id}.{item_id} "
                "hoặc https://shopee.vn/product/{shop_id}/{item_id}"
            )
        return v


class PriceSnapshotResponse(BaseModel):
    price: float
    checked_at: str  # ISO string


class TrackedProductResponse(BaseModel):
    """Response trả về client."""
    id: str
    shopee_url: str
    shop_id: int
    item_id: int
    product_name: str
    shop_name: str
    is_official: bool
    current_price: float
    alert_threshold_pct: float
    last_checked: str
    created_at: str


class CheckResultResponse(BaseModel):
    """Response sau khi cron check giá."""
    checked: int        # Số sản phẩm đã check
    alerted: int        # Số sản phẩm có biến động giá → đã gửi thông báo
    errors: list[str]   # Sản phẩm bị lỗi khi fetch
