from __future__ import annotations
# telegram.py — Gửi thông báo qua Telegram Bot API
#
# Setup (làm 1 lần):
# 1. Mở Telegram → tìm @BotFather → /newbot → đặt tên → copy BOT_TOKEN
# 2. Mở bot vừa tạo → gửi /start
# 3. Mở https://api.telegram.org/bot{BOT_TOKEN}/getUpdates → copy "id" trong "chat"
#    → đó là TELEGRAM_CHAT_ID của bạn

import httpx
from app.core.config import settings

# Telegram Bot API endpoint gửi message
# {token}: BOT_TOKEN từ BotFather
_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def send_price_alert(
    product_name: str,
    shop_name: str,
    old_price: float,
    new_price: float,
    shopee_url: str,
    is_official: bool,
) -> None:
    """Gửi thông báo biến động giá qua Telegram.

    Chỉ gửi nếu TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID đã được config.
    Nếu chưa config → bỏ qua (không raise error) để không block cron job.
    """
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        # Chưa config Telegram → skip silently
        return

    change_pct = ((new_price - old_price) / old_price) * 100
    direction = "📉 GIẢM" if new_price < old_price else "📈 TĂNG"
    official_badge = "🏅 Official Store" if is_official else ""

    # Format số tiền kiểu Việt Nam: 85000 → "85,000"
    def fmt(price: float) -> str:
        return f"{price:,.0f}đ"

    message = (
        f"⚠️ *Biến động giá Shopee* {direction} {abs(change_pct):.1f}%\n\n"
        f"📦 *{product_name}*\n"
        f"🏪 {shop_name} {official_badge}\n\n"
        f"💰 Giá cũ: ~~{fmt(old_price)}~~\n"
        f"💥 Giá mới: *{fmt(new_price)}*\n\n"
        f"🔗 [Xem trên Shopee]({shopee_url})"
    )

    url = _TELEGRAM_API.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        # MarkdownV2 hỗ trợ bold, strikethrough, link
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json=payload)
        # Log lỗi nhưng không raise — thông báo thất bại không nên làm crash cron job
        if not response.is_success:
            print(f"[telegram] Failed to send alert: {response.text}")
