# scenarios/zs_prihlaska.py
# ===========================
#
# Kompletný ZŠ scenár (1–31 krokov)
# so safe_extract + dynamickým REFEREROM pre vyhľadávanie.

import uuid

from config.random_names import generate_random_name
from config.settings import (
    HOST,
    SUBJEKT_GUID,
    PRIHLASENA_OSOBA_GUID,
    SKOLSKY_ROK_KOD_2026,
)

from payloads.dieta import create_dieta_payload
from payloads.prihlaska import (
    koncept_krok_1, koncept_krok_2, koncept_krok_3,
    koncept_krok_4, koncept_krok_5
)

from payloads.oblubene import payload_oblubene_zs, payload_add_favorite_school
from payloads.vyhladavanie import (
    search_address_payload, search_base_payload,
    search_slovak_payload, search_statne_payload,
    search_typy_payload
)


def safe_extract(resp, json_obj, path, label):
    """
    Extrakcia hodnoty z JSON podľa path (list).
    VŽDY explicitne vyhodnotí response.
    """
    try:
        obj = json_obj
        for key in path:
            obj = obj[key]

        if obj is None or obj == "":
            raise KeyError(f"{label} empty or null")

        # 🔥 SUCCESS
        resp.success()
        return obj

    except Exception as e:
        print(f"\n❌ FATAL – nepodarilo sa extrahovať {label}!")
        print(f"   Dôvod: {e}")
        print(f"   Response body: {json_obj}\n")

        # 🔥 DETAILNÁ SPRÁVA
        error_detail = f"Missing {label}: {e}"
        if isinstance(json_obj, dict):
            kod = json_obj.get('kodSpracovania', 'N/A')
            popis = json_obj.get('popisSpracovania', 'N/A')
            error_detail = f"Missing {label} | Kod: {kod} | Popis: {popis}"
        
        # 🔥 FAILURE
        resp.failure(error_detail)
        return None


