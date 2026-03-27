#!/usr/bin/env python3
"""
check_prices.py — Chạy trên máy local, fetch giá Shopee và gửi Telegram alert.

Chạy thủ công:
    python check_prices.py

Chạy tự động mỗi 1h (macOS launchd):
    Xem hướng dẫn trong README bên dưới.
"""

import asyncio
import os
import re
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from pymongo import MongoClient

# Đọc .env trong cùng thư mục
load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DB = os.environ.get("MONGODB_DB", "shopping_list")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
SHOPEE_COOKIE = os.environ.get("SHOPEE_COOKIE", "")

# Dùng pymongo sync thay vì motor async — script đơn giản hơn
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]


def fetch_product_price(shop_id: int, item_id: int) -> dict:
    """Fetch giá sản phẩm từ Shopee. Chạy từ IP nhà → không bị block."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://shopee.vn/",
        "Accept": "application/json",
        "x-api-source": "pc",
        "x-shopee-language": "vi",
        "Cookie": SHOPEE_COOKIE.strip(),
    }

    params = {"item_id": item_id, "shop_id": shop_id, "detail_level": 0}

    with httpx.Client(headers=headers, timeout=15, follow_redirects=True) as client:
        response = client.get("https://shopee.vn/api/v4/pdp/get_pc", params=params)
        response.raise_for_status()
        return response.json()


def parse_price(data: dict) -> tuple[str, float, bool]:
    """Tách tên, giá, is_official từ response Shopee."""
    item = (data.get("data") or {}).get("item_info") or data.get("item", {})
    if not item:
        raise ValueError("Không parse được item từ response")

    raw_price = item.get("price") or item.get("price_min") or 0
    price = raw_price / 100_000

    shop = item.get("shop_info") or {}
    is_official = bool(
        shop.get("is_official_shop") or shop.get("shopee_verified")
    )

    return item.get("name", ""), price, is_official


def send_telegram(product_name: str, shop_name: str, old_price: float,
                  new_price: float, url: str, is_official: bool):
    """Gửi thông báo Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Chưa config Telegram, bỏ qua notification")
        return

    change_pct = ((new_price - old_price) / old_price) * 100
    direction = "📉 GIẢM" if new_price < old_price else "📈 TĂNG"
    badge = "🏅 Official" if is_official else ""

    def fmt(p): return f"{p:,.0f}đ"

    msg = (
        f"⚠️ *Biến động giá Shopee* {direction} {abs(change_pct):.1f}%\n\n"
        f"📦 *{product_name}*\n"
        f"🏪 {shop_name} {badge}\n\n"
        f"💰 Giá cũ: {fmt(old_price)}\n"
        f"💥 Giá mới: *{fmt(new_price)}*\n\n"
        f"🔗 [Xem trên Shopee]({url})"
    )

    with httpx.Client(timeout=10) as c:
        c.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
        )


def run():
    print(f"\n{'='*50}")
    print(f"🕐 Check giá: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    products = list(db["tracked_products"].find({}))
    if not products:
        print("📭 Không có sản phẩm nào đang track.")
        return

    for doc in products:
        name = doc.get("product_name", "Unknown")
        try:
            data = fetch_product_price(doc["shop_id"], doc["item_id"])
            product_name, new_price, is_official = parse_price(data)
            old_price = doc["current_price"]

            change_pct = abs((new_price - old_price) / old_price * 100) if old_price else 0
            threshold = doc.get("alert_threshold_pct", 5.0)

            print(f"\n📦 {product_name or name}")
            print(f"   Giá cũ: {old_price:,.0f}đ → Giá mới: {new_price:,.0f}đ ({change_pct:.1f}%)")

            if change_pct >= threshold:
                print(f"   🚨 Biến động {change_pct:.1f}% >= {threshold}% → Gửi Telegram!")
                send_telegram(
                    product_name=product_name or name,
                    shop_name=doc.get("shop_name", ""),
                    old_price=old_price,
                    new_price=new_price,
                    url=doc["shopee_url"],
                    is_official=is_official,
                )

            # Cập nhật giá mới trong MongoDB
            db["tracked_products"].update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "current_price": new_price,
                    "last_checked": datetime.now(timezone.utc),
                }},
            )

            # Lưu snapshot lịch sử
            db["price_snapshots"].insert_one({
                "product_id": str(doc["_id"]),
                "price": new_price,
                "checked_at": datetime.now(timezone.utc),
            })

        except Exception as e:
            print(f"   ❌ Lỗi: {e}")

    print(f"\n✅ Xong. Check lại sau 1 giờ.")


if __name__ == "__main__":
    run()
