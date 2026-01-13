# tests/vyhladavanie/full_flow.py
# ============================================================
# VYHLADAVANIE – MS / ZŠ / SŠ (FULL TEST SUITE)
# ============================================================

import sys
import os
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.env import HOST
from config.http import build_headers

# SEARCH CASES
from tests.vyhladavanie.search_cases.ms import MS_SEARCH_CASES
from tests.vyhladavanie.search_cases.zs import ZS_SEARCH_CASES
from tests.vyhladavanie.search_cases.ss import SS_SEARCH_CASES

# PAYLOAD BUILDERS
from tests.vyhladavanie.payloads.ms import build_search_payload
from tests.vyhladavanie.payloads.zs import build_search_payload_zs
from tests.vyhladavanie.payloads.ss import build_search_payload_ss

CTX = "VYHLADAVANIE"


def send_post(login, ctx, endpoint, payload, show_data=False):
    url = f"{HOST}{endpoint}"
    headers = build_headers(login)

    print(f"[{ctx}] POST {endpoint}")

    if show_data:
        print("\n📤 PAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    resp = login.session.post(url, json=payload, headers=headers)
    print(f"[{ctx}] → {resp.status_code}")

    if show_data:
        print("\n📥 RESPONSE:")
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(resp.text)
        print()

    return resp


def run_search_suite(login, title, endpoint, builder, cases, show):
    print(f"\n🔎 {title}")
    print("-" * 60)

    success = 0
    total = len(cases)

    for i, (name, cfg) in enumerate(cases, 1):
        print(f"\n--- TEST {i}/{total}: {name} ---")

        payload = builder(**cfg)
        resp = send_post(login, CTX, endpoint, payload, show)

        ok = False
        if resp.status_code == 200:
            try:
                js = resp.json()
                if js.get("kodSpracovania") == "1700":
                    ok = True
                    count = (
                        js.get("pocet", {}).get("pocetKmenovychSaSZ")
                        or js.get("pocetSaSZ_SS", {}).get("pocetSaSZ")
                        or 0
                    )
                    print(f"🟢 PASS → Počet záznamov: {count}")
                else:
                    print(f"🔴 FAIL → kodSpracovania: {js.get('kodSpracovania')}")
            except Exception:
                print("❌ JSON parse error")
        else:
            print(f"🔴 HTTP ERROR {resp.status_code}")

        if ok:
            success += 1

    print(f"\n{title} SUMMARY: {success}/{total} tests passed")
    return success == total


def main():
    parser = argparse.ArgumentParser(
        description="Vyhľadávanie MS / ZŠ / SŠ – API test suite"
    )
    parser.add_argument("--show-data", action="store_true")
    args = parser.parse_args()
    SHOW = args.show_data

    print("\n=========================================")
    print(" VYHLADAVANIE – MS / ZŠ / SŠ (FULL TEST SUITE)")
    print("=========================================\n")

    login = saml_login()
    print("✔ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    all_ok = True

    all_ok &= run_search_suite(
        login,
        "MS SEARCH",
        "/api/vyhladanieMSaZS",
        build_search_payload,
        MS_SEARCH_CASES,
        SHOW,
    )

    all_ok &= run_search_suite(
        login,
        "ZŠ SEARCH",
        "/api/vyhladanieMSaZS",
        build_search_payload_zs,
        ZS_SEARCH_CASES,
        SHOW,
    )

    all_ok &= run_search_suite(
        login,
        "SŠ SEARCH",
        "/api/vyhladanieSaSZSS",
        build_search_payload_ss,
        SS_SEARCH_CASES,
        SHOW,
    )

    print("\n=========================================")
    if all_ok:
        print("🎉 ALL SEARCH TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME SEARCH TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
