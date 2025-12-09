import sys, os, json, argparse

# ===========================================
# FIX Python PATH → umožní importovať login/*
# ===========================================
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.env import HOST
from tests.vyhladavanie.payloads.search import build_search_payload, SEARCH_TEST_CONFIGS


CTX = "VYHLADAVANIE"


# ===========================================
# UNIFIED SEND POST
# ===========================================
def send_post(login, ctx, endpoint, payload, show_data=False):
    url = f"{HOST}{endpoint}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Moj-profil2",
        "RequestVerificationToken": login.csrf,
        "x-token-descriptor": login.token_desc,
        "Cookie": login.cookie_bundle,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
    }

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
        except:
            print(resp.text)
        print()

    return resp


# ===========================================
# MAIN
# ===========================================
def main():
    parser = argparse.ArgumentParser(description="Vyhľadávanie MS/ZS – API testy")
    parser.add_argument("--show-data", action="store_true")
    args = parser.parse_args()
    SHOW = args.show_data

    print("\n=========================================")
    print(" VYHLADAVANIE – MS / ZS (FULL TEST SUITE)")
    print("=========================================\n")

    # SAML LOGIN
    login = saml_login()

    print("✔️ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    print("\n🔍 Spúšťam testy vyhľadávania...\n")

    success = 0
    total = len(SEARCH_TEST_CONFIGS)

    for i, (name, cfg) in enumerate(SEARCH_TEST_CONFIGS, 1):
        print(f"\n--- TEST {i}/{total}: {name} ---")

        payload = build_search_payload(**cfg)

        resp = send_post(login, CTX, "/api/vyhladanieMSaZS", payload, SHOW)

        ok = False
        if resp.status_code == 200:
            try:
                js = resp.json()
                if js.get("kodSpracovania") == "1700":
                    ok = True
                    print(f"🟢 PASS → Počet škôl: {js.get('pocet', {}).get('pocetKmenovychSaSZ', 0)}")
                else:
                    print(f"🔴 FAIL → kodSpracovania: {js.get('kodSpracovania')}")
            except:
                print("❌ JSON error")
        else:
            print(f"🔴 HTTP ERROR {resp.status_code}")

        if ok:
            success += 1

    # SUMMARY
    print("\n=========================================")
    print(f"SUMMARY: {success}/{total} tests passed")
    print("=========================================\n")

    if success == total:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
