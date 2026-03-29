"""
import_products.py — Bulk import từ Google Sheets vào shopping list API
Chạy: python import_products.py
Mặc định gọi localhost:8000. Đổi API_BASE nếu muốn import thẳng lên Vercel.
"""

import json
import urllib.request
import urllib.error

API_BASE = "https://shopping-list-42q1iv0jr-cuongs-projects-d4d71256.vercel.app/api"

PRODUCTS = [
    # ── 1. Đồ cho bé ăn ──────────────────────────────────────────────────
    {"category": "1. Đồ cho bé ăn", "name": "bình sữa Dr Brown", "shopee_url": ""},
    {"category": "1. Đồ cho bé ăn", "name": "bình sữa Hegen", "shopee_url": ""},
    {"category": "1. Đồ cho bé ăn", "name": "thanh sữa meji", "shopee_url": ""},
    {"category": "1. Đồ cho bé ăn", "name": "sữa Aptamil", "shopee_url": ""},
    {"category": "1. Đồ cho bé ăn", "name": "nước cọ bình mamamy", "shopee_url": "https://s.shopee.vn/2g0H3ZY3vi"},
    {"category": "1. Đồ cho bé ăn", "name": "bộ cọ bình", "shopee_url": "https://s.shopee.vn/AA6HzIKFyW"},

    # ── 2. Sản phẩm vệ sinh ───────────────────────────────────────────────
    {"category": "2. Sản phẩm vệ sinh", "name": "rơ lưỡi dr papie", "shopee_url": "https://s.shopee.vn/709GDd5egF"},
    {"category": "2. Sản phẩm vệ sinh", "name": "rơ lưỡi cao su", "shopee_url": "https://s.shopee.vn/8KedmbphK6"},
    {"category": "2. Sản phẩm vệ sinh", "name": "nước muối fysoline", "shopee_url": "https://s.shopee.vn/20kaGUb9sI"},
    {"category": "2. Sản phẩm vệ sinh", "name": "kem hăm bepanthen", "shopee_url": "https://s.shopee.vn/2VgqpxELSC"},
    {"category": "2. Sản phẩm vệ sinh", "name": "kem hăm bebble", "shopee_url": "https://s.shopee.vn/6KtZQYE2oi"},
    {"category": "2. Sản phẩm vệ sinh", "name": "xịt khử khuẩn dizigone", "shopee_url": "https://s.shopee.vn/8Uy3z3TpS7"},
    {"category": "2. Sản phẩm vệ sinh", "name": "xịt khử khuẩn joona baby", "shopee_url": "https://s.shopee.vn/8pauPFNI4z"},
    {"category": "2. Sản phẩm vệ sinh", "name": "sữa tắm cetaphill", "shopee_url": "https://s.shopee.vn/60Gj0XWvWG"},
    {"category": "2. Sản phẩm vệ sinh", "name": "sữa tắm bebble", "shopee_url": "https://s.shopee.vn/5L12EIYEqP"},
    {"category": "2. Sản phẩm vệ sinh", "name": "sữa tắm joshon baby", "shopee_url": "https://s.shopee.vn/AA6HyFkJ6A"},
    {"category": "2. Sản phẩm vệ sinh", "name": "chậu tắm", "shopee_url": "https://s.shopee.vn/AA6HyJE6EB"},
    {"category": "2. Sản phẩm vệ sinh", "name": "nước giặt dnee", "shopee_url": "https://s.shopee.vn/2VgqqHF47e"},
    {"category": "2. Sản phẩm vệ sinh", "name": "nước giặt pompom", "shopee_url": "https://s.shopee.vn/3fsoFoMq0e"},
    {"category": "2. Sản phẩm vệ sinh", "name": "dầu mát xa pigeon", "shopee_url": "https://s.shopee.vn/9pTRZnQDFF"},
    {"category": "2. Sản phẩm vệ sinh", "name": "dầu mát xa chico", "shopee_url": "https://s.shopee.vn/1BBTHOuelh"},

    # ── 3. Tủ thuốc ───────────────────────────────────────────────────────
    {"category": "3. Tủ thuốc", "name": "d3k2 lineabon", "shopee_url": "https://s.shopee.vn/2VgqqN3dVE"},
    {"category": "3. Tủ thuốc", "name": "vitamin D", "shopee_url": ""},
    {"category": "3. Tủ thuốc", "name": "kem dưỡng Aveeno", "shopee_url": "https://s.shopee.vn/8pauPPAzKP"},
    {"category": "3. Tủ thuốc", "name": "xịt muỗi babycocole", "shopee_url": "https://s.shopee.vn/8pauPSedvy"},

    # ── 4. Bìm, khăn ướt ─────────────────────────────────────────────────
    {"category": "4. Bìm, khăn ướt", "name": "bỉm moony", "shopee_url": "https://s.shopee.vn/7V5WsxPsUz"},
    {"category": "4. Bìm, khăn ướt", "name": "gooby đêm", "shopee_url": "https://s.shopee.vn/7V5Wsu0gwE"},
    {"category": "4. Bìm, khăn ướt", "name": "khăn khô mamamy", "shopee_url": "https://s.shopee.vn/6fWPpWucHm"},
    {"category": "4. Bìm, khăn ướt", "name": "khăn khô zizou", "shopee_url": "https://s.shopee.vn/1BBTFzGAe0"},
    {"category": "4. Bìm, khăn ướt", "name": "khăn khô mipbi", "shopee_url": "https://s.shopee.vn/Blw4Maj0I"},

    # ── 5. Đồ vải cho bé ─────────────────────────────────────────────────
    {"category": "5. Đồ vải cho bé", "name": "gối musline", "shopee_url": "https://s.shopee.vn/2g0H30qbHE"},
    {"category": "5. Đồ vải cho bé", "name": "gối dono&dono", "shopee_url": ""},
    {"category": "5. Đồ vải cho bé", "name": "lót chống thấm", "shopee_url": "https://s.shopee.vn/9pTRaEo1Sc"},
    {"category": "5. Đồ vải cho bé", "name": "thảm lót Dotori", "shopee_url": "https://s.shopee.vn/5L12FSoYPW"},
    {"category": "5. Đồ vải cho bé", "name": "khăn sữa tef store", "shopee_url": "https://s.shopee.vn/VvmTDNYMi"},
    {"category": "5. Đồ vải cho bé", "name": "khăn sữa manny", "shopee_url": "https://s.shopee.vn/4flLQn6cKp"},
    {"category": "5. Đồ vải cho bé", "name": "khăn sữa nappi", "shopee_url": "https://s.shopee.vn/7piNDit5WE"},
    {"category": "5. Đồ vải cho bé", "name": "khăn sữa iuem", "shopee_url": "https://s.shopee.vn/6VCzcIeg8G"},
    {"category": "5. Đồ vải cho bé", "name": "khăn tắm tef store", "shopee_url": "https://s.shopee.vn/1LUtVSVdyv"},
    {"category": "5. Đồ vải cho bé", "name": "khăn tắm L Ange", "shopee_url": "https://s.shopee.vn/5fdsdsaBpT"},
    {"category": "5. Đồ vải cho bé", "name": "chũn Unbee", "shopee_url": "https://s.shopee.vn/4Ap4q4CTNV"},

    # ── 6. Máy móc ────────────────────────────────────────────────────────
    {"category": "6. Máy móc", "name": "đèn ngủ", "shopee_url": "https://s.shopee.vn/9KXB0vJIdE"},
    {"category": "6. Máy móc", "name": "máy hút sữa kamidi max", "shopee_url": "https://s.shopee.vn/1LUtSuHmje"},
    {"category": "6. Máy móc", "name": "máy hút sữa kamidi smart", "shopee_url": "https://s.shopee.vn/4VRvFyw5Cz"},
    {"category": "6. Máy móc", "name": "máy hâm sữa", "shopee_url": "https://s.shopee.vn/1g7jszwx4a"},

    # ── 7. Quần áo cho bé ─────────────────────────────────────────────────
    {"category": "7. Quần áo cho bé", "name": "set nous", "shopee_url": "https://s.shopee.vn/8fHUHn3zwf"},
]


def create_item(product: dict) -> bool:
    payload = json.dumps({
        "name": product["name"],
        "category": product["category"],
        "shopee_url": product.get("shopee_url", ""),
        "note": product.get("note", ""),
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{API_BASE}/items/",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
            return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {product['name']}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {product['name']} — {e}")
        return False


def main():
    print(f"Importing {len(PRODUCTS)} sản phẩm → {API_BASE}\n")
    ok = 0
    for i, p in enumerate(PRODUCTS, 1):
        success = create_item(p)
        status = "✓" if success else "✗"
        print(f"  [{i:02d}/{len(PRODUCTS)}] {status} [{p['category']}] {p['name']}")
        if success:
            ok += 1

    print(f"\nHoàn thành: {ok}/{len(PRODUCTS)} sản phẩm đã import.")


if __name__ == "__main__":
    main()
