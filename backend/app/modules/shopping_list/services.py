from __future__ import annotations
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.shopping_list.schemas import ItemCreate, ItemUpdate, ItemResponse

_COLLECTION = "items"


def _to_response(doc: dict) -> ItemResponse:
    return ItemResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        category=doc.get("category", "Khác"),
        shopee_url=doc.get("shopee_url", ""),
        image_url=doc.get("image_url", ""),
        quantity=doc.get("quantity", 1),
        note=doc.get("note", ""),
        status=doc.get("status", "purchased" if doc.get("is_purchased") else "considering"),
        skip_reason=doc.get("skip_reason", ""),
        created_at=doc["created_at"].isoformat(),
    )


async def get_all_items(db: AsyncIOMotorDatabase) -> list[ItemResponse]:
    # sort theo category trước, rồi created_at — giữ grouping ổn định
    cursor = db[_COLLECTION].find({}).sort([("category", 1), ("created_at", 1)])
    docs = await cursor.to_list(None)
    return [_to_response(doc) for doc in docs]


async def get_item_by_id(db: AsyncIOMotorDatabase, item_id: str) -> ItemResponse | None:
    if not ObjectId.is_valid(item_id):
        return None
    doc = await db[_COLLECTION].find_one({"_id": ObjectId(item_id)})
    return _to_response(doc) if doc else None


async def create_item(db: AsyncIOMotorDatabase, data: ItemCreate) -> ItemResponse:
    now = datetime.now(timezone.utc)
    doc = {
        "name": data.name,
        "category": data.category,
        "shopee_url": data.shopee_url,
        "image_url": data.image_url,
        "quantity": data.quantity,
        "note": data.note,
        "status": "considering",
        "skip_reason": "",
        "created_at": now,
    }
    result = await db[_COLLECTION].insert_one(doc)
    created = await db[_COLLECTION].find_one({"_id": result.inserted_id})
    return _to_response(created)


async def update_item(
    db: AsyncIOMotorDatabase, item_id: str, data: ItemUpdate
) -> ItemResponse | None:
    if not ObjectId.is_valid(item_id):
        return None

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return await get_item_by_id(db, item_id)

    result = await db[_COLLECTION].find_one_and_update(
        {"_id": ObjectId(item_id)},
        {"$set": update_data},
        return_document=True,
    )
    return _to_response(result) if result else None


async def delete_item(db: AsyncIOMotorDatabase, item_id: str) -> bool:
    if not ObjectId.is_valid(item_id):
        return False
    result = await db[_COLLECTION].delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count == 1
