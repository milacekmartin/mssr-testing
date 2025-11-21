import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import sys, os, html

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import HOST

USERNAME = ""
PASSWORD = ""

ACS_URL = f"{HOST}/assertionconsumerservice"


# -------------------------------------------------------------
# HTML Token extraction
# -------------------------------------------------------------
def extract_antiforgery(html_text: str):
    m = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html_text)
    return m.group(1) if m else None


def extract_userdata(html_text: str):
    m = re.search(r"window\.userData\s*=\s*(\{.*?\});", html_text, re.DOTALL)
    if not m:
        return None
    json_text = m.group(1).rstrip(";")
    try:
        return json.loads(json_text)
    except Exception:
        return None


def extract_guids(html_text: str, userdata: dict):
    """Extract subject and person GUIDs from various sources"""
    guids = {}
    
    # Try to extract from userdata
    if userdata:
        guids["subjekt_guid"] = userdata.get("subjektGuid")
        guids["prihlasena_osoba_guid"] = userdata.get("prihlasenOsobaGuid")
        guids["user_guid"] = userdata.get("userGuid")
        guids["identity_guid"] = userdata.get("identityGuid")
    
    # Try to extract from HTML patterns
    guid_patterns = [
        r'subjektGuid["\']?\s*[:=]\s*["\']?([a-f0-9\-]{36})',
        r'prihlasenOsobaGuid["\']?\s*[:=]\s*["\']?([a-f0-9\-]{36})',
        r'userGuid["\']?\s*[:=]\s*["\']?([a-f0-9\-]{36})',
        r'guid["\']?\s*[:=]\s*["\']?([a-f0-9\-]{36})',
    ]
    
    for pattern in guid_patterns:
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        if matches:
            guids[f"html_guids"] = matches
    
    return guids


# -------------------------------------------------------------
# Child payload builder
# -------------------------------------------------------------
def build_base_child_payload(first, last, subjekt_guid):
    return {
        "subjektGUID": subjekt_guid,
        "dietaGUID": None,
        "rodneCislo": None,
        "meno": first,
        "priezvisko": last,
        "rodnePriezvisko": None,
        "datumNarodenia": "2020-01-25",
        "miestoNarodenia": "Bratislava",
        "pohlavieKod": "1",
        "narodnostKod": "2",
        "statnaPrislusnost": [{"statnaPrislusnostKod": "211"}],
        "materinskyJazykKod": "SK",
        "inyMaterinskyJazykKod": None,
        "rozpracovane": False,
        "platne": True,

        "tpStatKod": "601",
        "tpObecKod": None,
        "tppsc": None,
        "tpUlicaKod": None,
        "tpUlica": None,
        "tpSupisneCislo": None,
        "tpOrientacneCislo": None,
        "tpAdresaMimoSR": "AAA",
        "adresaTPZhodnaSTPRodica": False,

        "zpStatKod": "601",
        "zpObecKod": None,
        "zppsc": None,
        "zpUlicaKod": None,
        "zpUlica": None,
        "zpSupisneCislo": None,
        "zpOrientacneCislo": None,
        "zpAdresaMimoSR": "AAA",
        "adresaObvyklaZhodnaSTP": True,

        "narodnostZRFO": False,
        "miestoNarodeniaZRFO": False
    }


def generate_random_name():
    """Generate random first and last name"""
    import random
    first_names = ["Martin", "Peter", "Jakub", "Anna", "Maria", "Eva", "Tomáš", "Michal"]
    last_names = ["Novák", "Svoboda", "Dvořák", "Černý", "Procházka", "Krejčí", "Horák"]
    return (
        random.choice(first_names) + str(random.randint(100, 999)),
        random.choice(last_names) + str(random.randint(100, 999))
    )


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

    antiforgery_input = extract_antiforgery(html_profile)
    userdata = extract_userdata(html_profile)
    token_descriptor = userdata.get("tokenDescriptor") if userdata else None
    guids = extract_guids(html_profile, userdata)

    # Extract all cookies
    cookies_dict = {}
    for cookie in sess.cookies:
        cookies_dict[cookie.name] = cookie.value

    return {
        "session": sess,
        "antiforgery_input": antiforgery_input,
        "token_descriptor": token_descriptor,
        "userdata": userdata,
        "guids": guids,
        "cookies": cookies_dict,
    }


