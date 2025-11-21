# tests/run_vyhladavanie.py
# ================================================
# Vyhľadávací test pre endpoint /api/vyhladanieMSaZS
# Používa PRIAMO čerstvé tokeny z login_preview.saml_login()

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests

# importujeme náš SAML login engine
from locust.tests.obsolete.login_preview import saml_login

# Payloady
from payloads.vyhladavanie import (
    search_base_payload,
    search_slovak_payload,
    search_statne_payload,
    search_typy_payload
)


def build_headers(xsrf, cookie_bundle, iam_token):
    """Vytvorí full browser-like EXTENDED headers pre vyhľadávanie."""

    return {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",

        # MUSÍ BYŤ — antiforgery validation
        "Origin": "https://test-eprihlasky.iedu.sk",
        "Referer": "https://test-eprihlasky.iedu.sk/",

        # MUSÍ BYŤ — RequestVerificationToken
        "RequestVerificationToken": xsrf,

        # MUSÍ BYŤ — AJAX validation
        "X-Requested-With": "XMLHttpRequest",

        # User-Agent (browser identity)
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36",

        # CORS metadata
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",

        # IAM token
        "X-Token-Descriptor": iam_token,

        # cookies
        "Cookie": cookie_bundle
    }


def format_cookie_bundle(cookie_dict):
    """Prevedie dict cookies → string ako v reálnom browseri."""
    return "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])


def post_vyhladavanie(url, payload, headers, ctx):
    print(f"[{ctx}] POST /api/vyhladanieMSaZS")

    resp = requests.post(url, json=payload, headers=headers)

    print(f"[{ctx}] → Status: {resp.status_code}")

    if resp.status_code != 200:
        print("\n❌ TEST FAILED – vyhľadávanie neprešlo.")
        print("Response body:")
        print(resp.text)
        sys.exit(1)

    return resp


def main():

    print("\n🔐 1) Spúšťam SAML login…\n")

    login = saml_login()

    xsrf = login["xsrfToken"]
    cookies = login["cookies"]
    iam_token = login["iamToken"]

    cookie_bundle_str = format_cookie_bundle(cookies)

    print("👉 XSRF Token:", xsrf)
    print("👉 IAM TOKEN:", iam_token)
    print("👉 Cookies:", cookie_bundle_str)
    print("👉 loggedInPersonGuid:", login["loggedInPersonGuid"])
    print("👉 subjectGuid:", login["subjectGuid"])

    print("\n🔧 Budujem HEADERS pre vyhľadávanie…")

    HEADERS = build_headers(xsrf, cookie_bundle_str, iam_token)

    HOST = "https://test-eprihlasky.iedu.sk"
    URL = f"{HOST}/api/vyhladanieMSaZS"

    print("\n🔍 2) Spúšťam test vyhľadávania škôl (kroky 11–22)…\n")

    context = "VYHLADAVANIE"

    # 11 – base 20
    post_vyhladavanie(URL, search_base_payload(20), HEADERS, context)

    # 12 – base 100k
    post_vyhladavanie(URL, search_base_payload(100000), HEADERS, context)

    # 13 – slovensky 20
    post_vyhladavanie(URL, search_slovak_payload(20), HEADERS, context)

    # 14 – slovensky 100k
    post_vyhladavanie(URL, search_slovak_payload(100000), HEADERS, context)

    # 15 – slovensky 20 (opak)
    post_vyhladavanie(URL, search_slovak_payload(20), HEADERS, context)

    # 16 – slovensky 100k (opak)
    post_vyhladavanie(URL, search_slovak_payload(100000), HEADERS, context)

    # 17 – štátne 20
    post_vyhladavanie(URL, search_statne_payload(20), HEADERS, context)

    # 18 – štátne 100k
    post_vyhladavanie(URL, search_statne_payload(100000), HEADERS, context)

    # 19 – typy škôl 20
    post_vyhladavanie(URL, search_typy_payload(20), HEADERS, context)

    # 20 – typy škôl 100k
    post_vyhladavanie(URL, search_typy_payload(100000), HEADERS, context)

    # 21 – typy škôl 20 (opak)
    post_vyhladavanie(URL, search_typy_payload(20), HEADERS, context)

    # 22 – typy škôl 100k (opak)
    post_vyhladavanie(URL, search_typy_payload(100000), HEADERS, context)

    print("\n✔️ TEST PASSED — všetky vyhľadávacie volania fungujú.\n")


if __name__ == "__main__":
    main()
