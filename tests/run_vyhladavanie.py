# tests/run_vyhladavanie.py
# ================================================
# Vyhľadávací test používajúci správny API endpoint a formát

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import re
import html
from bs4 import BeautifulSoup

from config.settings import HOST


# Prihlasovacie údaje
USERNAME = ""
PASSWORD = ""
ACS_URL = f"{HOST}/assertionconsumerservice"


# -------------------------------------------------------------
# Correct payload builders
# -------------------------------------------------------------
def search_api_payload(page_size=20, page_number=1, ms=False, zs=True, text=""):
    """Build payload in correct API format"""
    return {
        "skolskyRokKod": "2026/2027",
        "ms": ms,
        "zs": zs,
        "pocetZaznamovNaStranku": page_size,
        "cisloStranky": page_number,
        "text": text
    }


# -------------------------------------------------------------
# SAML login sequence
# -------------------------------------------------------------
def saml_login():
    sess = requests.Session()

    # SAML login process...
    r1 = sess.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)
    redirect1 = r1.headers.get("Location")

    r2 = sess.get(redirect1, allow_redirects=False)
    redirect2 = r2.headers.get("Location")
    if not redirect2.startswith("http"):
        redirect2 = "https://tiamidsk.iedu.sk" + redirect2

    r3 = sess.get(redirect2, allow_redirects=False)
    html3 = r3.text

    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        chooser = f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}"
        r3 = sess.get(chooser, allow_redirects=False)
        html3 = r3.text

    authn_guid = re.search(r'name="AuthnGuid"[^>]+value="([^"]+)"', html3).group(1)
    request_ver_token = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html3).group(1)

    r4 = sess.post("https://tiamidsk.iedu.sk/authn/lp", data={
        "AuthnGuid": authn_guid,
        "UserName": USERNAME,
        "UserPassword": PASSWORD,
        "btn-continue": "Prihlásiť sa",
        "__RequestVerificationToken": request_ver_token,
    }, allow_redirects=False)

    redirect3 = r4.headers.get("Location")
    if not redirect3.startswith("http"):
        redirect3 = "https://tiamidsk.iedu.sk" + redirect3

    r5 = sess.get(redirect3, allow_redirects=False)
    html5 = r5.text

    soup = BeautifulSoup(html5, "html.parser")
    form = soup.find("form")
    saml_raw = form.find("input", {"name": "SAMLResponse"}).get("value")
    relay = form.find("input", {"name": "RelayState"}).get("value")
    saml_decoded = html.unescape(saml_raw)

    acs_resp = sess.post(ACS_URL, data={
        "RelayState": relay,
        "SAMLResponse": saml_decoded,
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://tiamidsk.iedu.sk",
        "Referer": "https://tiamidsk.iedu.sk/",
    }, allow_redirects=False)

    home_url = acs_resp.headers["Location"]
    home = sess.get(home_url)

    profile = sess.get(f"{HOST}/Moj-profil2")
    html_profile = profile.text

    # Extract tokens
    antiforgery_match = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html_profile)
    antiforgery_input = antiforgery_match.group(1) if antiforgery_match else None

    userdata_match = re.search(r"window\.userData\s*=\s*(\{.*?\});", html_profile, re.DOTALL)
    userdata = None
    token_descriptor = None
    if userdata_match:
        try:
            userdata = json.loads(userdata_match.group(1).rstrip(";"))
            token_descriptor = userdata.get("tokenDescriptor")
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
        for cookie in sess.cookies:
            if cookie.name == cookie_name:
                cookie_parts.append(f"{cookie.name}={cookie.value}")
                break
    
    cookie_bundle = "; ".join(cookie_parts)

    return {
        "session": sess,
        "csrf": antiforgery_input,
        "token_descriptor": token_descriptor,
        "cookie_bundle": cookie_bundle,
        "userdata": userdata,
    }


