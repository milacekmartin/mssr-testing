# tests/run_vyhladavanie.py
# ============================================
# STRICT, FULLY BROWSER-ACCURATE SEARCH TEST

import sys, os, json, subprocess, re, requests, uuid
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payloads.vyhladavanie import (
    search_base_payload,
    search_slovak_payload,
    search_statne_payload,
    search_typy_payload
)

HOST = "https://test-eprihlasky.iedu.sk"


# ============================================
# 1) Run login_preview.py and get JSON login data
# ============================================
def get_login_data():
    proc = subprocess.run(
        ["python3", "tests/login_preview.py", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode != 0:
        print("❌ login_preview.py FAILED")
        print(proc.stderr)
        sys.exit(1)

    try:
        return json.loads(proc.stdout)
    except Exception as e:
        print("❌ ERROR parsing JSON from login_preview.py")
        print(proc.stdout)
        print(e)
        sys.exit(1)


# ============================================
# 2) Add browser-only cookies (_DC, cookies-warning, last_non_error_path)
# ============================================
def enrich_browser_cookies(login_cookies):
    enriched = dict(login_cookies)

    if "_DC" not in enriched:
        enriched["_DC"] = "c%3Dsk-SK%7Cuic%3Dsk-SK"

    enriched["cookies-warning"] = "true"
    enriched["last_non_error_path"] = "/Najst-skolu"

    return enriched


# ============================================
# 3) Extract hidden RequestVerificationToken from /Najst-skolu
# ============================================
def get_tokens_and_cookie_header(login):
    # START with login cookies
    sess = requests.Session()
    sess.cookies.update(login["cookies"])

    # GET /Najst-skolu – this will SET NEW antiforgery cookie
    resp = sess.get(f"{HOST}/Najst-skolu")

    html = resp.text
    with open("debug_Najst_skolu.html", "w", encoding="utf-8") as f:
        f.write(html)

    # extract new antiforgery cookie (THIS IS THE REAL ONE)
    api_cookie = None
    for k, v in sess.cookies.get_dict().items():
        if k.startswith(".AspNetCore.Antiforgery"):
            api_cookie = v

    if not api_cookie:
        print("❌ ERROR – server did not provide new antiforgery cookie!")
        sys.exit(1)

    # Extract HTML hidden input (used only for UI, but OK)
    m = re.search(r'<input name="__RequestVerificationToken"[^>]+value="([^"]+)"', html)
    html_hidden = m.group(1) if m else None

    # BUILD REAL cookie header – using updated session cookies
    final_cookie_header = "; ".join([f"{k}={v}" for k, v in sess.cookies.get_dict().items()])

    return html_hidden, api_cookie, final_cookie_header


# ============================================
# 4) POST wrapper with correlation ID
# ============================================
def post_vyhladavanie(payload, HEADERS, ctx):
    url = f"{HOST}/api/vyhladanieMSaZS"

    HEADERS["x-correlation-id"] = str(uuid.uuid4())
    print(f"[{ctx}] POST /api/vyhladanieMSaZS (corr={HEADERS['x-correlation-id']})")

    resp = requests.post(url, json=payload, headers=HEADERS)

    print(f"[{ctx}] → Status: {resp.status_code}")

    if resp.status_code != 200:
        print("\n❌ TEST FAILED — vyhľadávanie neprešlo.")
        print("Response:")
        print(resp.text)
        sys.exit(1)

    return resp


# ============================================
# MAIN
# ============================================
def main():

    print("🔐 Spúšťam login…\n")
    login = get_login_data()

    print("👉 XSRF:", login["xsrfToken"])
    print("👉 IAM TOKEN:", login["iamToken"])
    print("👉 loggedInPersonGuid:", login["loggedInPersonGuid"])
    print("👉 subjectGuid:", login["subjectGuid"])
    print("👉 Cookies:", login["cookies"], "\n")

    print("🌐 GET /Najst-skolu → získavam nový HTML antiforgery token…")
    html_token, api_cookie, cookie_header = get_tokens_and_cookie_header(login)

    print("👉 HTML RequestVerificationToken:", html_token)
    print("👉 API Antiforgery Token:", api_cookie, "\n")

    # ============================================
    # Build FINAL browser-accurate headers
    # ============================================
    HEADERS = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Najst-skolu",

        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),

        "X-Requested-With": "XMLHttpRequest",

        # *** CRITICAL TOKENS ***
        "RequestVerificationToken": api_cookie,
        "x-token-descriptor": login["iamToken"],

        # Full cookie header
        "Cookie": cookie_header,

        # browser fields
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    print("🔧 HEADERS pripravené:\n")
    for k, v in HEADERS.items():
        print(f"  {k}: {v}")
    print("\n")

    print("🔍 2) Spúšťam vyhľadávacie volania (11–22)…\n")
    ctx = "VYHLADAVANIE"

    post_vyhladavanie(search_base_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_base_payload(100000), HEADERS, ctx)

    post_vyhladavanie(search_slovak_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_slovak_payload(100000), HEADERS, ctx)
    post_vyhladavanie(search_slovak_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_slovak_payload(100000), HEADERS, ctx)

    post_vyhladavanie(search_statne_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_statne_payload(100000), HEADERS, ctx)

    post_vyhladavanie(search_typy_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_typy_payload(100000), HEADERS, ctx)
    post_vyhladavanie(search_typy_payload(20), HEADERS, ctx)
    post_vyhladavanie(search_typy_payload(100000), HEADERS, ctx)

    print("\n✔️ TEST PASSED — všetky vyhľadávacie volania fungujú.\n")


if __name__ == "__main__":
    main()
