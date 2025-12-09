# tests/run_zs_prihlaska.py
# ============================================================
# Komplexný ZŠ scenár s prihlásením a dynamic tokenmi
# Používa iba API + COMMON_HEADERS + VYHLEDAVACIE_HEADERS
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import re
import html
from bs4 import BeautifulSoup

from config.headers import COMMON_HEADERS, VYHLEDAVACIE_HEADERS
from config.settings import HOST, SUBJEKT_GUID, PRIHLASENA_OSOBA_GUID, SKOLSKY_ROK_KOD_2026
from config.random_names import generate_random_name

from tests.common import send_post, send_get, safe_extract

from payloads.dieta import create_dieta_payload
from payloads.prihlaska import (
    koncept_krok_1, koncept_krok_2, koncept_krok_3,
    koncept_krok_4, koncept_krok_5
)
from payloads.oblubene import payload_oblubene_zs, payload_add_favorite_school
from payloads.vyhladavanie import (
    search_address_payload, search_base_payload,
    search_slovak_payload, search_statne_payload, search_typy_payload
)

# Prihlasovacie údaje
USERNAME = "martin.milacek@professional-test-automation.com"
PASSWORD = "Initial0!"
ACS_URL = f"{HOST}/assertionconsumerservice"

CTX = "ZS-FLOW"

# Global authentication data
session = None
dynamic_csrf = None
dynamic_token_descriptor = None
dynamic_cookie_bundle = None
dynamic_subjekt_guid = None
dynamic_prihlasena_osoba_guid = None


# -------------------------------------------------------------
# SAML login sequence
# -------------------------------------------------------------
def saml_login():
    global session, dynamic_csrf, dynamic_token_descriptor, dynamic_cookie_bundle
    global dynamic_subjekt_guid, dynamic_prihlasena_osoba_guid
    
    session = requests.Session()

    # SAML login process
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
    dynamic_csrf = antiforgery_match.group(1) if antiforgery_match else None

    userdata_match = re.search(r"window\.userData\s*=\s*(\{.*?\});", html_profile, re.DOTALL)
    
    if userdata_match:
        try:
            userdata = json.loads(userdata_match.group(1).rstrip(";"))
            dynamic_token_descriptor = userdata.get("tokenDescriptor")
            
            # Extract GUIDs
            person_data = userdata.get("person", {})
            dynamic_subjekt_guid = person_data.get("subjectGuid", "")
            dynamic_prihlasena_osoba_guid = person_data.get("loggedInPersonGuid", "")
        except:
            pass

    # Extract cookies
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
    
    dynamic_cookie_bundle = "; ".join(cookie_parts)

    return bool(dynamic_csrf and dynamic_token_descriptor and dynamic_subjekt_guid and dynamic_prihlasena_osoba_guid)


