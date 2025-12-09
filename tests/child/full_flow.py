# locust/tests/child/run_edit_child.py

import sys, os, json, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload
from config.env import HOST


CTX = "CHILD-EDIT-FLOW"


# ============================================================
# SEND POST with tokens
# ============================================================
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


# ============================================================
# MAIN
# ============================================================
def main():
    # CLI ARGUMENTS
    parser = argparse.ArgumentParser(description="Child edit test flow")
    parser.add_argument(
        "--show-data",
        action="store_true",
        help="Show full request and response JSON payloads"
    )
    args = parser.parse_args()
    SHOW_DATA = args.show_data

    print("\n=====================================================")
    print(" CHILD EDIT FLOW – CREATE → UPDATE → VERIFY → DELETE")
    print("=====================================================\n")

    # LOGIN
    login = saml_login()
    print("✔️ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    subjekt_guid = login.subj_guid

    #
    # 1) CREATE CHILD
    #
    first, last = generate_random_name()
    payload = build_base_child_payload(first, last)
    payload["subjektGUID"] = subjekt_guid

    print(f"\n➡️ Creating child: {first} {last}")
    create_resp = send_post(login, "EDIT-CREATE", "/api/zapisAModifikaciaDietata", payload, SHOW_DATA)

    try:
        create_json = create_resp.json()
    except:
        print("❌ CREATE FAILED — server nevrátil JSON")
        print("Response:", create_resp.text)
        return

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
    edit_payload = build_base_child_payload(new_first, new_last)
    edit_payload["subjektGUID"] = subjekt_guid
    edit_payload["dietaGUID"] = guid
    edit_payload["pohlavieKod"] = "2"  # female

    print(f"\n➡️ Editing child → {new_first} {new_last}")
    edit_resp = send_post(login, "EDIT-UPDATE", "/api/zapisAModifikaciaDietata", edit_payload, SHOW_DATA)

    print(f"[EDIT-UPDATE] → {edit_resp.status_code}")
    if not SHOW_DATA:
        print("📥 RESPONSE:", edit_resp.text[:300])

    #
    # 3) VERIFY UPDATE
    #
    print("\n➡️ Reading child list to verify update…")

    verify_payload = {
        "guid": subjekt_guid,
        "lenPlatne": True
    }

    list_resp = send_post(login, "EDIT-VERIFY", "/api/vratenieZoznamuDeti", verify_payload, SHOW_DATA)

    if list_resp.status_code != 200:
        print(f"❌ VERIFY FAILED – /api/vratenieZoznamuDeti returned {list_resp.status_code}")
        print("Response:", list_resp.text)
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
    del_resp = send_post(login, "EDIT-DELETE", "/api/vymazDietata", {"guid": guid}, SHOW_DATA)

    print(f"[DELETE] → {del_resp.status_code}")
    if not SHOW_DATA:
        print("📥 RESPONSE:", del_resp.text[:300])

    print("\n🏁 EDIT FLOW DONE\n")


if __name__ == "__main__":
    main()
