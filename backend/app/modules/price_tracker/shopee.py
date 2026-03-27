from __future__ import annotations
# shopee.py — Shopee unofficial API client
#
# Shopee không có public API — chúng ta dùng internal API mà app Shopee gọi.
# Rủi ro: Shopee có thể thay đổi API bất cứ lúc nào hoặc block request.
# Cách giảm rủi ro: thêm headers giả browser, rate limiting, retry logic.

import re
import httpx
from dataclasses import dataclass


# Endpoint thật Shopee dùng cho product detail page
# Tìm được bằng cách inspect Network tab khi browse sản phẩm
_SHOPEE_API = "https://shopee.vn/api/v4/pdp/get_pc"

# Headers tối thiểu cần thiết
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://shopee.vn/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi,en;q=0.9",
    "x-api-source": "pc",
    "x-shopee-language": "vi",
    "x-requested-with": "XMLHttpRequest",
}

# Timeout: 10s — Vercel function timeout là 60s, để buffer cho xử lý
_TIMEOUT_SECONDS = 10


@dataclass
class ShopeeProduct:
    """Data class chứa thông tin sản phẩm fetch từ Shopee."""
    item_id: int
    shop_id: int
    name: str
    price: float        # Giá hiện tại (VNĐ)
    original_price: float  # Giá gốc trước giảm (nếu có)
    shop_name: str
    is_official: bool   # True nếu là Shopee Mall hoặc Official Store


def parse_shopee_url(url: str) -> tuple[int, int]:
    """Tách shop_id và item_id từ Shopee URL. Hỗ trợ 2 format:

    Format 1: https://shopee.vn/{slug}-i.{shop_id}.{item_id}
    Format 2: https://shopee.vn/product/{shop_id}/{item_id}?...
    """
    # Format 1: slug-i.shop_id.item_id
    match = re.search(r"-i\.(\d+)\.(\d+)", url)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Format 2: /product/shop_id/item_id
    match = re.search(r"/product/(\d+)/(\d+)", url)
    if match:
        return int(match.group(1)), int(match.group(2))

    raise ValueError(f"Không tách được shop_id/item_id từ URL: {url}")


async def fetch_product(shop_id: int, item_id: int) -> ShopeeProduct:
    """Gọi Shopee API để lấy thông tin và giá sản phẩm.

    Endpoint: /api/v4/pdp/get_pc — endpoint thật dùng trên web Shopee.
    Yêu cầu cookie đăng nhập trong SHOPEE_COOKIE env var.

    Raises:
        httpx.HTTPError: lỗi network hoặc HTTP status != 2xx
        ValueError: Shopee trả về error hoặc không parse được giá
    """
    from app.core.config import settings

    # Thêm cookie từ env var vào headers
    # Cookie này lấy từ browser đang đăng nhập Shopee
    # Hết hạn sau ~30 ngày → cần update lại trong Vercel env vars
    headers = {
        **_HEADERS,
        # strip() loại bỏ \n, \r, space thừa ở đầu/cuối — hay bị dính khi paste vào Vercel
        "Cookie": settings.shopee_cookie.strip(),
    }

    params = {
        "item_id": item_id,
        "shop_id": shop_id,
        "detail_level": 0,
    }

    async with httpx.AsyncClient(headers=headers, timeout=_TIMEOUT_SECONDS) as client:
        response = await client.get(_SHOPEE_API, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("error") or data.get("error_code"):
        raise ValueError(f"Shopee error: {data.get('error_msg', 'unknown')}")

    # Response structure: data.data.item_info
    item = (data.get("data") or {}).get("item_info") or data.get("item", {})
    if not item:
        raise ValueError("Không parse được thông tin sản phẩm từ response")

    # Giá đơn vị 1/100000 VNĐ → chia ra VNĐ thực
    raw_price = item.get("price") or item.get("price_min") or 0
    price = raw_price / 100_000

    raw_original = item.get("price_before_discount") or 0
    original_price = raw_original / 100_000 if raw_original else price

    shop = item.get("shop_info") or {}
    is_official = bool(
        shop.get("is_official_shop")
        or shop.get("shopee_verified")
        or item.get("is_official_shop")
    )

    return ShopeeProduct(
        item_id=item_id,
        shop_id=shop_id,
        name=item.get("name", ""),
        price=price,
        original_price=original_price,
        shop_name=shop.get("name", ""),
        is_official=is_official,
    )
