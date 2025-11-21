# tests/run_vyhladavanie_bruteforce.py
# ============================================
# Brute force antiforgery token tester for /api/vyhladanieMSaZS
# Tries all known token combinations after full login.

import sys, os, json, subprocess, re, requests, uuid
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payloads.vyhladavanie import search_base_payload

HOST = "https://test-eprihlasky.iedu.sk"


# ----------------------------------------------------------------------
# 1) Call login_preview.py → returns full JSON with xsrf + cookies
# ----------------------------------------------------------------------
def get_login_data():
    proc = subprocess.run(
        ["python3", "tests/login_preview.py", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode != 0:
        print("❌ login_preview.py failed")
        print(proc.stderr)
        sys.exit(1)

    try:
        return json.loads(proc.stdout)
    except Exception as e:
        print("❌ ERROR parsing JSON:")
        print(proc.stdout)
        print(e)
        sys.exit(1)


# ----------------------------------------------------------------------
# 2) GET /Najst-skolu → extract ALL possible antiforgery tokens
# ----------------------------------------------------------------------
def extract_antiforgery_tokens(login):
    cookies = login["cookies"]
    resp = requests.get(f"{HOST}/Najst-skolu", cookies=cookies)
    html = resp.text

    # Save debug
    with open("dump_Najst_skolu_bruteforce.html", "w", encoding="utf-8") as f:
        f.write(html)

    # A) hidden <input>
    hidden = re.findall(
        r'<input[^>]+name="__RequestVerificationToken"[^>]+value="([^"]+)"',
        html
    )
    hidden_token = hidden[0] if hidden else None

    # B) strings starting with CfDJ (HTML embed)
    all_html_tokens = re.findall(r"(CfDJ[0-9A-Za-z_\-]+)", html)

    # C) antiforgery cookies
    cookie_fAr6 = cookies.get(".AspNetCore.Antiforgery.fAr6xnvBhu0")
    cookie_UaYX = cookies.get(".AspNetCore.Antiforgery.UaYXyBoyr8Q")

    return hidden_token, all_html_tokens, cookie_fAr6, cookie_UaYX, html


# ----------------------------------------------------------------------
# 3) Generic POST attempt
# ----------------------------------------------------------------------
def try_token(token, iam_token, cookie_header, label):
    print(f"\n===== TEST {label} =====")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Najst-skolu",

        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),

        "X-Requested-With": "XMLHttpRequest",
        "X-Token-Descriptor": iam_token,
        "Cookie": cookie_header,
        "RequestVerificationToken": token,

        # browser headers
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',

        # correlation ID
        "X-Correlation-Id": str(uuid.uuid4())
    }

    url = f"{HOST}/api/vyhladanieMSaZS"
    payload = search_base_payload(20)

    r = requests.post(url, json=payload, headers=headers)

    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:400]}...")
    return r.status_code


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    print("🔐 Spúšťam login…")
    login = get_login_data()

    iam_token = login["iamToken"]
    cookies = login["cookies"]

    # Build cookie header exactly like browser
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    # Extract tokens from /Najst-skolu
    print("\n🌐 GET /Najst-skolu → extrahujem tokeny…")
    hidden, html_tokens, cookie_fAr6, cookie_UaYX, html = extract_antiforgery_tokens(login)

    print("\n==============================")
    print("🔑 TOKEN DUMP")
    print("==============================")
    print("Hidden token:", hidden)
    print("HTML CfDJ tokens:", html_tokens)
    print("Cookie fAr6xnvBhu0:", cookie_fAr6)
    print("Cookie UaYXyBoyr8Q:", cookie_UaYX)

    print("\n==============================")
    print("🚀 SPÚŠŤAM BRUTE-FORCE TOKEN TEST")
    print("==============================")

    # TEST A — hidden input
    if hidden:
        try_token(hidden, iam_token, cookie_header, "HTML hidden <input>")

    # TEST B — each HTML CfDJ token
    for i, t in enumerate(html_tokens):
        try_token(t, iam_token, cookie_header, f"HTML CfDJ token #{i+1}")

    # TEST C — antiforgery cookie fAr6
    if cookie_fAr6:
        try_token(cookie_fAr6, iam_token, cookie_header, "Cookie fAr6xnvBhu0")

    # TEST D — antiforgery cookie UaYX
    if cookie_UaYX:
        try_token(cookie_UaYX, iam_token, cookie_header, "Cookie UaYXyBoyr8Q")

    # TEST E — combos
    if hidden and cookie_fAr6:
        try_token(hidden + "," + cookie_fAr6, iam_token, cookie_header,
                  "hidden + fAr6")

    if hidden and cookie_UaYX:
        try_token(hidden + "," + cookie_UaYX, iam_token, cookie_header,
                  "hidden + UaYX")

    if len(html_tokens) > 0 and cookie_fAr6:
        try_token(html_tokens[0] + "," + cookie_fAr6,
                  iam_token, cookie_header,
                  "CfDJ0 + fAr6")

    if len(html_tokens) > 0 and cookie_UaYX:
        try_token(html_tokens[0] + "," + cookie_UaYX,
                  iam_token, cookie_header,
                  "CfDJ0 + UaYX")

    if hidden and cookie_fAr6 and cookie_UaYX:
        try_token(hidden + "," + cookie_fAr6 + "," + cookie_UaYX,
                  iam_token, cookie_header,
                  "hidden + fAr6 + UaYX (ALL)")

    print("\n🔥 HOTOVO – pozri ktorá kombinácia dala 200 OK.\n")


if __name__ == "__main__":
    main()
