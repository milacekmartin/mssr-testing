# scenarios/zs_prihlaska.py
# ===========================
# Kompletný ZŠ scenár (1–31 krokov)
# Používa SAML login cez http.auth

import uuid

from config.random_names import generate_random_name
from config.env import HOST

# payload builders
from tests.child.payloads.child import build_base_child_payload
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1, koncept_krok_2, koncept_krok_3,
    koncept_krok_4, koncept_krok_5
)
from tests.vyhladavanie.payloads.search import (
    build_search_payload
)
from payloads.oblubene import payload_oblubene_zs, payload_add_favorite_school


# ---------------------------------------------------------------------
# SAFE EXTRACT (opravené so správnym loggingom)
# ---------------------------------------------------------------------
from locust import events  # ✔ správny import

def safe_extract(resp, label, path):
    """
    Extrahuje hodnotu a ak neexistuje → vytvorí LOCUST FAILURE,
    ktoré sa ZOBRAZÍ v UI v záložke Failures.
    """

    try:
        js = resp.json()
        obj = js
        for key in path:
            obj = obj[key]

        if not obj:
            raise KeyError(f"{label} empty")

        resp.success()
        return obj

    except Exception as e:
        preview = resp.text[:400]
        detail = f"{label} missing: {e} | response: {preview}"

        print(f"\n❌ {detail}\n")

        # Označ pôvodný HTTP request ako FAIL
        resp.failure(detail)

        # 🔥 ZAREGISTRUJ FAILURE DO LOCUST UI
        events.request.fire(
            request_type="SCENARIO",
            name=f"CHYBA – {label}",
            response_time=0,
            response_length=len(preview),
            exception=Exception(detail)
        )

        return None




