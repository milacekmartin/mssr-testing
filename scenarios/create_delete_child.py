# scenarios/create_delete_child.py
# =================================
#
# Scenár:
#  1) vytvoriť dieťa
#  2) vymazať dieťa
#
# Používa safe_extract – ak GUID chýba → scenár končí a Locust ho označí ako FAIL.

import uuid

from config.random_names import generate_random_name
from payloads.dieta import create_dieta_payload
from scenarios.zs_prihlaska import safe_extract   # reuse safe extract
                                                   # (je univerzálne)

def run_create_delete_child(user, http):
    http.set_context("CREATE+DELETE")

    first, last = generate_random_name()
    print(f"🧒 [CREATE+DELETE] Generujem dieťa: {first} {last}")

    # 1. vytvorenie dieťaťa
    resp = http.post_scenario(
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last),
        "CREATE+DELETE – vytvorenie dieťaťa",
    )

    dieta_guid = safe_extract(
        resp,
        resp.json(),
        ["dieta", "guid"],
        "GUID dieťaťa",
    )

    if dieta_guid is None:
        print("🛑 CREATE+DELETE STOP – GUID dieťaťa chýba")
        return

    # 2. vymazanie dieťaťa
    http.post_scenario(
        "/api/vymazDietata",
        {"guid": dieta_guid},
        "CREATE+DELETE – vymazanie dieťaťa",
    )

    print("✔️ Dieťa bolo vytvorené aj zmazané.")