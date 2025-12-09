# locust/tests/prihlaska/test_prihlaska_all.py

import sys, os, json, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.env import HOST
from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

# Prihláška payloady
from tests.prihlaska.payloads.vyhladavanie import NEG_SEARCH_PAYLOADS
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
)

CTX = "PRIHLASKA-FLOW"


# ============================================================
# UNIFIED SEND POST (rovnaké ako child/edit)
# ============================================================
def send_post(login, ctx, endpoint, payload, show_data=False, extra_headers=None):
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

    if extra_headers:
        headers.update(extra_headers)

    print(f"[{ctx}] POST {endpoint}")

    if show_data:
        print("\n📤 REQUEST PAYLOAD:")
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


def safe_json(resp):
    try:
        return resp.json()
    except:
        return None


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Kompletné testy prihlášky")
    parser.add_argument("--show-data", action="store_true", help="Zobrazí všetky payloady a response")
    args = parser.parse_args()
    SHOW = args.show_data

    print("\n======================================================")
    print(" PRIHLASKA – FULL FLOW (DIEŤA → KROK1 → KROK2 → KROK3)")
    print("======================================================\n")

    # LOGIN
    login = saml_login()
    print("✔️ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    # ============================================================
    # 1) Vytvorenie dieťaťa
    # ============================================================
    first, last = generate_random_name()
    print(f"\n🧒 Vytváram dieťa: {first} {last}")

    child = build_base_child_payload(first, last)
    child["subjektGUID"] = login.subj_guid

    resp = send_post(login, CTX, "/api/zapisAModifikaciaDietata", child, SHOW)
    resp_json = safe_json(resp)

    dieta_guid = None
    if resp_json:
        dieta_guid = (
            resp_json.get("dieta", {}).get("guid")
            or resp_json.get("guid")
        )

    if not dieta_guid:
        print("❌ DIEŤA NEVYTVORENÉ — končím.")
        return

    print(f"✔️ Dieťa vytvorené → GUID: {dieta_guid}")

    # ============================================================
    # 2) Krok 1 prihlášky
    # ============================================================
    print("\n📋 Krok 1 – Vytváram koncept prihlášky...")

    krok1 = koncept_krok_1(dieta_guid)
    r1 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", krok1, SHOW)
    r1_json = safe_json(r1)

    if not r1_json or not r1_json.get("prihlaska", {}).get("prihlaskaGUID"):
        print("❌ KROK 1 ZLYHAL")
        print("Response:", r1.text)
        return

    prihlaska_guid = r1_json["prihlaska"]["prihlaskaGUID"]
    print(f"✔️ Krok 1 → prihláškaGUID = {prihlaska_guid}")

    # ============================================================
    # 3) Krok 2 prihlášky
    # ============================================================
    print("\n📋 Krok 2 – dopĺňam údaje...")

    krok2 = koncept_krok_2(dieta_guid, prihlaska_guid)

    r2 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", krok2, SHOW)
    if r2.status_code != 200:
        print("❌ KROK 2 ZLYHAL")
        print(r2.text)
        return

    print("✔️ Krok 2 OK")

    # ============================================================
    # 4) Krok 3 prihlášky
    # ============================================================
    print("\n📋 Krok 3 – finalizujem koncept...")

    krok3 = koncept_krok_3(dieta_guid, prihlaska_guid)

    r3 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", krok3, SHOW)
    if r3.status_code != 200:
        print("❌ KROK 3 ZLYHAL")
        print(r3.text)
        return

    print("✔️ Krok 3 OK")

    # ============================================================
    # 5) DETAIL prihlášky
    # ============================================================
    print("\n🔍 Kontrolujem detail prihlášky...")

    detail = send_post(
        login,
        CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid},
        SHOW
    )

    if detail.status_code != 200:
        print("❌ DETAIL ZLYHAL")
        print(detail.text)
        return

    print("✔️ Detail OK")

    # ============================================================
    # 6) SEARCH pozitívne testy
    # ============================================================
    print("\n🔎 Spúšťam vyhľadávacie testy...")

    SEARCH_HEADERS = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    SEARCH_PAYLOADS = [
        ("SEARCH-ZS", {"text": "", "zs": True, "ms": False, "pocetZaznamovNaStranku": 50}),
        ("SEARCH-MS", {"text": "", "zs": False, "ms": True, "pocetZaznamovNaStranku": 50}),
        ("SEARCH-TEXT", {"text": "bratislava", "zs": True, "ms": False, "pocetZaznamovNaStranku": 50}),
    ]

    for name, payload in SEARCH_PAYLOADS:
        payload.update({
            "skolskyRokKod": "2026/2027",
            "cisloStranky": 1
        })
        r = send_post(login, CTX, "/api/vyhladanieMSaZS", payload, SHOW, SEARCH_HEADERS)

        ok = False
        if r.status_code == 200:
            try:
                if r.json().get("kodSpracovania") == "1700":
                    ok = True
            except:
                pass

        print(f"{name}: {'🟢 PASS' if ok else '🔴 FAIL'}")

    # ============================================================
    # DONE
    # ============================================================
    print("\n🏁 PRIHLASKA FLOW HOTOVÝ\n")


if __name__ == "__main__":
    main()
