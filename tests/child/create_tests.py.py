# tests/child/run_create_child.py

import sys, os, json, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.env import HOST
from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

CTX = "CHILD-FLOW"


# ============================================================
# NEGATIVE TEST DEFINITIONS – komplet zoznam
# ============================================================
NEGATIVE_TESTS = [

    # pôvodné testy
    ("NEG-EMPTY-NAME",              {"meno": ""}),
    ("NEG-EMPTY-LASTNAME",          {"priezvisko": ""}),
    ("NEG-INVALID-DATE",            {"datumNarodenia": "2020-33-99"}),
    ("NEG-NONNUMERIC-PSC",          {"tppsc": "ABCDE"}),
    ("NEG-NONNUMERIC-SUPISNE",      {"tpSupisneCislo": "XYZ"}),
    ("NEG-INVALID-GENDER",          {"pohlavieKod": "99"}),
    ("NEG-INVALID-NARODNOST",       {"narodnostKod": "999"}),
    ("NEG-NONE-MIESTO",             {"miestoNarodenia": ""}),
    ("NEG-LONG-MENO",               {"meno": "A"*300}),
    ("NEG-LONG-PRIEZVISKO",         {"priezvisko": "B"*300}),

    # NOVÉ povinné polia (empty)
    ("NEG-EMPTY-DATE",              {"datumNarodenia": ""}),
    ("NEG-EMPTY-GENDER",            {"pohlavieKod": ""}),
    ("NEG-EMPTY-NARODNOST",         {"narodnostKod": ""}),
    ("NEG-EMPTY-STATNA-PRISL",      {"statnaPrislusnost": []}),
    ("NEG-EMPTY-MAT-JAZYK",         {"materinskyJazykKod": ""}),

    ("NEG-EMPTY-TP-STAT",           {"tpStatKod": ""}),
    ("NEG-EMPTY-TP-OBC",            {"tpObecKod": ""}),
    ("NEG-EMPTY-TP-SUPISNE",        {"tpSupisneCislo": ""}),
    ("NEG-EMPTY-TP-PSC",            {"tppsc": ""}),

    ("NEG-EMPTY-ZP-STAT",           {"zpStatKod": ""}),
    ("NEG-EMPTY-ZP-OBC",            {"zpObecKod": ""}),
    ("NEG-EMPTY-ZP-SUPISNE",        {"zpSupisneCislo": ""}),
    ("NEG-EMPTY-ZP-PSC",            {"zppsc": ""}),
]


# ============================================================
# SEND POST with tokens
# ============================================================
def send_post(login, endpoint, payload, show_data=False):
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

    print(f"[{CTX}] POST {endpoint}")

    if show_data:
        print("\n📤 REQUEST PAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    resp = login.session.post(url, json=payload, headers=headers)
    print(f"[{CTX}] → {resp.status_code}")

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
    parser = argparse.ArgumentParser(description="Child negative tests")
    parser.add_argument("--show-data", action="store_true",
                       help="Show request payloads and responses")
    args = parser.parse_args()
    SHOW_DATA = args.show_data

    print("\n==========================================")
    print(" CHILD RECORD VALIDATION & NEGATIVE TESTS")
    print("==========================================\n")

    # LOGIN cez nový modul
    login = saml_login()
    print("✔️ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    summary = []

    # ======================================================
    # VALID CREATE TEST
    # ======================================================
    first, last = generate_random_name()
    print(f"\n➡️ Vytváram VALID dieťa: {first} {last}")

    payload = build_base_child_payload(first, last)
    payload["subjektGUID"] = login.subj_guid

    resp = send_post(login, "/api/zapisAModifikaciaDietata", payload, SHOW_DATA)

    # VALID RESULT EVALUATION
    try:
        resp_json = resp.json()
    except:
        print("❌ VALID FAILED — server nevrátil JSON")
        print("📥 RESPONSE:", resp.text)
        summary.append(("VALID", "FAIL"))
        return

    kod = resp_json.get("kodSpracovania")
    guid = (
        resp_json.get("dieta", {}).get("guid")
        or resp_json.get("guid")
    )

    # SUCCESS = kod==1700 AND guid exists
    if resp.status_code == 200 and kod == "1700" and guid:
        print("✔️ VALID PASSED")
        summary.append(("VALID", "PASS"))
    else:
        print("❌ VALID FAILED")
        print(f"Status: {resp.status_code}")
        print(f"kodSpracovania: {kod}")
        print(f"guid: {guid}")
        print("📥 RESPONSE:", json.dumps(resp_json, indent=2, ensure_ascii=False))

        summary.append(("VALID", "FAIL"))
        return


    if not SHOW_DATA:
        print("📥 RESPONSE:", resp.text[:300])

    # ======================================================
    # NEGATIVE TESTS
    # ======================================================
    for name, patch in NEGATIVE_TESTS:

        print("\n==============================")
        print(name)
        print("==============================")

        f, l = generate_random_name()
        test_payload = build_base_child_payload(f, l)
        test_payload["subjektGUID"] = login.subj_guid

        # Apply patch
        for key, value in patch.items():
            print(f"🔧 mením: {key} → {value}")
            test_payload[key] = value

        resp = send_post(login, "/api/zapisAModifikaciaDietata", test_payload, SHOW_DATA)

        if resp.status_code != 200:
            print("✔️ NEGATIVE PASSED — očakávaný ne-200")
            summary.append((name, "PASS"))
        else:
            print("❌ NEGATIVE FAILED — server vrátil 200 (nemal!)")
            summary.append((name, "FAIL"))

        if not SHOW_DATA:
            print("📥 RESPONSE:", resp.text[:300])

    # ======================================================
    # SUMMARY
    # ======================================================
    print("\n=========== SUMMARY ===========")
    for name, status in summary:
        mark = "🟢" if status == "PASS" else "🔴"
        print(f"{name:30} {mark}")


if __name__ == "__main__":
    main()
