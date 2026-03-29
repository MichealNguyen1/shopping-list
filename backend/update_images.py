"""
update_images.py — Lấy ảnh Shopee thông qua CDP + localStorage token.

Luồng:
  1. Copy Chrome profile → temp dir (bypass "default dir" restriction)
  2. Mở Chrome với CDP, load shopee.vn để lấy af-ac-enc-dat từ localStorage
  3. Dùng token đó + pycookiecheat cookies để gọi Shopee API bằng requests
  4. PATCH ảnh lên API của mình

YÊU CẦU: Chrome phải ĐÓNG trước khi chạy.
Chạy:   /opt/homebrew/bin/python3.12 update_images.py
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from playwright.async_api import async_playwright

try:
    import requests
    from pycookiecheat import chrome_cookies
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

API_BASE           = "https://shopping-list-nu-gilt.vercel.app/api"
CHROME_APP         = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PROFILE_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")
CDP_URL            = "http://localhost:9222"

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = { runtime: {} };
"""


# ── API helpers ────────────────────────────────────────────────────────────────

def api_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}", headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def api_patch(item_id: str, image_url: str) -> bool:
    payload = json.dumps({"image_url": image_url}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/items/{item_id}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
            return True
    except Exception as e:
        print(f"             PATCH error: {e}")
        return False


# ── Profile copy ───────────────────────────────────────────────────────────────

def copy_profile(src_root: str) -> str:
    tmp = tempfile.mkdtemp(prefix="shopee_cdp_")
    src = os.path.join(src_root, "Default")
    dst = os.path.join(tmp, "Default")
    skip = shutil.ignore_patterns(
        "Cache", "Code Cache", "GPUCache", "ShaderCache",
        "CrashpadMetrics*", "Crashpad",
        "LOCK", "SingletonLock", "SingletonCookie", "SingletonSocket",
        "LOG", "LOG.old", "*.log",
    )
    try:
        shutil.copytree(src, dst, ignore=skip, dirs_exist_ok=True)
    except Exception as e:
        print(f"  (copy warning: {e})")
    return tmp


# ── Resolve short URL → product URL → shop_id, item_id ───────────────────────

def resolve_short_url(short_url: str) -> tuple[str, str]:
    """Trả về (shop_id, item_id) hoặc ('', '')"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
        )
    }
    try:
        req = urllib.request.Request(short_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            final = r.url
        # Format 1: /i.{shop_id}.{item_id}
        m = re.search(r'i\.(\d+)\.(\d+)', final)
        if m:
            return m.group(1), m.group(2)
        # Format 2: /{username}/{shop_id}/{item_id}
        m2 = re.search(r'/(\d{6,})/(\d{8,})', final)
        if m2:
            return m2.group(1), m2.group(2)
    except Exception:
        pass
    return "", ""


# ── Shopee API call (requires af-ac-enc-dat) ──────────────────────────────────

def shopee_get_image(shop_id: str, item_id: str, session: "requests.Session") -> str:
    """Gọi Shopee API để lấy hash ảnh đầu tiên."""
    try:
        r = session.get(
            "https://shopee.vn/api/v4/item/get",
            params={"itemid": item_id, "shopid": shop_id},
            timeout=12,
        )
        if r.status_code == 200:
            data = r.json()
            imgs = (
                data.get("data", {}).get("item", {}).get("images")
                or data.get("item", {}).get("images")
                or []
            )
            if imgs:
                return f"https://down-vn.img.susercontent.com/file/{imgs[0]}"
    except Exception:
        pass
    return ""


# ── Browser-based image fetch (fallback) ─────────────────────────────────────

async def fetch_image_via_browser(page, shopee_url: str) -> str:
    captured: dict = {}

    async def on_response(response):
        try:
            url = response.url
            if "pdp/get_pc" not in url and "item/get" not in url:
                return
            if "json" not in response.headers.get("content-type", ""):
                return
            data = await response.json()
            imgs = (
                data.get("data", {}).get("item", {}).get("images")
                or data.get("item", {}).get("images")
                or []
            )
            if imgs:
                captured["image"] = f"https://down-vn.img.susercontent.com/file/{imgs[0]}"
        except Exception:
            pass

    page.on("response", on_response)
    try:
        await page.goto(shopee_url, wait_until="domcontentloaded", timeout=30_000)
        for _ in range(20):
            if "image" in captured:
                break
            await asyncio.sleep(0.5)

        if "image" not in captured:
            try:
                await page.wait_for_selector('img[src*="susercontent.com"]', timeout=15_000)
                for el in await page.query_selector_all('img[src*="susercontent.com"]'):
                    src = (await el.get_attribute("src") or "").split("?")[0]
                    if "susercontent.com" in src and "_tn" not in src:
                        captured["image"] = src
                        break
                    if "susercontent.com" in src and "image" not in captured:
                        captured["image"] = src
            except Exception:
                pass
    except Exception as e:
        msg = str(e)
        if "timeout" not in msg.lower() and "closed" not in msg.lower():
            print(f"               browser error: {msg[:80]}")
    finally:
        page.remove_listener("response", on_response)

    return captured.get("image", "")


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    if not HAS_REQUESTS:
        print("THIẾU: requests hoặc pycookiecheat chưa được cài.")
        print("Chạy: pip install requests pycookiecheat")
        return

    print("Fetching items from API...\n")
    items   = api_get("/items/")["items"]
    targets = [i for i in items if i.get("shopee_url") and not i.get("image_url")]
    print(f"Cần lấy ảnh: {len(targets)}/{len(items)} sản phẩm\n")

    if not targets:
        print("Tất cả sản phẩm đã có ảnh rồi!")
        return

    # Chờ Chrome đóng
    check = subprocess.run(["pgrep", "-x", "Google Chrome"], capture_output=True)
    if check.returncode == 0:
        print("⚠️  Chrome đang chạy!")
        print("   Hãy đóng Chrome (Cmd+Q) rồi script sẽ tự tiếp tục...\n")
        while True:
            await asyncio.sleep(1)
            if subprocess.run(["pgrep", "-x", "Google Chrome"], capture_output=True).returncode != 0:
                print("Chrome đã đóng.\n")
                break

    # Copy profile
    print("Đang copy Chrome profile...")
    tmp_dir = copy_profile(CHROME_PROFILE_DIR)
    print(f"OK — temp dir: {tmp_dir}\n")

    chrome_proc = None
    ok = fail = 0

    try:
        # Mở Chrome với CDP
        print("Mở Chrome với remote debugging port 9222...")
        chrome_proc = subprocess.Popen(
            [
                CHROME_APP,
                "--remote-debugging-port=9222",
                f"--user-data-dir={tmp_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Chờ CDP
        started = False
        for _ in range(40):
            await asyncio.sleep(0.5)
            try:
                with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2):
                    started = True
                    break
            except Exception:
                pass

        if not started:
            print("Chrome không khởi động được sau 20 giây.")
            return

        print("Chrome sẵn sàng.\n")

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            await ctx.add_init_script(STEALTH_JS)
            page = await ctx.new_page()

            # Warm-up + lấy af-ac-enc-dat từ localStorage
            print("Warm-up: mở shopee.vn (đợi 8 giây)...")
            await page.goto("https://shopee.vn", wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(8)

            af_token = await page.evaluate("() => localStorage.getItem('af-ac-enc-dat')")
            csrftoken = await page.evaluate(
                "() => document.cookie.split('; ').find(r=>r.startsWith('SPC_SC_SESSION'))?.split('=')[1] || ''"
            )
            print(f"af-ac-enc-dat: {'✓ có' if af_token else '✗ không có'}")

            # Tạo requests session với cookies + af-ac-enc-dat
            shopee_cookies = chrome_cookies("https://shopee.vn")
            sess = requests.Session()
            sess.cookies.update(shopee_cookies)
            sess.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
                "Accept-Language": "vi-VN,vi;q=0.9",
                "Referer": "https://shopee.vn/",
                "x-requested-with": "XMLHttpRequest",
            })
            if af_token:
                sess.headers["af-ac-enc-dat"] = af_token

            print(f"Session ready: {len(shopee_cookies)} cookies, af_token={'YES' if af_token else 'NO'}\n")
            print("Bắt đầu lấy ảnh...\n")

            for idx, item in enumerate(targets, 1):
                print(f"  [{idx:02d}/{len(targets):02d}] {item['name'][:55]}")
                img = ""

                # Bước 1: resolve short URL → shop_id / item_id
                shop_id, item_id = resolve_short_url(item["shopee_url"])
                if shop_id and item_id:
                    img = shopee_get_image(shop_id, item_id, sess)
                    if not img:
                        print(f"               API failed (shop={shop_id} item={item_id}), thử browser...")

                # Bước 2: fallback qua browser
                if not img:
                    img = await fetch_image_via_browser(page, item["shopee_url"])

                if img:
                    if api_patch(item["id"], img):
                        print(f"             ✓ {img[:80]}")
                        ok += 1
                    else:
                        print(f"             ✗ PATCH thất bại")
                        fail += 1
                else:
                    print(f"             ✗ Không lấy được ảnh")
                    fail += 1

                await asyncio.sleep(1.5)

            await page.close()
            await browser.close()

    finally:
        if chrome_proc:
            chrome_proc.terminate()
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print("\nĐã dọn dẹp.")

    print(f"\nKết quả: {ok} ✓  |  {fail} ✗  |  tổng {len(targets)}")


if __name__ == "__main__":
    asyncio.run(main())