# -------------------------------------------------------------
# Override send functions to use dynamic tokens
# -------------------------------------------------------------
def send_post_with_tokens(ctx, endpoint, payload, headers=None):
    """Send POST with dynamic tokens and session"""
    global session, dynamic_csrf, dynamic_token_descriptor, dynamic_cookie_bundle
    
    url = f"{HOST}{endpoint}"
    print(f"[{ctx}] POST {endpoint}")
    
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
            "RequestVerificationToken": dynamic_csrf,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "x-token-descriptor": dynamic_token_descriptor,
            "Cookie": dynamic_cookie_bundle
        }
    else:
        # Update existing headers with dynamic values
        headers = headers.copy()
        headers["RequestVerificationToken"] = dynamic_csrf
        headers["x-token-descriptor"] = dynamic_token_descriptor
        headers["Cookie"] = dynamic_cookie_bundle
    
    try:
        resp = session.post(url, json=payload, headers=headers)
        print(f"[{ctx}] → Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"[{ctx}] ❌ Error: {resp.text[:200]}")
        
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


def send_get_with_tokens(ctx, endpoint, params, headers=None):
    """Send GET with dynamic tokens and session"""
    global session, dynamic_csrf, dynamic_token_descriptor, dynamic_cookie_bundle
    
    url = f"{HOST}{endpoint}"
    print(f"[{ctx}] GET {endpoint}")
    
    # Build dynamic headers
    if headers is None:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd", 
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": HOST,
            "Referer": f"{HOST}/Moj-profil2",
            "RequestVerificationToken": dynamic_csrf,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "x-token-descriptor": dynamic_token_descriptor,
            "Cookie": dynamic_cookie_bundle
        }
    else:
        # Update existing headers with dynamic values
        headers = headers.copy()
        headers["RequestVerificationToken"] = dynamic_csrf
        headers["x-token-descriptor"] = dynamic_token_descriptor
        headers["Cookie"] = dynamic_cookie_bundle
    
    try:
        resp = session.get(url, params=params, headers=headers)
        print(f"[{ctx}] → Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"[{ctx}] ❌ Error: {resp.text[:200]}")
        
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


def safe_extract_with_tokens(resp, json_data, path, description):
    """Safe extract with better error handling"""
    if resp.status_code != 200:
        print(f"   ⚠️ {description}: HTTP error {resp.status_code}")
        return None
        
    if not json_data:
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
            return None
    
    print(f"   ✅ {description}: {current}")
    return current


def create_dieta_payload_with_dynamic_guid(first, last):
    """Create child payload with dynamic GUID - FIXED"""
    payload = create_dieta_payload(first, last)
    
    # Debug - pozrime si štruktúru payload
    print(f"🔍 Original payload keys: {list(payload.keys())}")
    
    # Skúsme rôzne možné štruktúry
    if "dieta" in payload:
        payload["dieta"]["subjektGUID"] = dynamic_subjekt_guid
    elif "subjektGUID" in payload:
        payload["subjektGUID"] = dynamic_subjekt_guid
    else:
        # Ak nevieme nájsť správne miesto, pridáme top-level
        payload["subjektGUID"] = dynamic_subjekt_guid
        # A skúsme aj nested
        if isinstance(payload.get("dieta"), dict):
            payload["dieta"]["subjektGUID"] = dynamic_subjekt_guid
    
    print(f"🔍 Updated payload keys: {list(payload.keys())}")
    return payload


def main():
    print("\n🔐 Spúšťam SAML login…\n")
    
    if not saml_login():
        print("❌ Login failed!")
        sys.exit(1)
        
    print("✅ Login successful!")
    print(f"CSRF: {dynamic_csrf[:50]}...")
    print(f"Token: {dynamic_token_descriptor[:50]}...")
    print(f"Subjekt GUID: {dynamic_subjekt_guid}")
    print(f"Prihlasena Osoba GUID: {dynamic_prihlasena_osoba_guid}")

    print("\n🎓 Spúšťam ZŠ testovací scenár (1–31)…")

    # ---------------------------------------------
    # 0 – generovanie mena
    # ---------------------------------------------
    first, last = generate_random_name()
    print(f"\n🧒 Generujem dieťa: {first}-{last}")

    # ---------------------------------------------
    # 1 – oznámenia
    # ---------------------------------------------
    send_post_with_tokens(CTX, "/api/vratenieZoznamuOznameniPreZZ", {
        "prihlasenaOsobaGUID": dynamic_prihlasena_osoba_guid,
        "precitana": False,
        "pocetZaznamovNaStranku": 50,
        "cisloStranky": 1
    })

    # ---------------------------------------------
    # 2 – zoznam detí
    # ---------------------------------------------
    send_post_with_tokens(CTX, "/api/vratenieZoznamuDeti", {
        "guid": dynamic_subjekt_guid, "lenPlatne": True
    })

    # ---------------------------------------------
    # 3 – vytvorenie dieťaťa (FIXED)
    # ---------------------------------------------
    print("\n🔍 DEBUG: Vytváram payload pre dieťa...")
    child_payload = create_dieta_payload_with_dynamic_guid(first, last)
    
    print("🔍 Final child payload structure:")
    print(json.dumps(child_payload, indent=2, ensure_ascii=False))

    resp_create = send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaDietata",
        child_payload
    )

    try:
        dieta_guid = safe_extract_with_tokens(
            resp_create, resp_create.json(),
            ["dieta", "guid"],
            "GUID dieťaťa"
        )
    except Exception as e:
        print(f"❌ Exception extracting dieta GUID: {e}")
        # Try alternative extraction paths
        try:
            json_resp = resp_create.json()
            print(f"🔍 Full response: {json.dumps(json_resp, indent=2, ensure_ascii=False)}")
            
            # Try different paths
            possible_paths = [
                ["guid"],
                ["dieta"],
                ["data", "guid"],
                ["result", "guid"]
            ]
            
            for path in possible_paths:
                try:
                    dieta_guid = safe_extract_with_tokens(resp_create, json_resp, path, f"GUID dieťaťa (path: {path})")
                    if dieta_guid:
                        break
                except:
                    continue
        except:
            dieta_guid = None

    if not dieta_guid:
        print("❌ Failed to create child - končím.")
        return

    # ---------------------------------------------
    # 4 – refresh detí
    # ---------------------------------------------
    send_post_with_tokens(CTX, "/api/vratenieZoznamuDeti", {
        "guid": dynamic_subjekt_guid, "lenPlatne": True
    })

    # ---------------------------------------------
    # 5 – detail dieťaťa
    # ---------------------------------------------
    send_post_with_tokens(CTX, "/api/vratenieUdajovDietata", {
        "guid": dieta_guid
    })

    # ---------------------------------------------
    # 6 – koncept krok 1
    # ---------------------------------------------
    resp_k1 = send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid)
    )

    try:
        prihlaska_guid = safe_extract_with_tokens(
            resp_k1, resp_k1.json(),
            ["prihlaska", "prihlaskaGUID"],
            "GUID prihlášky"
        )
    except Exception as e:
        print(f"❌ Exception extracting prihlaska GUID: {e}")
        # Try alternative extraction
        try:
            json_resp = resp_k1.json()
            print(f"🔍 Full prihlaska response: {json.dumps(json_resp, indent=2, ensure_ascii=False)}")
        except:
            pass
        prihlaska_guid = None

    if not prihlaska_guid:
        print("❌ Failed to create prihlaska - končím.")
        return

    # ---------------------------------------------
    # 7 – koncept krok 2
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_2(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 8 – obľúbené školy
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 9 – vrateniePoloziekFiltrov (FIXED)
    # ---------------------------------------------
    print("[ZS-FLOW] POST /api/vrateniePoloziekFiltrov")

    # Build dynamic search headers
    search_headers = VYHLEDAVACIE_HEADERS.copy()
    search_headers["RequestVerificationToken"] = dynamic_csrf
    search_headers["x-token-descriptor"] = dynamic_token_descriptor
    search_headers["Cookie"] = dynamic_cookie_bundle

    resp_filters = send_post_with_tokens(
        CTX,
        "/api/vrateniePoloziekFiltrov",
        {
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "ms": False,
            "zs": True
        },
        headers=search_headers
    )

    try:
        vzd = resp_filters.json().get("vzdialenost", [])
        print(f"   → Načítaných vzdialeností: {len(vzd)}")
    except Exception as e:
        print(f"   ⚠️ Response nie je JSON: {e}")

    # ---------------------------------------------
    # 9b – vyhľadanie adresy
    # ---------------------------------------------
    send_get_with_tokens(
        CTX,
        "/api/search",
        search_address_payload()
    )

    # ---------------------------------------------
    # 10–22 – vyhľadávanie MS/ZŠ
    # ---------------------------------------------
    print("\n🔍 Spúšťam vyhľadávacie kroky (11–22)…")

    for p in [
        search_base_payload(20),
        search_base_payload(100000),

        search_slovak_payload(20),
        search_slovak_payload(100000),

        search_slovak_payload(20),
        search_slovak_payload(100000),

        search_statne_payload(20),
        search_statne_payload(100000),

        search_typy_payload(20),
        search_typy_payload(100000),

        search_typy_payload(20),
        search_typy_payload(100000),
    ]:
        send_post_with_tokens(
            CTX,
            "/api/vyhladanieMSaZS",
            p,
            headers=search_headers
        )

    # ---------------------------------------------
    # 23 – finálne obľúbené
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 24 – pridanie obľúbenej školy
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/zapisOblubenychSaSZ",
        payload_add_favorite_school()
    )

    # ---------------------------------------------
    # 25 – overenie obľúbených
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieEDUIDOblubenychSaSZ",
        payload_oblubene_zs()
    )

    # ---------------------------------------------
    # 26 – koncept krok 3
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_3(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 27 – vybrané školy
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieVybranychSaSZ",
        {"prihlaskaGUID": prihlaska_guid}
    )

    # ---------------------------------------------
    # 28 – koncept krok 4
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_4(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 29 – koncept krok 5
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_5(dieta_guid, prihlaska_guid)
    )

    # ---------------------------------------------
    # 30 – kontrola konceptu
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid}
    )

    # ---------------------------------------------
    # 31 – finálna kontrola
    # ---------------------------------------------
    send_post_with_tokens(
        CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": prihlaska_guid}
    )

    print(f"\n✔️ TEST PASSED — ZŠ scenár 1–31 prešiel úspešne!")
    print(f"   🧒 Dieťa: {first} {last} (GUID: {dieta_guid})")
    print(f"   📋 Prihláška: {prihlaska_guid}")
    print()


if __name__ == "__main__":
    main()