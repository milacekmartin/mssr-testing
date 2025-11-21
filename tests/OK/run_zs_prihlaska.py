# tests/run_zs_prihlaska.py
# ============================================================
# Komplexný ZŠ scenár bez HTML, bez /Prihlaska, bez token refreshov
# Používa iba API + COMMON_HEADERS + VYHLEDAVACIE_HEADERS
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.headers import COMMON_HEADERS, VYHLEDAVACIE_HEADERS
from config.settings import HOST, SUBJEKT_GUID, PRIHLASENA_OSOBA_GUID, SKOLSKY_ROK_KOD_2026
from config.random_names import generate_random_name

from tests.common import send_post, send_get, safe_extract

from payloads.dieta import create_dieta_payload
from payloads.prihlaska import (
    koncept_krok_1, koncept_krok_2, koncept_krok_3,
    koncept_krok_4, koncept_krok_5
)
from payloads.oblubene import payload_oblubene_zs, payload_add_favorite_school
from payloads.vyhladavanie import (
    search_address_payload, search_base_payload,
    search_slovak_payload, search_statne_payload, search_typy_payload
)

CTX = "ZS-FLOW"


def main():

    print("🎓 Spúšťam ZŠ testovací scenár (1–31)…")

    # ---------------------------------------------
    # 0 – generovanie mena
    # ---------------------------------------------
    first, last = generate_random_name()
    print(f"🧒 Generujem dieťa: {first}-{last}")

    # ---------------------------------------------
    # 1 – oznámenia
    # ---------------------------------------------
    send_post(CTX, "/api/vratenieZoznamuOznameniPreZZ", {
        "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
        "precitana": False,
        "pocetZaznamovNaStranku": 50,
        "cisloStranky": 1
    })

    # ---------------------------------------------
    # 2 – zoznam detí
    # ---------------------------------------------
    send_post(CTX, "/api/vratenieZoznamuDeti", {
        "guid": SUBJEKT_GUID, "lenPlatne": True
    })

    # ---------------------------------------------
    # 3 – vytvorenie dieťaťa
    # ---------------------------------------------
    resp_create = send_post(
        CTX,
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last)
    )

    dieta_guid = safe_extract(
        resp_create, resp_create.json(),
        ["dieta", "guid"],
        "GUID dieťaťa"
    )

    # ---------------------------------------------
    # 4 – refresh detí
    # ---------------------------------------------
    send_post(CTX, "/api/vratenieZoznamuDeti", {
        "guid": SUBJEKT_GUID, "lenPlatne": True
    })

    # ---------------------------------------------
    # 5 – detail dieťaťa
    # ---------------------------------------------
    send_post(CTX, "/api/vratenieUdajovDietata", {
        "guid": dieta_guid
    })

    # ---------------------------------------------
    # 6 – koncept krok 1
    # ---------------------------------------------
    resp_k1 = send_post(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid)
    )

    prihlaska_guid = safe_extract(
        resp_k1, resp_k1.json(),
        ["prihlaska", "prihlaskaGUID"],
        "GUID prihlášky"
    )

    # ---------------------------------------------
    # 7 – koncept krok 2
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_2(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 8 – obľúbené školy
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 9 – vrateniePoloziekFiltrov (FIXED)
    # ---------------------------------------------
    print("[ZS-FLOW] POST /api/vrateniePoloziekFiltrov")

    resp_filters = send_post(
        CTX,
        "/api/vrateniePoloziekFiltrov",
        {
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "ms": False,
            "zs": True
        },
        headers=VYHLEDAVACIE_HEADERS
    )

    try:
        vzd = resp_filters.json().get("vzdialenost", [])
        print(f"   → Načítaných vzdialeností: {len(vzd)}")
    except Exception as e:
        print(f"   ⚠️ Response nie je JSON: {e}")

    # ---------------------------------------------
    # 9 – vyhľadanie adresy
    # ---------------------------------------------
    send_get(
        CTX,
        "/api/search",
        search_address_payload()
    )

    # ---------------------------------------------
    # 10–22 – vyhľadávanie MS/ZŠ (rovnaké HEADERS ako run_vyhladavanie.py)
    # ---------------------------------------------
    print("🔍 Spúšťam vyhľadávacie kroky (11–22)…")

    for p in [
        search_base_payload(20),
        search_base_payload(100000),

        search_slovak_payload(20),
        search_slovak_payload(100000),

        search_slovak_payload(20),
        search_slovak_payload(100000),

        search_statne_payload(20),
        search_statne_payload(100000),

        search_typy_payload(20),
        search_typy_payload(100000),

        search_typy_payload(20),
        search_typy_payload(100000),
    ]:
        send_post(
            CTX,
            "/api/vyhladanieMSaZS",
            p,
            headers=VYHLEDAVACIE_HEADERS
        )

    # ---------------------------------------------
    # 23 – finálne obľúbené
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 24 – pridanie obľúbenej školy
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/zapisOblubenychSaSZ",
        payload_add_favorite_school()
    )

    # ---------------------------------------------
    # 25 – overenie obľúbených
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 26 – koncept krok 3
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_3(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 27 – vybrané školy
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieVybranychSaSZ",
        {"prihlaskaGUID": prihlaska_guid}
    )

    # ---------------------------------------------
    # 28 – koncept krok 4
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_4(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 29 – koncept krok 5
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_5(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 30 – kontrola konceptu
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid}
    )

    # ---------------------------------------------
    # 31 – finálna kontrola
    # ---------------------------------------------
    send_post(
        CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid}
    )

    print("\n✔️ TEST PASSED — ZŠ scenár 1–31 prešiel úspešne.\n")


if __name__ == "__main__":
    main()
