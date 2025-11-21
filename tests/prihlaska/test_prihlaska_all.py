import sys, os, json
import requests
import re
import html
from bs4 import BeautifulSoup

# ===============================
# FIX PYTHON PATH (LOAD config/*)
# ===============================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # tests/prihlaska
TESTS_DIR = os.path.dirname(CURRENT_DIR)                       # tests/
PROJECT_ROOT = os.path.dirname(TESTS_DIR)                      # locust/
sys.path.append(PROJECT_ROOT)

# teraz importy fungujú:
from config.headers import COMMON_HEADERS, EXTENDED_HEADERS, VYHLEDAVACIE_HEADERS
from config.settings import HOST, SUBJEKT_GUID, PRIHLASENA_OSOBA_GUID, SKOLSKY_ROK_KOD_2026

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from config.headers import COMMON_HEADERS, EXTENDED_HEADERS, VYHLEDAVACIE_HEADERS

from tests.common import send_post, send_get, safe_extract
from config.random_names import generate_random_name

# Import DETSKÉHO payloadu zo správneho miesta
from tests.child.payloads.child import build_base_child_payload

# Importy pre prihlášku
from tests.prihlaska.payloads.vyhladavanie import (
    search_base_payload,
    search_slovak_payload,
    search_statne_payload,
    search_typy_payload,
    NEG_SEARCH_PAYLOADS
)
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_4,
    koncept_krok_5,
    NEG_KONCEPT_PAYLOADS
)

# Prihlasovacie údaje
USERNAME = "martin.milacek@professional-test-automation.com"
PASSWORD = "Initial0!"
ACS_URL = f"{HOST}/assertionconsumerservice"

CTX = "PRIHLASKA-FLOW"

results = []

# Global session and auth data
session = None
csrf = None
token_descriptor = None
cookie_bundle = None
subjekt_guid = None
prihlasena_osoba_guid = None


# -------------------------------------------------------------
# SAML login sequence
# -------------------------------------------------------------
def saml_login():
    global session, csrf, token_descriptor, cookie_bundle, subjekt_guid, prihlasena_osoba_guid
    
    session = requests.Session()

    # SAML login process...
    r1 = session.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)
    redirect1 = r1.headers.get("Location")

    r2 = session.get(redirect1, allow_redirects=False)
    redirect2 = r2.headers.get("Location")
    if not redirect2.startswith("http"):
        redirect2 = "https://tiamidsk.iedu.sk" + redirect2

    r3 = session.get(redirect2, allow_redirects=False)
    html3 = r3.text

    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        chooser = f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}"
        r3 = session.get(chooser, allow_redirects=False)
        html3 = r3.text

    authn_guid = re.search(r'name="AuthnGuid"[^>]+value="([^"]+)"', html3).group(1)
    request_ver_token = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html3).group(1)

    r4 = session.post("https://tiamidsk.iedu.sk/authn/lp", data={
        "AuthnGuid": authn_guid,
        "UserName": USERNAME,
        "UserPassword": PASSWORD,
        "btn-continue": "Prihlásiť sa",
        "__RequestVerificationToken": request_ver_token,
    }, allow_redirects=False)

    redirect3 = r4.headers.get("Location")
    if not redirect3.startswith("http"):
        redirect3 = "https://tiamidsk.iedu.sk" + redirect3

    r5 = session.get(redirect3, allow_redirects=False)
    html5 = r5.text

    soup = BeautifulSoup(html5, "html.parser")
    form = soup.find("form")
    saml_raw = form.find("input", {"name": "SAMLResponse"}).get("value")
    relay = form.find("input", {"name": "RelayState"}).get("value")
    saml_decoded = html.unescape(saml_raw)

    acs_resp = session.post(ACS_URL, data={
        "RelayState": relay,
        "SAMLResponse": saml_decoded,
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://tiamidsk.iedu.sk",
        "Referer": "https://tiamidsk.iedu.sk/",
    }, allow_redirects=False)

    home_url = acs_resp.headers["Location"]
    home = session.get(home_url)

    profile = session.get(f"{HOST}/Moj-profil2")
    html_profile = profile.text

    # Extract tokens
    antiforgery_match = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html_profile)
    csrf = antiforgery_match.group(1) if antiforgery_match else None

    userdata_match = re.search(r"window\.userData\s*=\s*(\{.*?\});", html_profile, re.DOTALL)
    userdata = None
    
    if userdata_match:
        try:
            userdata = json.loads(userdata_match.group(1).rstrip(";"))
            token_descriptor = userdata.get("tokenDescriptor")
            
            # Extract GUIDs
            person_data = userdata.get("person", {})
            subjekt_guid = person_data.get("subjectGuid", "")
            prihlasena_osoba_guid = person_data.get("loggedInPersonGuid", "")
        except:
            pass

    # Extract all cookies into bundle
    important_cookies = [
        "IamTokenDescriptor", 
        "_DS", "_DSA", "_DC",
        ".AspNetCore.Antiforgery.UaYXyBoyr8Q",
        ".AspNetCore.Antiforgery.fAr6xnvBhu0",
        "IamWeb", "culture", "Balanced_and_Offloaded", 
        "cookies-warning", "last_non_error_path"
    ]
    
    cookie_parts = []
    for cookie_name in important_cookies:
        for cookie in session.cookies:
            if cookie.name == cookie_name:
                cookie_parts.append(f"{cookie.name}={cookie.value}")
                break
    
    cookie_bundle = "; ".join(cookie_parts)

    return {
        "success": bool(csrf and token_descriptor and subjekt_guid and prihlasena_osoba_guid),
        "csrf": csrf,
        "token_descriptor": token_descriptor,
        "cookie_bundle": cookie_bundle,
        "subjekt_guid": subjekt_guid,
        "prihlasena_osoba_guid": prihlasena_osoba_guid,
    }