def print_extracted_tokens(data):
    """Print all extracted tokens and identifiers"""
    print("\n" + "="*50)
    print("🔐 EXTRACTED TOKENS & IDENTIFIERS")
    print("="*50)
    
    print("\n# -----------------------------")
    print("# Tokeny, cookies, autentifikácia")
    print("# -----------------------------")
    
    if data["antiforgery_input"]:
        print(f'CSRF = "{data["antiforgery_input"]}"')
    
    if data["token_descriptor"]:
        print(f'IAM_TOKEN = "{data["token_descriptor"]}"')
    
    # Print important cookies
    important_cookies = [
        "IamTokenDescriptor", 
        "_DS", "_DSA", "_DC",
        ".AspNetCore.Antiforgery.UaYXyBoyr8Q",
        ".AspNetCore.Antiforgery.fAr6xnvBhu0",
        "IamWeb", "culture"
    ]
    
    cookie_parts = []
    for cookie_name in important_cookies:
        if cookie_name in data["cookies"]:
            cookie_parts.append(f"{cookie_name}={data['cookies'][cookie_name]}")
    
    if cookie_parts:
        cookie_bundle = "; ".join(cookie_parts)
        print(f'COOKIE_BUNDLE = "{cookie_bundle}"')
    
    print("\n# -----------------------------")
    print("# GUIDy subjektu / prihlásenej osoby")
    print("# -----------------------------")
    
    # Extract GUIDs from userdata
    person_data = data["userdata"].get("person", {}) if data["userdata"] else {}
    subjekt_guid = person_data.get("subjectGuid", "")
    prihlasena_osoba_guid = person_data.get("loggedInPersonGuid", "")
    
    if subjekt_guid:
        print(f'SUBJEKT_GUID = "{subjekt_guid}"')
    
    if prihlasena_osoba_guid:
        print(f'PRIHLASENA_OSOBA_GUID = "{prihlasena_osoba_guid}"')


# -------------------------------------------------------------
# Test child creation
# -------------------------------------------------------------
def test_child_creation(session, antiforgery_input, token_descriptor, subjekt_guid):
    print("\n===============================================")
    print("🧒 TESTING CHILD CREATION")
    print("===============================================\n")

    # Generate random child
    first, last = generate_random_name()
    print(f"Creating child: {first} {last}")
    
    # Build payload
    child_payload = build_base_child_payload(first, last, subjekt_guid)
    
    # Test child creation endpoint
    endpoint = f"{HOST}/api/zapisAModifikaciaDietata"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Moj-profil2",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "RequestVerificationToken": antiforgery_input,
        "x-token-descriptor": token_descriptor,
    }
    
    print(f"🧪 POST {endpoint}")
    print(f"   Payload: {first} {last}")
    print(f"   Headers: {list(headers.keys())}")
    
    r = session.post(endpoint, json=child_payload, headers=headers)
    
    print(f"   → {r.status_code}")
    
    # Try to parse response
    try:
        response_json = r.json()
        print("   ✅ JSON Response:")
        print("   ", json.dumps(response_json, indent=4, ensure_ascii=False)[:500])
        
        # Check for child GUID
        child_guid = response_json.get("dieta", {}).get("guid") if isinstance(response_json, dict) else None
        if child_guid:
            print(f"   🎉 Child created successfully! GUID: {child_guid}")
            return True, child_guid
            
    except Exception as e:
        print(f"   📄 Non-JSON Response: {r.text[:300]}")
        print(f"   Error parsing JSON: {e}")
    
    return False, None


