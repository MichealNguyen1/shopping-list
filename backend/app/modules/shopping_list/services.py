# services.py — Business logic, tất cả thao tác với MongoDB
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Tại sao tách services khỏi router?
# Router chỉ nên làm 2 việc: nhận request, trả response.
# Logic thực sự (query DB, transform data) nằm ở service.
# Lợi ích: dễ test service độc lập mà không cần chạy HTTP server.

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.shopping_list.models import ShoppingItem
from app.modules.shopping_list.schemas import ItemCreate, ItemUpdate, ItemResponse


# Tên collection trong MongoDB
# Convention: dùng số nhiều, snake_case
_COLLECTION = "items"


def _to_response(doc: dict) -> ItemResponse:
    """Convert MongoDB document dict → ItemResponse schema.

    Tại sao cần hàm này?
    MongoDB trả về dict với "_id" là ObjectId.
    Client cần JSON với "id" là string.
    Hàm này làm cầu nối giữa 2 world đó.
    """
    return ItemResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        category=doc.get("category", "Khác"),
        brand=doc.get("brand", ""),
        quantity=doc["quantity"],
        price=doc["price"],
        is_purchased=doc["is_purchased"],
        shopee_url=doc.get("shopee_url", ""),
        note=doc.get("note", ""),
        created_at=doc["created_at"].isoformat(),
    )


async def get_all_items(db: AsyncIOMotorDatabase) -> list[ItemResponse]:
    """Lấy tất cả items, sắp xếp mới nhất trước.

    find({}) = không filter gì = lấy tất cả documents trong collection.
    sort("created_at", -1) = sort DESC theo thời gian tạo.
    to_list(None) = convert cursor → list, None = không giới hạn số lượng.

    Cursor là gì? MongoDB không trả về tất cả kết quả 1 lần (tốn RAM).
    Thay vào đó nó trả về cursor — một "con trỏ" để iterate qua kết quả từng phần.
    """
    cursor = db[_COLLECTION].find({}).sort("created_at", -1)
    docs = await cursor.to_list(None)
    return [_to_response(doc) for doc in docs]


async def get_item_by_id(db: AsyncIOMotorDatabase, item_id: str) -> ItemResponse | None:
    """Lấy 1 item theo ID. Trả về None nếu không tìm thấy.

    Tại sao phải convert item_id thành ObjectId?
    MongoDB lưu _id dưới dạng ObjectId (binary), không phải string.
    Nếu tìm bằng string thì sẽ không match — đây là lỗi phổ biến nhất khi mới học MongoDB.
    """
    # Validate format trước khi query, tránh exception từ MongoDB
    if not ObjectId.is_valid(item_id):
        return None

    doc = await db[_COLLECTION].find_one({"_id": ObjectId(item_id)})
    if doc is None:
        return None
    return _to_response(doc)


async def create_item(db: AsyncIOMotorDatabase, data: ItemCreate) -> ItemResponse:
    """Tạo item mới, trả về item đã được tạo (có id và created_at).

    insert_one() trả về InsertOneResult chứa inserted_id.
    Sau khi insert, phải query lại để lấy full document (có _id và created_at).

    Tại sao query lại thay vì build response thủ công?
    Đảm bảo response phản ánh đúng data đang nằm trong DB,
    tránh trường hợp có default value hoặc transformation ở DB level.
    """
    item = ShoppingItem(
        name=data.name,
        brand=data.brand,
        quantity=data.quantity,
        price=data.price,
    )

    # model_dump(by_alias=True) → convert sang dict, dùng alias "_id" thay vì "id"
    # exclude_none=True → bỏ qua field None (id=None lúc chưa insert)
    doc = item.model_dump(by_alias=True, exclude_none=True)
    result = await db[_COLLECTION].insert_one(doc)

    # Query lại document vừa insert để lấy full data
    created = await db[_COLLECTION].find_one({"_id": result.inserted_id})
    return _to_response(created)


async def update_item(
    db: AsyncIOMotorDatabase, item_id: str, data: ItemUpdate
) -> ItemResponse | None:
    """Cập nhật item, trả về item sau khi update. None nếu không tìm thấy.

    PATCH semantics: chỉ update field được gửi lên, giữ nguyên field còn lại.
    Dùng $set operator của MongoDB để update từng field riêng lẻ.

    Ví dụ: chỉ gửi {"is_purchased": true} → chỉ field đó thay đổi,
    name/quantity/price giữ nguyên.
    """
    if not ObjectId.is_valid(item_id):
        return None

    # exclude_none=True: bỏ qua field None (không gửi lên) → chỉ update field có giá trị
    update_data = data.model_dump(exclude_none=True)

    if not update_data:
        # Không có gì để update → trả về item hiện tại
        return await get_item_by_id(db, item_id)

    # $set: chỉ update các field được chỉ định, KHÔNG xóa field khác
    # (khác với replace_one() sẽ thay toàn bộ document)
    # return_document=True → trả về document SAU khi update
    result = await db[_COLLECTION].find_one_and_update(
        {"_id": ObjectId(item_id)},
        {"$set": update_data},
        return_document=True,  # True = AFTER, False = BEFORE
    )

    if result is None:
        return None
    return _to_response(result)


async def delete_item(db: AsyncIOMotorDatabase, item_id: str) -> bool:
    """Xóa item. Trả về True nếu xóa thành công, False nếu không tìm thấy."""
    if not ObjectId.is_valid(item_id):
        return False

    result = await db[_COLLECTION].delete_one({"_id": ObjectId(item_id)})

    # deleted_count = số document đã xóa (0 hoặc 1 vì filter theo _id)
    return result.deleted_count == 1
