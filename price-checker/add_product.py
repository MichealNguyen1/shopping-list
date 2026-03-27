#!/usr/bin/env python3
"""Thêm sản phẩm Shopee vào danh sách track — chạy 1 lần khi muốn theo dõi sản phẩm mới."""

import re
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
import httpx

load_dotenv()

db = MongoClient(os.environ["MONGODB_URI"])[os.environ.get("MONGODB_DB", "shopping_list")]
SHOPEE_COOKIE = os.environ.get("SHOPEE_COOKIE", "")


def parse_url(url: str) -> tuple[int, int]:
    m = re.search(r"-i\.(\d+)\.(\d+)", url)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"/product/(\d+)/(\d+)", url)
    if m:
        return int(m.group(1)), int(m.group(2))
    raise ValueError("URL không hợp lệ")


def fetch_info(shop_id: int, item_id: int) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://shopee.vn/",
        "Accept": "application/json",
        "x-api-source": "pc",
        "Cookie": SHOPEE_COOKIE.strip(),
    }
    r = httpx.get(
        "https://shopee.vn/api/v4/pdp/get_pc",
        params={"item_id": item_id, "shop_id": shop_id, "detail_level": 0},
        headers=headers, timeout=15
    )
    r.raise_for_status()
    return r.json()


def main():
    url = input("Shopee URL: ").strip()
    threshold = float(input("Ngưỡng cảnh báo % (Enter = 5): ").strip() or "5")

    shop_id, item_id = parse_url(url)
    print(f"shop_id={shop_id}, item_id={item_id}")
    print("Đang fetch từ Shopee...")

    data = fetch_info(shop_id, item_id)
    item = (data.get("data") or {}).get("item_info") or data.get("item", {})

    if not item:
        print(f"❌ Không lấy được thông tin. Response: {data}")
        return

    price = (item.get("price") or item.get("price_min") or 0) / 100_000
    shop = item.get("shop_info") or {}
    name = item.get("name", "")
    shop_name = shop.get("name", "")
    is_official = bool(shop.get("is_official_shop") or shop.get("shopee_verified"))

    print(f"\n✅ Sản phẩm: {name}")
    print(f"   Shop: {shop_name} {'[Official]' if is_official else ''}")
    print(f"   Giá: {price:,.0f}đ")

    # Kiểm tra đã track chưa
    existing = db["tracked_products"].find_one({"shop_id": shop_id, "item_id": item_id})
    if existing:
        print("⚠️  Sản phẩm này đã được track rồi.")
        return

    now = datetime.now(timezone.utc)
    result = db["tracked_products"].insert_one({
        "shopee_url": url,
        "shop_id": shop_id,
        "item_id": item_id,
        "product_name": name,
        "shop_name": shop_name,
        "is_official": is_official,
        "current_price": price,
        "alert_threshold_pct": threshold,
        "last_checked": now,
        "created_at": now,
    })

    db["price_snapshots"].insert_one({
        "product_id": str(result.inserted_id),
        "price": price,
        "checked_at": now,
    })

    print(f"\n🎉 Đã thêm vào danh sách track!")


if __name__ == "__main__":
    main()
