"""
update_images.py — Tự động lấy ảnh Shopee cho tất cả sản phẩm đã có link
Chạy: python3 update_images.py
"""

import json
import time
import urllib.request
import urllib.parse

API_BASE = "https://shopping-list-nu-gilt.vercel.app/api"


def api_get(path: str) -> dict:
    req = urllib.request.Request(f"{API_BASE}{path}",
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def api_patch(path: str, data: dict) -> bool:
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{API_BASE}{path}", data=payload,
                                  headers={"Content-Type": "application/json"},
                                  method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
            return True
    except Exception:
        return False


def fetch_image(shopee_url: str) -> str:
    encoded = urllib.parse.quote(shopee_url, safe="")
    req = urllib.request.Request(
        f"{API_BASE}/items/shopee-image?url={encoded}",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
            return data.get("image_url", "")
    except Exception:
        return ""


def main():
    print(f"Fetching items from {API_BASE}...\n")
    items = api_get("/items/")["items"]

    # Chỉ xử lý items có shopee_url nhưng chưa có image_url
    targets = [i for i in items if i.get("shopee_url") and not i.get("image_url")]
    print(f"Cần lấy ảnh: {len(targets)}/{len(items)} sản phẩm\n")

    ok = 0
    for idx, item in enumerate(targets, 1):
        print(f"  [{idx:02d}/{len(targets)}] {item['name']}")
        print(f"           → {item['shopee_url'][:60]}...")

        image_url = fetch_image(item["shopee_url"])
        if image_url:
            success = api_patch(f"/items/{item['id']}", {"image_url": image_url})
            if success:
                print(f"           ✓ {image_url[:70]}...")
                ok += 1
            else:
                print(f"           ✗ PATCH thất bại")
        else:
            print(f"           ✗ Không lấy được ảnh")

        # Nghỉ 1 giây giữa các request để không bị Shopee rate-limit
        time.sleep(1)

    print(f"\nHoàn thành: {ok}/{len(targets)} sản phẩm có ảnh.")


if __name__ == "__main__":
    main()
