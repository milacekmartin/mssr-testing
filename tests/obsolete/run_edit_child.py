# locust/tests/child/run_edit_child.py

import sys, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from tests.common import send_post, send_get
from tests.child.payloads.child import build_child_payload
from config.random_names import generate_random_name
from config.settings import SUBJEKT_GUID


def main():
    print("\n============================================================")
    print("EDIT-CHILD")
    print("============================================================")

    #
    # 1) CREATE CHILD
    #
    first, last = generate_random_name()
    payload = build_child_payload(first, last)

    print(f"\n➡️ Creating child: {first} {last}")
    create_resp = send_post("EDIT-CREATE", "/api/zapisAModifikaciaDietata", payload)
    create_json = create_resp.json()

    # API niekedy vracia GUID v rôznych štruktúrach
    guid = (
        create_json.get("dieta", {}).get("guid")
        or create_json.get("guid")
        or None
    )

    if not guid:
        print("❌ CREATE FAILED — GUID nie je v response")
        print("📥 RESPONSE:", create_resp.text)
        return

    print(f"✔️ Created GUID: {guid}")

    #
    # 2) EDIT CHILD
    #
    new_first, new_last = generate_random_name()
    payload = build_child_payload(new_first, new_last)
    payload["dietaGUID"] = guid
    payload["pohlavieKod"] = "2"  # female

    print(f"\n➡️ Editing child → {new_first} {new_last}")
    edit_resp = send_post("EDIT-UPDATE", "/api/zapisAModifikaciaDietata", payload)

    print(f"[EDIT-UPDATE] → {edit_resp.status_code}")
    print("📥 RESPONSE:", edit_resp.text)

    #
    # 3) VERIFY UPDATE
    #
    print("\n➡️ Reading child list to verify update…")

    verify_payload = {
        "guid": SUBJEKT_GUID,
        "lenPlatne": True
    }

    list_resp = send_post(
        "EDIT-VERIFY",
        "/api/vratenieZoznamuDeti",
        verify_payload
    )

    if list_resp.status_code != 200:
        print(f"❌ TEST FAILED – /api/vratenieZoznamuDeti returned {list_resp.status_code}")
        print("Response:")
        print(list_resp.text)
        return

    list_json = list_resp.json()

    deti = list_json.get("dieta", [])
    found = next((d for d in deti if d.get("guid") == guid), None)

    if not found:
        print("❌ EDIT FAILED — child not found in list")
        return

    if found.get("meno") == new_first and found.get("priezvisko") == new_last:
        print("✔️ EDIT PASSED — údaje sú aktualizované")
    else:
        print("❌ EDIT FAILED — údaje sa nezhodujú")
        print("Nájdené:", found)

    #
    # 4) DELETE CHILD
    #
    print("\n➡️ Deleting child…")
    del_resp = send_post("EDIT-DELETE", "/api/vymazDietata", {"guid": guid})

    print(f"[DELETE] → {del_resp.status_code}")
    print("📥 RESPONSE:", del_resp.text)

    print("\n🏁 EDIT FLOW DONE\n")


if __name__ == "__main__":
    main()
