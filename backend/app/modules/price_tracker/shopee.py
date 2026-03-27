from __future__ import annotations
# shopee.py — Shopee unofficial API client
#
# Shopee không có public API — chúng ta dùng internal API mà app Shopee gọi.
# Rủi ro: Shopee có thể thay đổi API bất cứ lúc nào hoặc block request.
# Cách giảm rủi ro: thêm headers giả browser, rate limiting, retry logic.

import re
import httpx
from dataclasses import dataclass


# Shopee internal API endpoint để lấy thông tin sản phẩm
# Tham số: itemid + shopid (lấy từ URL)
_SHOPEE_API = "https://shopee.vn/api/v4/item/get"

# Headers giả lập browser — thiếu cái này Shopee sẽ trả 403
# User-Agent: chuỗi định danh browser, Shopee dùng để filter bot
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://shopee.vn/",
    "Accept": "application/json",
    # af-ac-enc-dat: Shopee dùng để verify request từ web app
    # Để trống vẫn hoạt động trong hầu hết trường hợp
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
    """Gọi Shopee internal API để lấy thông tin và giá sản phẩm.

    Dùng httpx.AsyncClient vì đây là async function — không block event loop.
    Nếu dùng requests (sync), sẽ block toàn bộ server trong lúc chờ response.

    Raises:
        httpx.HTTPError: lỗi network hoặc HTTP status != 2xx
        ValueError: Shopee trả về error code (sản phẩm không tồn tại, bị xóa...)
    """
    params = {"itemid": item_id, "shopid": shop_id}

    async with httpx.AsyncClient(headers=_HEADERS, timeout=_TIMEOUT_SECONDS) as client:
        response = await client.get(_SHOPEE_API, params=params)
        response.raise_for_status()  # raise nếu status 4xx/5xx
        data = response.json()

    # Shopee trả error_code != 0 khi sản phẩm không hợp lệ
    error_code = data.get("error_code", data.get("error", 0))
    if error_code != 0:
        raise ValueError(f"Shopee error code {error_code}: sản phẩm không tồn tại hoặc đã bị xóa")

    item = data["item"]
    shop = item.get("shop_info", {})

    # Giá Shopee trả về đơn vị: 1/100000 VNĐ (ví dụ: 8500000 = 85.000đ)
    # Chia 100000 để ra VNĐ thực
    raw_price = item.get("price", item.get("price_min", 0))
    price = raw_price / 100_000

    raw_original = item.get("price_before_discount", 0)
    original_price = raw_original / 100_000 if raw_original else price

    # Xác định Official Store / Shopee Mall
    # is_official_shop: cửa hàng được Shopee verify
    # shopee_verified: badge xanh
    # shop_location không dùng để check official
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
