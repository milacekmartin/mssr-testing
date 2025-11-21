import sys, os, json, requests
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from config.settings import HOST, CSRF, COOKIE_BUNDLE, IAM_TOKEN
from config.settings import SUBJEKT_GUID
from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload


# ================================================================
# RAW POST – lokálne, nech to funguje bez common.py
# ================================================================
def post_raw(context, endpoint, payload):
    url = f"{HOST}{endpoint}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": HOST + "/",
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "RequestVerificationToken": CSRF,
        "X-Token-Descriptor": IAM_TOKEN,
        "Cookie": COOKIE_BUNDLE
    }

    print(f"[{context}] POST {endpoint}")
    resp = requests.post(url, json=payload, headers=headers)
    print(f"[{context}] → {resp.status_code}")
    return resp


# ================================================================
# GUID extract
# ================================================================
def child_guid_from_response(resp_json):
    try:
        return resp_json.get("dieta", {}).get("guid")
    except:
        return None


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ================================================================
# NEGATIVE TEST DEFINITIONS (rozšírené o všetky povinné polia)
# ================================================================
NEGATIVE_TESTS = [

    # už existujúce
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

    # ---- NOVÉ povinné polia (empty) ----
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


# ================================================================
# MAIN
# ================================================================
def main():

    summary = []

    # ======================================================
    # VALID TEST
    # ======================================================
    print_header("VALID-CREATE-CHILD")

    first, last = generate_random_name()
    print(f"➡️ Vytváram dieťa: {first} {last}")

    valid_payload = build_base_child_payload(first, last)

    resp = post_raw("VALID-CREATE-CHILD", "/api/zapisAModifikaciaDietata", valid_payload)

    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        pass

    guid = child_guid_from_response(resp_json)

    if resp.status_code == 200 and guid:
        print("✔️ VALID TEST PASSED — GUID nájdený:", guid)
        summary.append(("VALID", "PASS"))
    else:
        print("⚠️ VALID FAILED — GUID nenájdený")
        summary.append(("VALID", "FAIL"))
        print("📥 RESPONSE:", resp.text)

    # ======================================================
    # NEGATIVE TESTS
    # ======================================================
    for test_name, patch in NEGATIVE_TESTS:

        print_header(test_name)

        # 1) nový payload
        first, last = generate_random_name()
        payload = build_base_child_payload(first, last)

        # 2) patch
        for k, v in patch.items():
            print(f"🔧 mením: {k} → {v}")
            payload[k] = v

        # 3) send
        resp = post_raw(test_name, "/api/zapisAModifikaciaDietata", payload)

        # očakávané: != 200 → PASS
        if resp.status_code != 200:
            print(f"✔️ NEGATIVE PASSED — očakávaný status {resp.status_code}")
            summary.append((test_name, "PASS"))
        else:
            print(f"❌ NEGATIVE FAILED — server vrátil 200 (nemal!)")
            summary.append((test_name, "FAIL"))

        print("📥 RESPONSE:", resp.text)

    # ======================================================
    # SUMMARY (with green/red icons)
    # ======================================================
    print_header("SUMMARY")

    print(f"{'TEST NAME':30} | RESULT")
    print("-" * 45)

    ICON = {
        "PASS": "🟢",
        "FAIL": "🔴"
    }

    for name, result in summary:
        print(f"{name:30} | {ICON[result]}")

    print("\n🏁 HOTOVO.\n")


if __name__ == "__main__":
    main()
