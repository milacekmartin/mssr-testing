import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import HOST


USERNAME = "martin.milacek@annotation.sk"
PASSWORD = "Initial0!"


# ============================================================
# 1) HTML DECODE (Cypress version → Python equivalent)
# ============================================================
def decode_html_entities(s: str):
    import html
    return html.unescape(s)


# ============================================================
# 2) FOLLOW REDIRECT CHAIN (bez automatického redirect)
# ============================================================
def follow_redirects(url, cookies, max_hops=20):
    hops = 0
    sess = requests.Session()

    while True:
        if hops > max_hops:
            raise Exception("Too many redirects")

        resp = sess.get(url, cookies=cookies, allow_redirects=False)

        # konečný response = nie redirect
        if resp.status_code < 300 or resp.status_code >= 400:
            return resp

        loc = resp.headers.get("Location")
        if not loc:
            return resp

        # relatívne → absolútne
        if not loc.startswith("http"):
            loc = urljoin(HOST, loc)

        url = loc
        hops += 1


# ============================================================
# 3) Extract GUID from HTML
# ============================================================
def extract_guid(html: str, key: str):
    m = re.search(rf'"{key}"\s*:\s*"([^"]+)"', html)
    return m.group(1) if m else None


# ============================================================
# 4) Build SAFE cookie header (Cypress version)
# ============================================================
def build_cookie_dict(raw_set_cookie_list):
    """
    Prijme zoznam Set-Cookie a vyrobí dict {name:value}
    """
    cookies = {}
    for raw in raw_set_cookie_list:
        parts = raw.split(";")
        keyval = parts[0].strip()
        if "=" in keyval:
            k, v = keyval.split("=", 1)
            cookies[k] = v
    return cookies


# ============================================================
# 5) SAML LOGIN ENGINE (Python equivalent)
# ============================================================
def saml_login():

    sess = requests.Session()

    # 1) GET /loginosoba
    r1 = sess.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)
    if "Location" not in r1.headers:
        raise Exception("Expected redirect from /loginosoba")

    # 2) redirect to IAM
    r2 = sess.get(r1.headers["Location"], allow_redirects=False)

    # 3) IAM entrypoint
    loc = r2.headers["Location"]
    if not loc.startswith("http"):
        loc = "https://tiamidsk.iedu.sk" + loc

    r3 = sess.get(loc, allow_redirects=False)
    html3 = r3.text

    # --- IAM chooser ---
    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        r4 = sess.get(f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}",
                      allow_redirects=False)
        html4 = r4.text
    else:
        html4 = html3

    # --- Login form ---
    if 'name="UserPassword"' in html4:
        authn_guid = re.search(r'name="AuthnGuid"[^>]+value="([^"]+)"', html4).group(1)
        token = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html4).group(1)

        r5 = sess.post(
            "https://tiamidsk.iedu.sk/authn/lp",
            data={
                "AuthnGuid": authn_guid,
                "UserName": USERNAME,
                "UserPassword": PASSWORD,
                "btn-continue": "Prihlásiť sa",
                "__RequestVerificationToken": token
            },
            allow_redirects=False
        )

        nxt = r5.headers["Location"]
        if not nxt.startswith("http"):
            nxt = "https://tiamidsk.iedu.sk" + nxt

        r6 = sess.get(nxt, allow_redirects=False)
        html6 = r6.text
    else:
        html6 = html4

    # --- SAML Response ---
    if "SAMLResponse" in html6:
        soup = BeautifulSoup(html6, "html.parser")
        form = soup.find("form")
        action = form.get("action")
        saml_raw = form.find("input", {"name": "SAMLResponse"}).get("value")
        relay = form.find("input", {"name": "RelayState"})
        relay_val = relay.get("value") if relay else ""

        saml_decoded = decode_html_entities(saml_raw)

        r7 = sess.post(
            action,
            data={"SAMLResponse": saml_decoded, "RelayState": relay_val},
            allow_redirects=False
        )

        # posledný redirect chain
        final = follow_redirects(f"{HOST}/Moj-Profil2", sess.cookies.get_dict())

        html_final = final.text

        # extrahovať token / GUIDy zo stránky
        xsrf = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html_final)
        xsrf_val = xsrf.group(1) if xsrf else None

        subj = extract_guid(html_final, "subjectGuid")
        logged = extract_guid(html_final, "loggedInPersonGuid")

        # cookies → safe dict
        cookie_dict = sess.cookies.get_dict()

        return {
            "success": True,
            "cookies": cookie_dict,
            "xsrfToken": xsrf_val,
            "subjectGuid": subj,
            "loggedInPersonGuid": logged
        }

    raise Exception("SAMLResponse not found – cannot login.")


# ============================================================
# 6) WRITE settings.py AUTOMATICALLY
# ============================================================
def update_settings(data):
    """Prepíše config/settings.py s novými tokenmi."""

    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config/settings.py"
    )

    cookies_str = "; ".join([f"{k}={v}" for k, v in data["cookies"].items()])

    new_content = f"""
# AUTO-GENERATED BY generate_tokens.py
HOST = "https://test-eprihlasky.iedu.sk"

WAIT_TIME_MIN = 1
WAIT_TIME_MAX = 3

CSRF = "{data['xsrfToken']}"
IAM_TOKEN = "{data['loggedInPersonGuid']}:{data['subjectGuid']}"
COOKIE_BUNDLE = "{cookies_str}"

SUBJEKT_GUID = "{data['subjectGuid']}"
PRIHLASENA_OSOBA_GUID = "{data['loggedInPersonGuid']}"

SKOLSKY_ROK_KOD_2026 = "2026/2027"
""".strip()

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n✔️ settings.py bol úspešne aktualizovaný.")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("🔐 Spúšťam SAML login (Python)…")
    data = saml_login()

    print("\n🎉 Login úspešný!")
    print("XSRF Token:", data["xsrfToken"])
    print("GUID subjektu:", data["subjectGuid"])
    print("GUID osoby:", data["loggedInPersonGuid"])
    print("Cookies:", data["cookies"])

    update_settings(data)
    print("\n🔥 Hotovo — teraz spusti ľubovoľný test.")
