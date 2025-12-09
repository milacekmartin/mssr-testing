import sys, os, json, re, html, requests
from bs4 import BeautifulSoup
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from config.settings import HOST
from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

# ==============================
# PRIHLASOVACIE UDÁJE
# ==============================
USERNAME = "martin.milacek@professional-test-automation.com"
PASSWORD = "Initial0!"
ACS_URL = f"{HOST}/assertionconsumerservice"

CTX = "CHILD-FLOW"

# Global dynamic tokens
session = None
dynamic_csrf = None
dynamic_token_descriptor = None
dynamic_cookie_bundle = None
dynamic_subjekt_guid = None
dynamic_prihlasena_osoba_guid = None

# Global flag pre zobrazenie dat
SHOW_DATA = False


# ============================================================
# SAML LOGIN (rovnaký ako run_zs_prihlaska.py)
# ============================================================
def saml_login():
    global session, dynamic_csrf, dynamic_token_descriptor, dynamic_cookie_bundle
    global dynamic_subjekt_guid, dynamic_prihlasena_osoba_guid

    print("🔐 Spúšťam SAML login…")

    session = requests.Session()

    # 1) GET /loginosoba → redirect
    r1 = session.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)
    redirect1 = r1.headers.get("Location")

    # 2) GET redirect1 → ďalší redirect
    r2 = session.get(redirect1, allow_redirects=False)
    redirect2 = r2.headers.get("Location")
    if not redirect2.startswith("http"):
        redirect2 = "https://tiamidsk.iedu.sk" + redirect2

    # 3) GET TIAM login page
    r3 = session.get(redirect2, allow_redirects=False)
    html3 = r3.text

    # Niekedy TIAM zobrazí "Vyberte spôsob prihlásenia"
    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        chooser = f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}"
        r3 = session.get(chooser, allow_redirects=False)
        html3 = r3.text

    # Extract AuthnGuid + CSRF
    authn_guid = re.search(r'name="AuthnGuid"[^>]+value="([^"]+)"', html3).group(1)
    request_ver_token = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html3).group(1)

    # 4) POST credentials to TIAM
    r4 = session.post(
        "https://tiamidsk.iedu.sk/authn/lp",
        data={
            "AuthnGuid": authn_guid,
            "UserName": USERNAME,
            "UserPassword": PASSWORD,
            "btn-continue": "Prihlásiť sa",
            "__RequestVerificationToken": request_ver_token,
        },
        allow_redirects=False,
    )

    redirect3 = r4.headers.get("Location")
    if not redirect3.startswith("http"):
        redirect3 = "https://tiamidsk.iedu.sk" + redirect3

    # 5) GET SAMLResponse page
    r5 = session.get(redirect3, allow_redirects=False)
    soup = BeautifulSoup(r5.text, "html.parser")

    saml_raw = soup.find("input", {"name": "SAMLResponse"}).get("value")
    relay = soup.find("input", {"name": "RelayState"}).get("value")
    saml_decoded = html.unescape(saml_raw)

    # 6) POST SAMLResponse to ePrihlášky
    acs = session.post(
        ACS_URL,
        data={
            "RelayState": relay,
            "SAMLResponse": saml_decoded,
        },
        allow_redirects=False,
    )

    # 7) Load homepage to finalize login
    home = session.get(acs.headers["Location"])

    # 8) GET Moj-profil2 → extrakcia tokenov
    profile = session.get(f"{HOST}/Moj-profil2")
    html_profile = profile.text

    # CSRF
    m_csrf = re.search(
        r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html_profile
    )
    global dynamic_csrf
    dynamic_csrf = m_csrf.group(1) if m_csrf else None

    # userData JSON
    m_user = re.search(
        r"window\.userData\s*=\s*(\{.*?\});", html_profile, re.DOTALL
    )
    userdata = json.loads(m_user.group(1)) if m_user else {}

    global dynamic_token_descriptor, dynamic_subjekt_guid, dynamic_prihlasena_osoba_guid
    dynamic_token_descriptor = userdata.get("tokenDescriptor")
    person = userdata.get("person", {})
    dynamic_subjekt_guid = person.get("subjectGuid")
    dynamic_prihlasena_osoba_guid = person.get("loggedInPersonGuid")

    # Cookies
    important = [
        "IamTokenDescriptor",
        "_DS",
        "_DSA",
        "_DC",
        ".AspNetCore.Antiforgery.UaYXyBoyr8Q",
        ".AspNetCore.Antiforgery.fAr6xnvBhu0",
        "IamWeb",
        "culture",
        "Balanced_and_Offloaded",
        "cookies-warning",
        "last_non_error_path",
    ]

    parts = []
    for cookie in session.cookies:
        if cookie.name in important:
            parts.append(f"{cookie.name}={cookie.value}")

    global dynamic_cookie_bundle
    dynamic_cookie_bundle = "; ".join(parts)

    return all(
        [
            dynamic_csrf,
            dynamic_token_descriptor,
            dynamic_subjekt_guid,
            dynamic_prihlasena_osoba_guid,
        ]
    )


