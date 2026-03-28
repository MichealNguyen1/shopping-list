# router.py — Định nghĩa HTTP endpoints
from __future__ import annotations  # cho phép dùng X | Y syntax trên Python 3.9
#
# Router chỉ làm 2 việc:
# 1. Nhận HTTP request, validate input (Pydantic tự làm)
# 2. Gọi service, trả HTTP response với đúng status code
#
# Business logic KHÔNG nằm ở đây — nằm ở services.py

import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.modules.shopping_list import services
from app.modules.shopping_list.schemas import (
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)

# APIRouter giống như "mini app" — group các endpoint liên quan
# prefix="/items" → tất cả route trong router này đều bắt đầu bằng /items
# tags=["items"] → nhóm trong Swagger UI (/docs)
router = APIRouter(prefix="/items", tags=["items"])


# Dependency Injection cho database
# Hàm này được FastAPI gọi tự động mỗi khi có request vào endpoint nào dùng Depends(get_db)
# Tại sao dùng Depends thay vì import trực tiếp?
# → Dễ mock trong testing: chỉ cần override dependency, không cần patch module
def get_db() -> AsyncIOMotorDatabase:
    return get_database()


@router.get(
    "/shopee-image",
    summary="Tự động lấy ảnh từ Shopee URL",
)
async def get_shopee_image(url: str = Query(..., description="Shopee product URL")):
    """GET /items/shopee-image?url=... — Fetch og:image từ trang sản phẩm Shopee."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            resp = await client.get(url, headers=headers)

        # Tìm og:image trong HTML (Shopee render server-side)
        match = re.search(
            r'<meta\b[^>]*\bproperty=["\']og:image["\']\s[^>]*\bcontent=["\']([^"\']+)["\']'
            r'|<meta\b[^>]*\bcontent=["\']([^"\']+)["\']\s[^>]*\bproperty=["\']og:image["\']',
            resp.text,
        )
        if match:
            image_url = match.group(1) or match.group(2)
            return {"image_url": image_url}
    except Exception:
        pass
    return {"image_url": ""}


@router.get(
    "/",
    response_model=ItemListResponse,
    summary="Lấy danh sách tất cả items",
)
async def list_items(db: AsyncIOMotorDatabase = Depends(get_db)):
    """GET /items — Trả về tất cả shopping items, sắp xếp mới nhất trước."""
    items = await services.get_all_items(db)
    return ItemListResponse(items=items, total=len(items))


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Lấy 1 item theo ID",
)
async def get_item(item_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """GET /items/{item_id} — Trả về item cụ thể."""
    item = await services.get_item_by_id(db, item_id)
    if item is None:
        # HTTP 404: resource không tồn tại
        # raise HTTPException thay vì return để FastAPI tự format error response
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} không tồn tại",
        )
    return item


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,  # 201 Created thay vì 200 OK khi tạo mới
    summary="Tạo item mới",
)
async def create_item(data: ItemCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """POST /items — Tạo shopping item mới.

    FastAPI tự động:
    - Parse JSON body → ItemCreate (validate bằng Pydantic)
    - Trả 422 Unprocessable Entity nếu data không hợp lệ
    """
    return await services.create_item(db, data)


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Cập nhật item (partial update)",
)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """PATCH /items/{item_id} — Cập nhật một hoặc nhiều field của item.

    Dùng PATCH (không phải PUT) vì chỉ update field được gửi lên.
    Ví dụ: chỉ gửi {"is_purchased": true} để đánh dấu đã mua.
    """
    item = await services.update_item(db, item_id, data)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} không tồn tại",
        )
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 204: thành công nhưng không có body
    summary="Xóa item",
)
async def delete_item(item_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """DELETE /items/{item_id} — Xóa item khỏi danh sách."""
    deleted = await services.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} không tồn tại",
        )
    # 204 No Content: không return gì — đây là convention REST cho DELETE thành công
