# tests/common.py
# ==========================

import json
import requests
import sys

from config.settings import HOST, CSRF, IAM_TOKEN, COOKIE_BUNDLE


# ---------------------------------------------------------
#  HEADERS
# ---------------------------------------------------------
COMMON_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "RequestVerificationToken": CSRF,
    "X-Token-Descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE
}

EXTENDED_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": HOST,
    "Referer": f"{HOST}/",
    "RequestVerificationToken": CSRF,
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "X-Token-Descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE
}


# ---------------------------------------------------------
#  LOG
# ---------------------------------------------------------
def log(context, method, url, status):
    print(f"[{context}] {method} {url} → {status}")


session = requests.Session()


# ---------------------------------------------------------
#  POST
# ---------------------------------------------------------
def send_post(context, url, payload, extended=False, headers=None):
    if headers is not None:
        final_headers = headers
    else:
        final_headers = EXTENDED_HEADERS if extended else COMMON_HEADERS

    try:
        resp = requests.post(HOST + url, json=payload, headers=final_headers)
    except Exception as e:
        print(f"[{context}] ERROR during POST {url}: {e}")
        return None

    print(f"[{context}] POST {url} → {resp.status_code}")
    return resp

# ---------------------------------------------------------
#  GET
# ---------------------------------------------------------
def send_get(context, url, params):
    resp = session.get(
        HOST + url,
        params=params,
        headers=COMMON_HEADERS
    )

    log(context, "GET", url, resp.status_code)

    if resp.status_code != 200:
        print(f"\n❌ TEST FAILED – {url} returned {resp.status_code}")
        print("Response:")
        print(resp.text)
        sys.exit(1)

    return resp


# ---------------------------------------------------------
# SAFE EXTRACT
# ---------------------------------------------------------
def safe_extract(resp, json_obj, path, label):
    try:
        obj = json_obj
        for p in path:
            obj = obj[p]

        if obj is None or obj == "":
            raise KeyError(f"{label} empty")

        return obj

    except Exception as e:
        print(f"\n❌ FATAL – Missing {label}: {e}")
        print("Response:")
        print(json.dumps(json_obj, indent=2, ensure_ascii=False))
        print("\nTEST FAILED\n")
        sys.exit(1)
