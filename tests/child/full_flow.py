# tests/child/full_flow.py
# ======================================================
# CHILD – FULL FLOW
# ======================================================

import sys, os, json, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.random_names import generate_random_name
from config.env import HOST
from utils.http import build_headers
from tests.child.payloads.child import build_base_child_payload

CTX = "CHILD"


NEGATIVE_TESTS = [
    ("EMPTY NAME", {"meno": ""}),
    ("EMPTY LASTNAME", {"priezvisko": ""}),
    ("INVALID DATE", {"datumNarodenia": "2020-99-99"}),
]


# ======================================================
def post(login, endpoint, payload, show=False):
    url = f"{HOST}{endpoint}"
    r = login.session.post(url, json=payload, headers=build_headers(login))

    if show:
        print("📤 REQUEST:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("📥 RESPONSE:")
        try:
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        except:
            print(r.text)

    return r


# ======================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-data", action="store_true")
    args = parser.parse_args()

    print("\n=====================================================")
    print(" CHILD – FULL FLOW")
    print("=====================================================\n")

    # LOGIN
    login = saml_login()
    print("   • Subjekt GUID:", login.subj_guid)
    print("   • User GUID:", login.logged_guid)

    # --------------------------------------------------
    # STEP 1 – CREATE
    # --------------------------------------------------
    first, last = generate_random_name()
    payload = build_base_child_payload(first, last)
    payload["subjektGUID"] = login.subj_guid

    r = post(login, "/api/zapisAModifikaciaDietata", payload, args.show_data)
    data = r.json()
    guid = data.get("dieta", {}).get("guid")

    if not guid:
        print("\n❌ STEP 1 FAILED")
        return

    print("\n📘 STEP 1 – create child")
    print(f"   • meno: {first} {last}")
    print(f"   • GUID: {guid}")

    # --------------------------------------------------
    # STEP 2 – UPDATE
    # --------------------------------------------------
    new_first, new_last = generate_random_name()
    payload = build_base_child_payload(new_first, new_last)
    payload["subjektGUID"] = login.subj_guid
    payload["dietaGUID"] = guid
    payload["pohlavieKod"] = "2"

    post(login, "/api/zapisAModifikaciaDietata", payload, args.show_data)

    print("\n📘 STEP 2 – update child")
    print(f"   • meno: {new_first} {new_last}")
    print("   • pohlavie: žena")

    # --------------------------------------------------
    # STEP 3 – VERIFY
    # --------------------------------------------------
    r = post(
        login,
        "/api/vratenieZoznamuDeti",
        {"guid": login.subj_guid, "lenPlatne": True},
        args.show_data,
    )

    found = next(
        (d for d in r.json().get("dieta", []) if d.get("guid") == guid),
        None
    )

    print("\n📘 STEP 3 – verify child")
    print("   • údaje:", "OK" if found else "FAILED")

    # --------------------------------------------------
    # STEP 4 – NEGATIVE
    # --------------------------------------------------
    print("\n📘 STEP 4 – negative validation")

    for name, patch in NEGATIVE_TESTS:
        payload = build_base_child_payload("Test", "Negativ")
        payload["subjektGUID"] = login.subj_guid
        payload.update(patch)

        r = post(login, "/api/zapisAModifikaciaDietata", payload)

        result = "rejected" if r.status_code != 200 else "FAILED"
        print(f"   • {name} → {result}")

    # --------------------------------------------------
    # STEP 5 – DELETE
    # --------------------------------------------------
    r = post(login, "/api/vymazDietata", {"guid": guid})

    print("\n📘 STEP 5 – delete child")
    print("   • status:", "OK" if r.status_code == 200 else "FAILED")

    print("\n✅ CHILD – FULL FLOW COMPLETED\n")


if __name__ == "__main__":
    main()