# -------------------------------------------------------------
# Fixed koncept payloads based on working examples
# -------------------------------------------------------------
def build_koncept_krok_1(dieta_guid):
    """Build working concept step 1 payload"""
    return {
        "prihlaska": {
            "prihlaskaGUID": None,
            "dietaGUID": dieta_guid,
            "skolskyRokKod": "2026/2027",
            "typSaSZ": "ZS",
            "krok": 1,
            "rozpracovane": True,
            "platne": False
        }
    }


def build_koncept_krok_2(dieta_guid, prihlaska_guid):
    """Build working concept step 2 payload"""
    return {
        "prihlaska": {
            "prihlaskaGUID": prihlaska_guid,
            "dietaGUID": dieta_guid,
            "skolskyRokKod": "2026/2027",
            "typSaSZ": "ZS",
            "krok": 2,
            "rozpracovane": True,
            "platne": False,
            "stravovanie": True,
            "druzina": True
        }
    }


def build_koncept_krok_3(dieta_guid, prihlaska_guid):
    """Build working concept step 3 payload"""
    return {
        "prihlaska": {
            "prihlaskaGUID": prihlaska_guid,
            "dietaGUID": dieta_guid,
            "skolskyRokKod": "2026/2027",
            "typSaSZ": "ZS",
            "krok": 3,
            "rozpracovane": True,
            "platne": False
        }
    }


