from __future__ import annotations
# services.py — Business logic: track sản phẩm, check giá, so sánh, alert

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.price_tracker import shopee, telegram
from app.modules.price_tracker.models import TrackedProduct, PriceSnapshot
from app.modules.price_tracker.schemas import (
    TrackProductRequest,
    TrackedProductResponse,
    CheckResultResponse,
    PriceSnapshotResponse,
)

_PRODUCTS_COL = "tracked_products"
_SNAPSHOTS_COL = "price_snapshots"


def _to_response(doc: dict) -> TrackedProductResponse:
    return TrackedProductResponse(
        id=str(doc["_id"]),
        shopee_url=doc["shopee_url"],
        shop_id=doc["shop_id"],
        item_id=doc["item_id"],
        product_name=doc["product_name"],
        shop_name=doc["shop_name"],
        is_official=doc["is_official"],
        current_price=doc["current_price"],
        alert_threshold_pct=doc["alert_threshold_pct"],
        last_checked=doc["last_checked"].isoformat(),
        created_at=doc["created_at"].isoformat(),
    )


async def add_product(
    db: AsyncIOMotorDatabase, data: TrackProductRequest
) -> TrackedProductResponse:
    """Thêm sản phẩm mới vào danh sách theo dõi.

    Flow:
    1. Parse URL → shop_id + item_id
    2. Fetch Shopee API → lấy tên, giá, shop info
    3. Lưu vào MongoDB
    4. Lưu snapshot giá đầu tiên
    """
    shop_id, item_id = shopee.parse_shopee_url(data.shopee_url)

    # Kiểm tra đã track chưa — tránh duplicate
    existing = await db[_PRODUCTS_COL].find_one(
        {"shop_id": shop_id, "item_id": item_id}
    )
    if existing:
        return _to_response(existing)

    # Fetch thông tin sản phẩm từ Shopee
    product_info = await shopee.fetch_product(shop_id, item_id)

    product = TrackedProduct(
        shopee_url=data.shopee_url,
        shop_id=shop_id,
        item_id=item_id,
        product_name=product_info.name,
        shop_name=product_info.shop_name,
        is_official=product_info.is_official,
        current_price=product_info.price,
        alert_threshold_pct=data.alert_threshold_pct,
    )

    doc = product.model_dump()
    result = await db[_PRODUCTS_COL].insert_one(doc)
    inserted_id = result.inserted_id

    # Lưu snapshot giá đầu tiên
    snapshot = PriceSnapshot(
        product_id=str(inserted_id),
        price=product_info.price,
    )
    await db[_SNAPSHOTS_COL].insert_one(snapshot.model_dump())

    created = await db[_PRODUCTS_COL].find_one({"_id": inserted_id})
    return _to_response(created)


async def list_products(db: AsyncIOMotorDatabase) -> list[TrackedProductResponse]:
    cursor = db[_PRODUCTS_COL].find({}).sort("created_at", -1)
    docs = await cursor.to_list(None)
    return [_to_response(doc) for doc in docs]


async def delete_product(db: AsyncIOMotorDatabase, product_id: str) -> bool:
    if not ObjectId.is_valid(product_id):
        return False
    result = await db[_PRODUCTS_COL].delete_one({"_id": ObjectId(product_id)})
    # Xóa luôn price history
    await db[_SNAPSHOTS_COL].delete_many({"product_id": product_id})
    return result.deleted_count == 1


async def get_price_history(
    db: AsyncIOMotorDatabase, product_id: str
) -> list[PriceSnapshotResponse]:
    """Lấy lịch sử giá của 1 sản phẩm, mới nhất trước."""
    cursor = (
        db[_SNAPSHOTS_COL]
        .find({"product_id": product_id})
        .sort("checked_at", -1)
        .limit(100)  # Giới hạn 100 điểm dữ liệu
    )
    docs = await cursor.to_list(None)
    return [
        PriceSnapshotResponse(
            price=doc["price"],
            checked_at=doc["checked_at"].isoformat(),
        )
        for doc in docs
    ]


async def check_all_prices(db: AsyncIOMotorDatabase) -> CheckResultResponse:
    """Cron job: check giá tất cả sản phẩm đang track.

    Flow cho mỗi sản phẩm:
    1. Fetch giá mới từ Shopee
    2. So sánh với giá cũ
    3. Nếu thay đổi >= threshold → gửi Telegram alert
    4. Cập nhật current_price và last_checked trong DB
    5. Lưu snapshot mới
    """
    products = await db[_PRODUCTS_COL].find({}).to_list(None)

    checked = 0
    alerted = 0
    errors: list[str] = []

    for doc in products:
        product_id = str(doc["_id"])
        try:
            new_info = await shopee.fetch_product(doc["shop_id"], doc["item_id"])
            new_price = new_info.price
            old_price = doc["current_price"]

            # Tính % thay đổi giá
            # abs(): lấy giá trị tuyệt đối — alert cả tăng lẫn giảm
            if old_price > 0:
                change_pct = abs((new_price - old_price) / old_price) * 100
            else:
                change_pct = 0

            # Gửi alert nếu biến động vượt ngưỡng
            if change_pct >= doc["alert_threshold_pct"]:
                await telegram.send_price_alert(
                    product_name=doc["product_name"],
                    shop_name=doc["shop_name"],
                    old_price=old_price,
                    new_price=new_price,
                    shopee_url=doc["shopee_url"],
                    is_official=doc["is_official"],
                )
                alerted += 1

            # Cập nhật giá mới và thời gian check
            await db[_PRODUCTS_COL].update_one(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "current_price": new_price,
                        "last_checked": datetime.now(timezone.utc),
                    }
                },
            )

            # Lưu snapshot — dùng để vẽ biểu đồ lịch sử giá
            snapshot = PriceSnapshot(product_id=product_id, price=new_price)
            await db[_SNAPSHOTS_COL].insert_one(snapshot.model_dump())

            checked += 1

        except Exception as e:
            # Không raise — 1 sản phẩm lỗi không nên dừng cả cron job
            errors.append(f"{doc.get('product_name', product_id)}: {str(e)}")

    return CheckResultResponse(checked=checked, alerted=alerted, errors=errors)