# ---------------------------------------------------------------------
# HLAVNÝ ZŠ SCENÁR
# ---------------------------------------------------------------------
def run_zs_scenario(user, http):
    """
    user → Locust user instance (má wait_time, env, auth, logger, user_id…)
    http → náš custom HTTP wrapper (má post_scenario / get_scenario)
    """

    http.set_context("ZS-FLOW")
    print(f"🎓 Spúšťam ZŠ scenár – user: {user.user_id}")

    # =====================================================================================
    # KROK 0 – meno dieťaťa
    # =====================================================================================
    first, last = generate_random_name()
    print(f"🧒 Generujem dieťa: {first} {last}")

    subjekt_guid = user.auth.subj_guid
    prihlasena_osoba_guid = user.auth.logged_guid

    # =====================================================================================
    # KROK 1 – OZNÁMENIA
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieZoznamuOznameniPreZZ",
        {
            "prihlasenaOsobaGUID": prihlasena_osoba_guid,
            "precitana": False,
            "pocetZaznamovNaStranku": 50,
            "cisloStranky": 1,
        },
        "KROK 1 – Načítanie oznámení"
    )

    # =====================================================================================
    # KROK 2 – ZOZNAM DETÍ
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieZoznamuDeti",
        {"guid": subjekt_guid, "lenPlatne": True},
        "KROK 2 – Zoznam detí"
    )

    # =====================================================================================
    # KROK 3 – VYTVORENIE DIEŤAŤA
    # =====================================================================================
    child_payload = build_base_child_payload(first, last)
    child_payload["subjektGUID"] = subjekt_guid

    resp_create = http.post_scenario(
        "/api/zapisAModifikaciaDietata",
        child_payload,
        "KROK 3 – Pridanie dieťaťa"
    )

    dieta_guid = safe_extract(resp_create, "GUID dieťaťa", ["dieta", "guid"])
    if dieta_guid is None:
        print("🛑 STOP – dieťa sa nepodarilo vytvoriť.")
        return

    # =====================================================================================
    # KROK 4 – REFRESH DETÍ
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieZoznamuDeti",
        {"guid": subjekt_guid, "lenPlatne": True},
        "KROK 4 – Refresh detí"
    )

    # =====================================================================================
    # KROK 5 – DETAIL DIEŤAŤA
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieUdajovDietata",
        {"guid": dieta_guid},
        "KROK 5 – Detail dieťaťa"
    )

    # =====================================================================================
    # KROK 6 – KONCEPT KROK 1
    # =====================================================================================
    resp_k1 = http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid),
        "KROK 6 – Koncept krok 1"
    )

    prihlaska_guid = safe_extract(resp_k1, "GUID prihlášky", ["prihlaska", "prihlaskaGUID"])
    if prihlaska_guid is None:
        print("🛑 STOP – GUID prihlášky chýba.")
        return

    # =====================================================================================
    # DYNAMICKÝ REFERER pre všetky vyhľadávania
    # =====================================================================================
    dyn_ref = f"{HOST}/Prihlaska?typSaSZ=ZS&guid={prihlaska_guid}"
    http.set_referer(dyn_ref)

    # =====================================================================================
    # KROK 7 – KONCEPT 2
    # =====================================================================================
    http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_2(dieta_guid, prihlaska_guid),
        "KROK 7 – Koncept krok 2"
    )

    # =====================================================================================
    # KROK 8 – OBĽÚBENÉ ZŠ
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs(prihlasena_osoba_guid),
        "KROK 8 – Obľúbené ZŠ"
    )

    # =====================================================================================
    # KROK 9 – FILTROVANIE ZŠ (EXTENDED)
    # =====================================================================================
    http.post_extended_scenario(
        "/api/vrateniePoloziekFiltrov",
        {"skolskyRokKod": "2026/2027", "ms": False, "zs": True},
        "KROK 9 – Filtrovanie ZŠ"
    )

    # =====================================================================================
    # KROK 10 – VYHĽADÁVANIE ADRESY
    # =====================================================================================
    http.get_scenario(
        "/api/search",
        {"text": "Bratislava 2, Bratislava", "_": "123123123"},
        "KROK 10 – Vyhľadávanie adresy"
    )

    # =====================================================================================
    # KROKY 11–22 – VYHĽADÁVANIA
    # =====================================================================================
    print("🔍 Spúšťam vyhľadávacie kroky 11–22...")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_base_payload(20), "KROK 11 – base 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_base_payload(100000), "KROK 12 – base 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(20), "KROK 13 – slovensky 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_slovak_payload(100000), "KROK 14 – slovensky 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_statne_payload(20), "KROK 17 – štátne 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_statne_payload(100000), "KROK 18 – štátne 100k")

    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(20), "KROK 19 – typy 20")
    http.post_extended_scenario("/api/vyhladanieMSaZS", search_typy_payload(100000), "KROK 20 – typy 100k")

    # =====================================================================================
    # KROK 23 – OBĽÚBENÉ
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs(prihlasena_osoba_guid),
        "KROK 23 – Obľúbené ZŠ"
    )

    # =====================================================================================
    # KROK 24 – PRIDANIE OBĽÚBENEJ ŠKOLY
    # =====================================================================================
    http.post_scenario(
        "/api/zapisOblubenychSaSZ",
        payload_add_favorite_school(prihlasena_osoba_guid),
        "KROK 24 – Pridanie obľúbenej školy"
    )

    # =====================================================================================
    # KROK 25 – REFRESH OBĽÚBENÝCH
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs(prihlasena_osoba_guid),
        "KROK 25 – Refresh obľúbených"
    )

    # =====================================================================================
    # KROK 26 – KONCEPT KROK 3 (VÝBER ŠKOLY)
    # =====================================================================================
    http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_3(dieta_guid, prihlaska_guid),
        "KROK 26 – Koncept krok 3"
    )

    # =====================================================================================
    # KROK 27 – VYBRANÉ ŠKOLY
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieVybranychSaSZ",
        {"prihlaskaGUID": prihlaska_guid},
        "KROK 27 – Vybrané školy"
    )

    # =====================================================================================
    # KROK 28 – KONCEPT KROK 4
    # =====================================================================================
    http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_4(dieta_guid, prihlaska_guid),
        "KROK 28 – Koncept krok 4"
    )

    # =====================================================================================
    # KROK 29 – KONCEPT KROK 5
    # =====================================================================================
    http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_5(dieta_guid, prihlaska_guid),
        "KROK 29 – Koncept krok 5"
    )

    # =====================================================================================
    # KROK 30 – DETAIL KONCEPTU
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid},
        "KROK 30 – Kontrola konceptu"
    )

    # =====================================================================================
    # KROK 31 – FINÁLNA KONTROLA KONCEPTU
    # =====================================================================================
    http.post_scenario(
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid},
        "KROK 31 – Finálna kontrola"
    )

    print(f"🏁 User {user.user_id}: ZŠ scenár dokončený.")