# ============================================================
# SEND POST with dynamic tokens
# ============================================================
def send_post_with_tokens(ctx, endpoint, payload):
    url = f"{HOST}{endpoint}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Moj-profil2",
        "RequestVerificationToken": dynamic_csrf,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "x-token-descriptor": dynamic_token_descriptor,
        "Cookie": dynamic_cookie_bundle,
    }

    print(f"[{ctx}] POST {endpoint}")
    
    if SHOW_DATA:
        print("\n📤 REQUEST PAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    resp = session.post(url, json=payload, headers=headers)
    print(f"[{ctx}] → {resp.status_code}")
    
    if SHOW_DATA:
        print("\n📥 RESPONSE:")
        try:
            response_json = resp.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(resp.text)
        print()
    
    return resp


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
# MAIN
# ============================================================
def main():
    # Parse argumentov
    parser = argparse.ArgumentParser(description="Child negative tests")
    parser.add_argument("--show-data", action="store_true", 
                       help="Show request payloads and responses")
    args = parser.parse_args()
    
    global SHOW_DATA
    SHOW_DATA = args.show_data

    print("\n====================================")
    print(" CHILD NEGATIVE TESTS – DYNAMIC LOGIN")
    print("====================================\n")

    # LOGIN
    if not saml_login():
        print("❌ LOGIN FAILED!")
        return

    print("✔️ Login OK")
    print("Subjekt GUID:", dynamic_subjekt_guid)
    print("Prihl. osoba GUID:", dynamic_prihlasena_osoba_guid)

    summary = []

    # ======================================================
    # VALID CREATE TEST
    # ======================================================
    first, last = generate_random_name()
    print(f"\n➡️ Vytváram VALID dieťa: {first} {last}")

    payload = build_base_child_payload(first, last)
    # ak payload ešte nemá subjektGUID, doplníme
    if "subjektGUID" not in payload:
        payload["subjektGUID"] = dynamic_subjekt_guid

    resp = send_post_with_tokens(CTX, "/api/zapisAModifikaciaDietata", payload)

    if resp.status_code == 200:
        print("✔️ VALID PASSED")
        summary.append(("VALID", "PASS"))
    else:
        print("❌ VALID FAILED")
        summary.append(("VALID", "FAIL"))

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
        p = build_base_child_payload(f, l)

        # doplníme subjektGUID, ak chýba
        if "subjektGUID" not in p:
            p["subjektGUID"] = dynamic_subjekt_guid

        # patch
        for k, v in patch.items():
            print(f"🔧 mením: {k} → {v}")
            p[k] = v

        resp = send_post_with_tokens(CTX, "/api/zapisAModifikaciaDietata", p)

        # očakávané: != 200 → PASS
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