def run_zs_scenario(user, http):
    http.set_context("ZS-FLOW")
    print("🎓 Spúšťam kompletný ZŠ scenár (1–31)")

    # -----------------------------------
    # KROK 0 – meno
    # -----------------------------------
    first, last = generate_random_name()
    print(f"🧒 Generujem dieťa: {first} {last}")

    # 1 – Oznámenia
    http.post_scenario(
        "/api/vratenieZoznamuOznameniPreZZ",
        {"prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
         "precitana": False,
         "pocetZaznamovNaStranku": 50,
         "cisloStranky": 1},
        "KROK 1 – Načítanie oznámení"
    )

    # 2 – Zoznam detí
    http.post_scenario(
        "/api/vratenieZoznamuDeti",
        {"guid": SUBJEKT_GUID, "lenPlatne": True},
        "KROK 2 – Zoznam detí"
    )

    # 3 – Vytvorenie dieťaťa
    resp_create = http.post_scenario(
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last),
        "KROK 3 – Pridanie dieťaťa"
    )

    dieta_guid = safe_extract(resp_create, resp_create.json(), ["dieta", "guid"], "GUID dieťaťa")
    if dieta_guid is None:
        print("🛑 STOP – GUID dieťaťa chýba.")
        return

    # 4 – Refresh
    http.post_scenario(
        "/api/vratenieZoznamuDeti",
        {"guid": SUBJEKT_GUID, "lenPlatne": True},
        "KROK 4 – Refresh detí"
    )

    # 5 – Detail dieťaťa
    http.post_scenario(
        "/api/vratenieUdajovDietata",
        {"guid": dieta_guid},
        "KROK 5 – Detail dieťaťa"
    )

    # 6 – Koncept krok 1
    resp_k1 = http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid),
        "KROK 6 – Koncept krok 1"
    )

    prihlaska_guid = safe_extract(resp_k1, resp_k1.json(), ["prihlaska", "prihlaskaGUID"], "GUID prihlášky")
    if prihlaska_guid is None:
        print("🛑 STOP – GUID prihlášky chýba.")
        return

    # ----------------------------------------------------------
    # 🔥 DYNAMICKÝ REFERER (pre všetky vyhľadávania)
    # ----------------------------------------------------------
    dyn_ref = f"{HOST}/Prihlaska?typSaSZ=ZS&guid={prihlaska_guid}"
    http.set_referer(dyn_ref)

    # 7 – Koncept krok 2
    http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_2(dieta_guid, prihlaska_guid),
        "KROK 7 – Koncept krok 2"
    )

    # 8 – Obľúbené ZŠ
    http.post_scenario(
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs(),
        "KROK 8 – Obľúbené ZŠ"
    )

    # 9 – Filtrovanie ZŠ (EXTENDED HEADERS)
    http.post_extended_scenario(
        "/api/vrateniePoloziekFiltrov",
        {"skolskyRokKod": SKOLSKY_ROK_KOD_2026, "ms": False, "zs": True},
        "KROK 9 – Filtrovanie ZŠ"
    )

    # 10 – Vyhľadávanie adresy (GET)
    http.get_scenario(
        "/api/search",
        search_address_payload(),
        "KROK 10 – Vyhľadávanie adresy"
    )

    # 11–22 – VYHĽADÁVANIA (EXTENDED)
    print("🔍 Spúšťam vyhľadávacie kroky (11–22)...")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_base_payload(20), "KROK 11 – base 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_base_payload(100000), "KROK 12 – base 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(20), "KROK 13 – slovensky 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(100000), "KROK 14 – slovensky 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(20), "KROK 15 – slovensky 20 opak")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(100000), "KROK 16 – slovensky 100k opak")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_statne_payload(20), "KROK 17 – štátne 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_statne_payload(100000), "KROK 18 – štátne 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(20), "KROK 19 – typy 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(100000), "KROK 20 – typy 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(20), "KROK 21 – typy 20 opak")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(100000), "KROK 22 – typy 100k opak")

    # 23 – obľúbené
    http.post_scenario("/api/vratenieEDUIDOblubenychSaSZ", payload_oblubene_zs(), "KROK 23 – Finálne obľúbené ZŠ")

    # 24 – pridanie obľúbenej školy
    http.post_scenario("/api/zapisOblubenychSaSZ",
                       payload_add_favorite_school(),
                       "KROK 24 – Pridanie obľúbenej školy")

    # 25 – refresh obľúbených
    http.post_scenario("/api/vratenieEDUIDOblubenychSaSZ",
                       payload_oblubene_zs(),
                       "KROK 25 – Overenie obľúbených")

    # 26–31 – dokončenie konceptu
    http.post_scenario("/api/zapisAModifikaciaKonceptuPrihlasky",
                       koncept_krok_3(dieta_guid, prihlaska_guid),
                       "KROK 26 – Koncept krok 3")

    http.post_scenario("/api/vratenieVybranychSaSZ",
                       {"prihlaskaGUID": prihlaska_guid},
                       "KROK 27 – Vybrané školy")

    http.post_scenario("/api/zapisAModifikaciaKonceptuPrihlasky",
                       koncept_krok_4(dieta_guid, prihlaska_guid),
                       "KROK 28 – Koncept krok 4")

    http.post_scenario("/api/zapisAModifikaciaKonceptuPrihlasky",
                       koncept_krok_5(dieta_guid, prihlaska_guid),
                       "KROK 29 – Koncept krok 5")

    http.post_scenario("/api/vratenieKonceptuPrihlasky",
                       {"prihlaskaGUID": prihlaska_guid},
                       "KROK 30 – Kontrola konceptu")

    http.post_scenario("/api/vratenieKonceptuPrihlasky",
                       {"prihlaskaGUID": prihlaska_guid},
                       "KROK 31 – Finálna kontrola konceptu")

    print("🏁 Scenár ZŠ kompletne dokončený (1–31).")