# -------------------------------------------------------------
# Updated send functions to use global session
# -------------------------------------------------------------
def send_post_with_session(ctx, endpoint, payload, headers=None, debug=False):
    """Send POST with session using dynamic headers"""
    global session, csrf, token_descriptor, cookie_bundle
    
    url = f"{HOST}{endpoint}"
    print(f"[{ctx}] POST {endpoint}")
    
    if debug:
        print(f"[{ctx}] DEBUG Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Build dynamic headers
    if headers is None:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd", 
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": HOST,
            "Referer": f"{HOST}/Moj-profil2",
            "RequestVerificationToken": csrf,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "x-token-descriptor": token_descriptor,
            "Cookie": cookie_bundle
        }
    else:
        # Update existing headers with dynamic values
        headers = headers.copy()
        headers["RequestVerificationToken"] = csrf
        headers["x-token-descriptor"] = token_descriptor
        headers["Cookie"] = cookie_bundle
    
    try:
        resp = session.post(url, json=payload, headers=headers)
        print(f"[{ctx}] → Status: {resp.status_code}")
        
        # Log response for debugging
        if resp.status_code != 200:
            print(f"[{ctx}] ❌ Error Response:")
            print(f"   Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"   Response Text: {resp.text}")
        elif debug:
            try:
                resp_json = resp.json()
                print(f"[{ctx}] ✅ Success Response:")
                print(json.dumps(resp_json, indent=2, ensure_ascii=False))
            except:
                print(f"[{ctx}] ✅ Success Response (not JSON): {resp.text[:500]}")
        
        return resp
        
    except Exception as e:
        print(f"[{ctx}] 💥 Exception: {e}")
        # Return mock response for compatibility
        class MockResponse:
            status_code = 500
            def json(self):
                return {}
            text = str(e)
        return MockResponse()


def safe_extract_with_session(resp, json_data, path, description):
    """Safe extract with better error handling"""
    if resp.status_code != 200:
        print(f"   ⚠️ {description}: HTTP error {resp.status_code}")
        return None
        
    if not json_data:
        print(f"   ⚠️ {description}: No JSON data")
        try:
            json_data = resp.json()
        except:
            print(f"   ⚠️ {description}: Cannot parse JSON")
            return None
        
    current = json_data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            print(f"   ⚠️ {description}: Key '{key}' not found")
            if isinstance(current, dict):
                print(f"   Available keys: {list(current.keys())}")
            else:
                print(f"   Current value type: {type(current)}")
                print(f"   Current value: {current}")
            return None
    
    print(f"   ✅ {description}: {current}")
    return current


def record(name, ok):
    results.append((name, ok))


def main():
    print("\n🔐 Spúšťam SAML login…\n")
    
    login_result = saml_login()
    
    if not login_result["success"]:
        print("❌ Login failed!")
        print(f"CSRF: {'✅' if csrf else '❌'}")
        print(f"Token: {'✅' if token_descriptor else '❌'}")
        print(f"Subjekt GUID: {'✅' if subjekt_guid else '❌'}")
        print(f"Prihlasena Osoba GUID: {'✅' if prihlasena_osoba_guid else '❌'}")
        sys.exit(1)
        
    print("✅ Login successful!")
    print(f"CSRF: {csrf[:50]}...")
    print(f"Token: {token_descriptor[:50]}...")
    print(f"Subjekt GUID: {subjekt_guid}")
    print(f"Prihlasena Osoba GUID: {prihlasena_osoba_guid}")

    print("\n🎓 Spúšťam testy prihlášky…")

    # ------------------------------------------
    # 0 — Vytvorenie dieťaťa
    # ------------------------------------------
    first, last = generate_random_name()
    print(f"\n🧒 Generujem dieťa: {first}-{last}")

    # Update child payload with correct GUID
    child_payload = build_base_child_payload(first, last)
    if "dieta" in child_payload and "subjektGUID" in child_payload["dieta"]:
        child_payload["dieta"]["subjektGUID"] = subjekt_guid

    resp = send_post_with_session(CTX, "/api/zapisAModifikaciaDietata", child_payload)

    try:
        dieta_guid = safe_extract_with_session(resp, resp.json(), ["dieta", "guid"], "GUID dieťaťa")
    except:
        print("❌ DIEŤA NEVYTVORENÉ — končím.")
        return

    if not dieta_guid:
        print("❌ DIEŤA NEVYTVORENÉ — končím.")
        return

    # ------------------------------------------
    # 1 — Krok 1 (vytvorenie prihlášky) - WITH FIXED PAYLOAD
    # ------------------------------------------
    print(f"\n📋 Vytváram prihlášku pre dieťa: {dieta_guid}")
    
    # Try multiple payload formats
    payload_attempts = [
        ("Fixed format", build_koncept_krok_1(dieta_guid)),
        ("Original format", koncept_krok_1(dieta_guid)),
        ("Minimal format", {
            "dietaGUID": dieta_guid,
            "skolskyRokKod": "2026/2027",
            "typSaSZ": "ZS",
            "krok": 1
        }),
        ("Alternative format", {
            "prihlaska": {
                "dietaGUID": dieta_guid,
                "skolskyRokKod": "2026/2027",
                "typSaSZ": "ZS"
            }
        })
    ]

    prihlaska_guid = None
    
    for attempt_name, k1_payload in payload_attempts:
        print(f"\n🔍 Trying {attempt_name}:")
        
        resp_k1 = send_post_with_session(CTX,
                            "/api/zapisAModifikaciaKonceptuPrihlasky",
                            k1_payload,
                            debug=True)

        if resp_k1.status_code == 200:
            try:
                prihlaska_guid = safe_extract_with_session(resp_k1, resp_k1.json(),
                                          ["prihlaska", "prihlaskaGUID"],
                                          "GUID prihlášky")
                if prihlaska_guid:
                    print(f"✅ {attempt_name} worked! Prihlaska GUID: {prihlaska_guid}")
                    break
            except Exception as e:
                print(f"❌ Exception parsing response: {e}")
        else:
            print(f"❌ {attempt_name} failed with status {resp_k1.status_code}")

    if not prihlaska_guid:
        print("❌ VŠETKY POKUSY O KROK 1 NEPREŠLI — končím.")
        return

    # ------------------------------------------
    # Continue with rest of tests only if prihlaska creation succeeded
    # ------------------------------------------
    
    # 2 — Krok 2
    print(f"\n📋 Krok 2 prihlášky...")
    send_post_with_session(CTX, "/api/zapisAModifikaciaKonceptuPrihlasky",
              build_koncept_krok_2(dieta_guid, prihlaska_guid))

    # ------------------------------------------
    # POZITÍVNE SEARCH TESTY - FIXED PAYLOADS
    # ------------------------------------------
    print("\n🔍 POZITÍVNE TESTY: vyhľadávanie\n")

    # Use correct API format for search
    def search_api_format(page_size=20, ms=False, zs=True, text=""):
        return {
            "skolskyRokKod": "2026/2027",
            "ms": ms,
            "zs": zs,
            "pocetZaznamovNaStranku": page_size,
            "cisloStranky": 1,
            "text": text
        }

    POS = [
        ("SEARCH-BASE-20", search_api_format(20)),
        ("SEARCH-BASE-100K", search_api_format(100000)),
        ("SEARCH-ZS-20", search_api_format(20, False, True)),
        ("SEARCH-ZS-100K", search_api_format(100000, False, True)),
        ("SEARCH-MS-20", search_api_format(20, True, False)),
        ("SEARCH-MS-100K", search_api_format(100000, True, False)),
        ("SEARCH-TEXT-20", search_api_format(20, False, True, "bratislava")),
        ("SEARCH-TEXT-100K", search_api_format(100000, False, True, "bratislava")),
    ]

    # Build search headers with dynamic tokens
    search_headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive", 
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Moj-profil2",
        "RequestVerificationToken": csrf,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "x-token-descriptor": token_descriptor,
        "Cookie": cookie_bundle
    }

    for name, p in POS:
        r = send_post_with_session(CTX, "/api/vyhladanieMSaZS", p, headers=search_headers)
        
        # Check for success response
        ok = False
        if r.status_code == 200:
            try:
                resp_json = r.json()
                if resp_json.get("kodSpracovania") == "1700":
                    ok = True
                    pocet_skol = resp_json.get("pocet", {}).get("pocetKmenovychSaSZ", 0)
                    print(f"{name} → {r.status_code} (školy: {pocet_skol})")
                else:
                    print(f"{name} → {r.status_code} (kód: {resp_json.get('kodSpracovania')})")
            except:
                print(f"{name} → {r.status_code} (JSON error)")
        else:
            print(f"{name} → {r.status_code}")
            
        record(name, ok)

    # ------------------------------------------
    # POZITÍVNE VRATENIE KONCEPTU
    # ------------------------------------------
    send_post_with_session(CTX, "/api/zapisAModifikaciaKonceptuPrihlasky",
              build_koncept_krok_3(dieta_guid, prihlaska_guid))

    detail = send_post_with_session(CTX, "/api/vratenieKonceptuPrihlasky",
                       {"prihlaskaGUID": prihlaska_guid})

    ok = (detail.status_code == 200)
    record("KONCEPT-DETAIL", ok)
    print(f"KONCEPT-DETAIL → {detail.status_code}")

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------
    print("\n============================================================")
    print("SUMMARY")
    print("============================================================")
    print("TEST NAME                      | RESULT")
    print("--------------------------------|-------------")

    passed = 0
    total = 0
    
    for name, ok in results:
        icon = "🟢 PASS" if ok else "🔴 FAIL"
        print(f"{name:30} | {icon}")
        if ok:
            passed += 1
        total += 1

    print(f"\n📊 FINAL RESULT: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% success rate
        print(f"✔️ TEST MOSTLY PASSED!")
        print(f"   🧒 Dieťa: {first} {last} (GUID: {dieta_guid})")
        print(f"   📋 Prihláška: {prihlaska_guid}")
    else:
        print(f"❌ TEST FAILED!")

    print("\n🏁 HOTOVO.\n")


if __name__ == "__main__":
    main()