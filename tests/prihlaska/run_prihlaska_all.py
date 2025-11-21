# tests/prihlaska/test_prihlaska_all.py
# ============================================================
# Komplexné testy pre prihlášku: vyhľadávanie + koncepty
# ============================================================

import sys, os, json

# ===============================
# FIX PYTHON PATH (LOAD config/*)
# ===============================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # tests/prihlaska
TESTS_DIR = os.path.dirname(CURRENT_DIR)                       # tests
PROJECT_ROOT = os.path.dirname(TESTS_DIR)                      # locust (root)
sys.path.append(PROJECT_ROOT)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from config.headers import COMMON_HEADERS, EXTENDED_HEADERS, VYHLEDAVACIE_HEADERS

from tests.common import send_post, send_get, safe_extract
from config.random_names import generate_random_name

# Import DETSKÉHO payloadu zo správneho miesta
from tests.child.payloads.child import build_base_child_payload

# Importy pre prihlášku
from tests.prihlaska.payloads.vyhladavanie import (
    search_base_payload,
    search_slovak_payload,
    search_statne_payload,
    search_typy_payload,
    NEG_SEARCH_PAYLOADS
)
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_4,
    koncept_krok_5,
    NEG_KONCEPT_PAYLOADS
)

HOST = "https://test-eprihlasky.iedu.sk"
CTX = "PRIHLASKA-FLOW"

results = []


def record(name, ok):
    results.append((name, ok))


def main():
    print("🎓 Spúšťam testy prihlášky…")

    # ------------------------------------------
    # 0 — Vytvorenie dieťaťa
    # ------------------------------------------
    first, last = generate_random_name()
    print(f"🧒 Generujem dieťa: {first}-{last}")

    payload = build_base_child_payload(first, last)
    resp = send_post(CTX, "/api/zapisAModifikaciaDietata", payload)

    try:
        dieta_guid = safe_extract(resp, resp.json(), ["dieta", "guid"], "GUID dieťaťa")
    except:
        print("❌ DIEŤA NEVYTVORENÉ — končím.")
        return

    # ------------------------------------------
    # 1 — Krok 1 (vytvorenie prihlášky)
    # ------------------------------------------
    resp_k1 = send_post(CTX,
                        "/api/zapisAModifikaciaKonceptuPrihlasky",
                        koncept_krok_1(dieta_guid))

    try:
        prihlaska_guid = safe_extract(resp_k1, resp_k1.json(),
                                      ["prihlaska", "prihlaskaGUID"],
                                      "GUID prihlášky")
    except:
        print("❌ KROK 1 NEPREŠIEL — končím.")
        return

    # 2 — Krok 2
    send_post(CTX, "/api/zapisAModifikaciaKonceptuPrihlasky",
              koncept_krok_2(dieta_guid, prihlaska_guid))

    # ------------------------------------------
    # POZITÍVNE SEARCH TESTY
    # ------------------------------------------
    print("\n🔍 POZITÍVNE TESTY: vyhľadávanie\n")

    POS = [
        ("SEARCH-BASE-20", search_base_payload(20)),
        ("SEARCH-BASE-100K", search_base_payload(100000)),
        ("SEARCH-SLOVAK-20", search_slovak_payload(20)),
        ("SEARCH-SLOVAK-100K", search_slovak_payload(100000)),
        ("SEARCH-STATNE-20", search_statne_payload(20)),
        ("SEARCH-STATNE-100K", search_statne_payload(100000)),
        ("SEARCH-TYPY-20", search_typy_payload(20)),
        ("SEARCH-TYPY-100K", search_typy_payload(100000)),
    ]

    for name, p in POS:
        r = send_post(CTX, "/api/vyhladanieMSaZS", p, headers=VYHLEDAVACIE_HEADERS)
        ok = (r.status_code == 200)
        record(name, ok)
        print(f"{name} → {r.status_code}")

    # ------------------------------------------
    # NEGATÍVNE SEARCH TESTY
    # ------------------------------------------
    print("\n🔍 NEGATÍVNE TESTY: vyhľadávanie\n")

    for name, p in NEG_SEARCH_PAYLOADS.items():
        r = send_post(CTX, "/api/vyhladanieMSaZS", p, headers=VYHLEDAVACIE_HEADERS)
        ok = (r.status_code != 200)
        record(name, ok)
        print(f"{name} → {r.status_code}")

    # ------------------------------------------
    # POZITÍVNE VRATENIE KONCEPTU
    # ------------------------------------------
    send_post(CTX, "/api/zapisAModifikaciaKonceptuPrihlasky",
              koncept_krok_3(dieta_guid, prihlaska_guid))

    detail = send_post(CTX, "/api/vratenieKonceptuPrihlasky",
                       {"prihlaskaGUID": prihlaska_guid})

    ok = (detail.status_code == 200)
    record("KONCEPT-DETAIL", ok)
    print(f"KONCEPT-DETAIL → {detail.status_code}")

    # ------------------------------------------
    # NEGATÍVNE KONCEPTY
    # ------------------------------------------
    print("\n📘 NEGATÍVNE TESTY: vratenieKonceptuPrihlasky\n")

    for name, p in NEG_KONCEPT_PAYLOADS.items():
        r = send_post(CTX, "/api/vratenieKonceptuPrihlasky", p)
        ok = (r.status_code != 200)
        record(name, ok)
        print(f"{name} → {r.status_code}")

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------
    print("\n============================================================")
    print("SUMMARY")
    print("============================================================")
    print("TEST NAME                      | RESULT")
    print("--------------------------------|-------------")

    for name, ok in results:
        icon = "🟢 PASS" if ok else "🔴 FAIL"
        print(f"{name:30} | {icon}")

    print("\n🏁 HOTOVO.\n")


if __name__ == "__main__":
    main()
