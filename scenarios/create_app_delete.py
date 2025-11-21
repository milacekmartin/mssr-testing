# scenarios/create_app_delete.py
# ================================
#
# Scenár:
#  1) vytvoriť dieťa
#  2) vytvoriť prihlášku (krok 1)
#  3) vymazať prihlášku
#  4) vymazať dieťa

import uuid

from config.random_names import generate_random_name
from payloads.dieta import create_dieta_payload
from payloads.prihlaska import koncept_krok_1

from scenarios.zs_prihlaska import safe_extract   # rovnaké safe_extract


def run_create_app_delete(user, http):
    http.set_context("CREATE-APP+DELETE")

    first, last = generate_random_name()
    print(f"📄 [CREATE-APP+DELETE] Generujem dieťa: {first} {last}")

    # 1. vytvorenie dieťaťa
    resp_dieta = http.post_scenario(
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last),
        "APP-FLOW – vytvorenie dieťaťa"
    )

    dieta_guid = safe_extract(
        resp_dieta,
        resp_dieta.json(),
        ["dieta", "guid"],
        "GUID dieťaťa"
    )
    
    if dieta_guid is None:
        print("🛑 APP-FLOW STOP – GUID dieťaťa chýba")
        return

    # 2. vytvorenie prihlášky
    resp_k1 = http.post_scenario(
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid),
        "APP-FLOW – vytvorenie prihlášky (krok 1)"
    )

    prihlaska_guid = safe_extract(
        resp_k1,
        resp_k1.json(),
        ["prihlaska", "prihlaskaGUID"],
        "GUID prihlášky"
    )
    
    if prihlaska_guid is None:
        print("🛑 APP-FLOW STOP – GUID prihlášky chýba")
        return

    # 3. mazanie prihlášky
    http.post_scenario(
        "/api/vymazPrihlasky",
        {"PrihlaskaGUID": prihlaska_guid},
        "APP-FLOW – mazanie prihlášky"
    )

    # 4. mazanie dieťaťa
    http.post_scenario(
        "/api/vymazDietata",
        {"guid": dieta_guid},
        "APP-FLOW – mazanie dieťaťa"
    )

    print("✔️ Dieťa + prihláška boli vytvorené a zmazané.")