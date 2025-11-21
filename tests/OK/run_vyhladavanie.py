# tests/run_vyhladavanie.py
# ================================================
# Vyhľadávací test iba pre endpoint /api/vyhladanieMSaZS
# Používa EXTENDED headers (rovnaké ako run_session_health)

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests

from config.settings import HOST, CSRF, COOKIE_BUNDLE
from payloads.vyhladavanie import (
    search_base_payload,
    search_slovak_payload,
    search_statne_payload,
    search_typy_payload
)


# EXTENDED HEADERS (rovnaké ako v run_session_health.py, ale plus X-Token-Descriptor)
HEADERS = {
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
    "Cookie": COOKIE_BUNDLE
}


def post_vyhladavanie(payload, ctx):
    url = f"{HOST}/api/vyhladanieMSaZS"

    print(f"[{ctx}] POST /api/vyhladanieMSaZS")

    resp = requests.post(url, json=payload, headers=HEADERS)

    print(f"[{ctx}] → Status: {resp.status_code}")

    if resp.status_code != 200:
        print("\n❌ TEST FAILED – vyhľadávanie neprešlo.")
        print("Response body:")
        print(resp.text)
        sys.exit(1)

    return resp


def main():
    context = "VYHLADAVANIE"

    print("\n🔍 Spúšťam test vyhľadávania škôl (kroky 11–22)…\n")

    # 11 – base 20
    post_vyhladavanie(search_base_payload(20), context)

    # 12 – base 100k
    post_vyhladavanie(search_base_payload(100000), context)

    # 13 – slovensky 20
    post_vyhladavanie(search_slovak_payload(20), context)

    # 14 – slovensky 100k
    post_vyhladavanie(search_slovak_payload(100000), context)

    # 15 – slovensky 20 (opak)
    post_vyhladavanie(search_slovak_payload(20), context)

    # 16 – slovensky 100k (opak)
    post_vyhladavanie(search_slovak_payload(100000), context)

    # 17 – štátne 20
    post_vyhladavanie(search_statne_payload(20), context)

    # 18 – štátne 100k
    post_vyhladavanie(search_statne_payload(100000), context)

    # 19 – typy škôl 20
    post_vyhladavanie(search_typy_payload(20), context)

    # 20 – typy škôl 100k
    post_vyhladavanie(search_typy_payload(100000), context)

    # 21 – typy škôl 20 (opak)
    post_vyhladavanie(search_typy_payload(20), context)

    # 22 – typy škôl 100k (opak)
    post_vyhladavanie(search_typy_payload(100000), context)

    print("\n✔️ TEST PASSED — všetky vyhľadávacie volania fungujú.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