def test_api_search(session, csrf, token_descriptor, cookie_bundle):
    """Test the exact API format from your example"""
    
    url = f"{HOST}/api/vyhladanieMSaZS"
    
    # Exact payload from your example
    payload = {
        "skolskyRokKod": "2026/2027",
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "text": "groslingova"
    }
    
    # Headers matching your example
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Prihlaska?typSaSZ=Z%C5%A0&guid=56d4b481-2f38-437c-beac-4491c2337800",
        "RequestVerificationToken": csrf,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors", 
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "x-token-descriptor": token_descriptor,
        "Cookie": cookie_bundle
    }
    
    print(f"🧪 Testing exact API format...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Key headers: RequestVerificationToken, x-token-descriptor, Cookie")
    
    try:
        resp = session.post(url, json=payload, headers=headers)
        
        print(f"→ Status: {resp.status_code}")
        print(f"→ Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        
        if resp.status_code == 200:
            try:
                resp_json = resp.json()
                print(f"✅ JSON Response:")
                print(json.dumps(resp_json, indent=2, ensure_ascii=False))
                
                # Check for expected response structure
                if "kodSpracovania" in resp_json:
                    if resp_json["kodSpracovania"] == "1700":
                        print(f"🎉 Success! Service returned success code 1700")
                        return True, resp_json
                    else:
                        print(f"⚠️ Service returned code: {resp_json['kodSpracovania']}")
                        print(f"Description: {resp_json.get('popisSpracovania', 'N/A')}")
                        return False, resp_json
                else:
                    print(f"🔍 Unexpected response structure")
                    return False, resp_json
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Response text: {resp.text}")
                return False, None
        else:
            print(f"❌ HTTP Error {resp.status_code}")
            print(f"Response: {resp.text}")
            return False, None
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False, None


def post_vyhladavanie_api(session, csrf, token_descriptor, cookie_bundle, test_config, ctx):
    """Search using correct API format"""
    
    url = f"{HOST}/api/vyhladanieMSaZS"
    
    payload = search_api_payload(
        page_size=test_config.get("page_size", 20),
        page_number=test_config.get("page_number", 1), 
        ms=test_config.get("ms", False),
        zs=test_config.get("zs", True),
        text=test_config.get("text", "")
    )
    
    headers = {
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

    print(f"[{ctx}] POST /api/vyhladanieMSaZS")
    print(f"[{ctx}] Config: {test_config}")

    try:
        resp = session.post(url, json=payload, headers=headers)
        print(f"[{ctx}] → Status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[{ctx}] ❌ Error: {resp.text}")
            return False

        resp_json = resp.json()
        
        if resp_json.get("kodSpracovania") == "1700":
            pocet_info = resp_json.get("pocet", {})
            pocet_skol = pocet_info.get("pocetKmenovychSaSZ", 0)
            print(f"[{ctx}] ✅ Success! Found {pocet_skol} schools")
            return True
        else:
            kod = resp_json.get("kodSpracovania", "unknown")
            popis = resp_json.get("popisSpracovania", "No description")
            print(f"[{ctx}] ⚠️ Service code {kod}: {popis}")
            return False

    except Exception as e:
        print(f"[{ctx}] 💥 Exception: {e}")
        return False


def main():
    print("\n🔐 Spúšťam SAML login…\n")
    
    login_data = saml_login()
    
    if not login_data["csrf"] or not login_data["token_descriptor"]:
        print("❌ Login failed - missing tokens")
        sys.exit(1)
        
    print("✅ Login successful!")
    print(f"CSRF: {login_data['csrf'][:50]}...")
    print(f"Token: {login_data['token_descriptor'][:50]}...")

    # Test exact API format first
    api_works, sample_response = test_api_search(
        login_data["session"],
        login_data["csrf"], 
        login_data["token_descriptor"],
        login_data["cookie_bundle"]
    )
    
    if not api_works:
        print("\n❌ API test failed! Cannot proceed with full test suite.")
        sys.exit(1)

    print(f"\n🎉 API works! Running full test suite...")

    session = login_data["session"]
    csrf = login_data["csrf"]
    token_descriptor = login_data["token_descriptor"]
    cookie_bundle = login_data["cookie_bundle"]

    success_count = 0
    total_tests = 12

    # Updated test configurations using correct API format
    tests = [
        ("base 20", {"page_size": 20, "page_number": 1}),
        ("base 100k", {"page_size": 100000, "page_number": 1}),
        ("MS only 20", {"page_size": 20, "page_number": 1, "ms": True, "zs": False}),
        ("MS only 100k", {"page_size": 100000, "page_number": 1, "ms": True, "zs": False}),
        ("ZS only 20", {"page_size": 20, "page_number": 1, "ms": False, "zs": True}),
        ("ZS only 100k", {"page_size": 100000, "page_number": 1, "ms": False, "zs": True}),
        ("Both MS+ZS 20", {"page_size": 20, "page_number": 1, "ms": True, "zs": True}),
        ("Both MS+ZS 100k", {"page_size": 100000, "page_number": 1, "ms": True, "zs": True}),
        ("Text search 20", {"page_size": 20, "page_number": 1, "text": "bratislava"}),
        ("Text search 100k", {"page_size": 100000, "page_number": 1, "text": "bratislava"}),
        ("Page 2 test", {"page_size": 20, "page_number": 2}),
        ("Page 3 test", {"page_size": 20, "page_number": 3}),
    ]

    for i, (test_name, config) in enumerate(tests, 11):
        print(f"\n--- Test {i}: {test_name} ---")
        if post_vyhladavanie_api(session, csrf, token_descriptor, cookie_bundle, config, f"TEST-{i}"):
            success_count += 1

    print(f"\n" + "="*60)
    print(f"📊 SUMMARY: {success_count}/{total_tests} tests passed")
    print("="*60)

    if success_count >= total_tests * 0.9:  # 90% success rate
        print(f"\n✔️ TEST PASSED — {success_count}/{total_tests} tests succeeded.\n")
        sys.exit(0)
    else:
        print(f"\n❌ TEST FAILED — only {success_count}/{total_tests} tests succeeded.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()