# -------------------------------------------------------------
# Test správneho endpointu s JSON response extraction
# -------------------------------------------------------------
def test_correct_endpoint(session, antiforgery_input, token_descriptor):
    print("\n===============================================")
    print("🔍 TESTING CORRECT ENDPOINT WITH DIFFERENT METHODS")
    print("===============================================\n")

    endpoint = f"{HOST}/Moj-profil2/vyhladanieMSaZS"
    
    tests = [
        # Test 1: GET request
        ("GET", None, {"Accept": "application/json"}),
        
        # Test 2: GET s parametrami
        ("GET", None, {"Accept": "application/json"}, "?druhVzdelavania=MS"),
        
        # Test 3: POST JSON
        ("POST", {"druhVzdelavania": "MS"}, {
            "Accept": "application/json", 
            "Content-Type": "application/json; charset=UTF-8"
        }),
        
        # Test 4: POST form-encoded
        ("POST", {"druhVzdelavania": "MS"}, {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }),
        
        # Test 5: POST s antiforgery tokenmi
        ("POST", {"druhVzdelavania": "MS"}, {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "RequestVerificationToken": antiforgery_input,
            "x-token-descriptor": token_descriptor,
            "X-Requested-With": "XMLHttpRequest"
        }),
    ]

    for i, test_data in enumerate(tests, 1):
        method = test_data[0]
        payload = test_data[1]
        headers = test_data[2]
        url_params = test_data[3] if len(test_data) > 3 else ""
        
        url = endpoint + url_params
        
        print(f"\n🧪 TEST {i}: {method} {url}")
        print(f"   Payload: {payload}")
        print(f"   Headers: {list(headers.keys())}")

        # Add base headers
        full_headers = {
            "Origin": HOST,
            "Referer": f"{HOST}/Moj-profil2",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        full_headers.update(headers)

        if method == "GET":
            r = session.get(url, headers=full_headers)
        else:  # POST
            if headers.get("Content-Type", "").startswith("application/json"):
                r = session.post(url, json=payload, headers=full_headers)
            else:
                r = session.post(url, data=payload, headers=full_headers)

        print(f"   → {r.status_code}")
        
        # Check if response is JSON
        try:
            response_json = r.json()
            print("   ✅ JSON Response:")
            print("   ", json.dumps(response_json, indent=4, ensure_ascii=False)[:500])
            if response_json:  # If not empty
                return True, method, payload, response_json
        except:
            # Try to extract JSON from HTML
            json_matches = re.findall(r'(\{[^{}]*"data"[^{}]*\})', r.text)
            if json_matches:
                print("   🔍 Found JSON in HTML:")
                for match in json_matches[:2]:
                    try:
                        parsed = json.loads(match)
                        print("   ", json.dumps(parsed, indent=4, ensure_ascii=False)[:300])
                        return True, method, payload, parsed
                    except:
                        print(f"   📄 Invalid JSON: {match[:100]}")
            
            print("   📄 HTML Response (first 300 chars):")
            print("   ", r.text[:300].replace('\n', ' '))

        print()
    
    return False, None, None, None


# -------------------------------------------------------------
# Extract data from HTML response
# -------------------------------------------------------------
def extract_data_from_html(html_text):
    """Try to extract data from HTML response"""
    print("\n===============================================")
    print("🔍 ANALYZING HTML RESPONSE FOR DATA")
    print("===============================================\n")

    # Look for JSON data in HTML
    json_matches = re.findall(r'(\{[^{}]*"[^"]*"[^{}]*\})', html_text)
    if json_matches:
        print(f"Found {len(json_matches)} potential JSON objects:")
        for i, match in enumerate(json_matches[:5], 1):
            print(f"  {i}. {match[:100]}...")
            try:
                parsed = json.loads(match)
                print(f"     ✅ Valid JSON: {parsed}")
            except:
                print(f"     ❌ Invalid JSON")

    # Look for data in tables
    soup = BeautifulSoup(html_text, 'html.parser')
    
    tables = soup.find_all('table')
    if tables:
        print(f"\nFound {len(tables)} tables")
        for i, table in enumerate(tables[:2], 1):
            rows = table.find_all('tr')
            print(f"  Table {i}: {len(rows)} rows")
            if rows:
                first_row = [td.get_text().strip() for td in rows[0].find_all(['th', 'td'])]
                print(f"    First row: {first_row[:5]}")

    # Look for lists
    lists = soup.find_all(['ul', 'ol'])
    if lists:
        print(f"\nFound {len(lists)} lists")
        for i, lst in enumerate(lists[:2], 1):
            items = lst.find_all('li')
            print(f"  List {i}: {len(items)} items")
            if items:
                first_items = [li.get_text().strip() for li in items[:3]]
                print(f"    First items: {first_items}")


def print_final_tokens(data):
    """Print final clean tokens for copy-paste"""
    print("\n" + "="*80)
    print("🎯 FINAL TOKENS FOR COPY-PASTE")
    print("="*80)
    
    # Extract important cookies
    important_cookies = [
        "IamTokenDescriptor", 
        "_DS", "_DSA", "_DC",
        ".AspNetCore.Antiforgery.UaYXyBoyr8Q",
        ".AspNetCore.Antiforgery.fAr6xnvBhu0",
        "IamWeb", "culture"
    ]
    
    cookie_parts = []
    for cookie_name in important_cookies:
        if cookie_name in data["cookies"]:
            cookie_parts.append(f"{cookie_name}={data['cookies'][cookie_name]}")
    
    cookie_bundle = "; ".join(cookie_parts) if cookie_parts else ""
    
    # Extract GUIDs from userdata
    person_data = data["userdata"].get("person", {}) if data["userdata"] else {}
    subjekt_guid = person_data.get("subjectGuid", "")
    prihlasena_osoba_guid = person_data.get("loggedInPersonGuid", "")
    
    print("\n📋 CSRF Token:")
    print(f'"{data["antiforgery_input"]}"')
    
    print("\n🔑 x-token-descriptor:")
    print(f'"{data["token_descriptor"]}"')
    
    print("\n🍪 Complete Cookie Bundle:")
    print(f'"{cookie_bundle}"')
    
    print("\n🆔 Subject GUID:")
    print(f'"{subjekt_guid}"')
    
    print("\n👤 Logged In Person GUID:")
    print(f'"{prihlasena_osoba_guid}"')
    
    print("\n" + "="*80)


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
if __name__ == "__main__":
    print("\n🔐 Spúšťam SAML login…\n")

    data = saml_login()

    print("\n✅ Login successful!")
    
    # Print all extracted tokens and identifiers
    print_extracted_tokens(data)

    # Extract subject GUID for child creation
    person_data = data["userdata"].get("person", {}) if data["userdata"] else {}
    subjekt_guid = person_data.get("subjectGuid", "")

    # Test child creation first
    if subjekt_guid:
        child_success, child_guid = test_child_creation(
            data["session"], 
            data["antiforgery_input"], 
            data["token_descriptor"],
            subjekt_guid
        )
        
        if child_success:
            print(f"\n🎉 Child creation successful! GUID: {child_guid}")
        else:
            print("\n⚠️ Child creation failed!")
    else:
        print("\n❌ No subject GUID found, skipping child creation test")

    # Test search endpoint
    success, method, payload, response = test_correct_endpoint(
        data["session"], 
        data["antiforgery_input"], 
        data["token_descriptor"]
    )
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"Method: {method}")
        print(f"Payload: {payload}")
        print(f"Response: {response}")
    else:
        print("\n📄 No JSON responses found, but endpoint works!")
        print("Let's analyze the HTML response...")
        
        # Get the HTML response again for analysis
        r = data["session"].post(
            f"{HOST}/Moj-profil2/vyhladanieMSaZS",
            json={"druhVzdelavania": "MS"},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "Origin": HOST,
                "Referer": f"{HOST}/Moj-profil2",
            }
        )
        
        if r.status_code == 200:
            extract_data_from_html(r.text)
            
            # Save HTML for manual inspection
            with open("vyhladanie_response.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"\n💾 HTML response saved to: vyhladanie_response.html")

    # FINAL TOKEN PRINTOUT
    print_final_tokens(data)

    print("\n🔥 Hotovo.\n")