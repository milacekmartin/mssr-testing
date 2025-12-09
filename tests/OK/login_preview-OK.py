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
# HTML decode
# ============================================================
def decode_html_entities(s: str):
    import html
    return html.unescape(s)


# ============================================================
# Follow redirects manually
# ============================================================
def follow_redirects(url, cookies, max_hops=15):
    sess = requests.Session()
    hops = 0

    while hops < max_hops:
        resp = sess.get(url, cookies=cookies, allow_redirects=False)

        # not a redirect → final response
        if resp.status_code < 300 or resp.status_code >= 400:
            return resp

        loc = resp.headers.get("Location")
        if not loc:
            return resp

        if not loc.startswith("http"):
            loc = urljoin(HOST, loc)

        url = loc
        hops += 1

    raise Exception("Too many redirects")


# ============================================================
# Extract window.userData JSON object
# ============================================================
def extract_window_userdata(html: str):
    m = re.search(r"window\.userData\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not m:
        return None

    json_text = m.group(1)

    # Fix JSON (replace single-quoted keys, remove trailing semicolon)
    try:
        data = json.loads(json_text)
        return data
    except:
        # fallback regex cleaning
        cleaned = json_text.replace(";", "")
        try:
            return json.loads(cleaned)
        except:
            return None


# ============================================================
# Extract XSRF token from HTML
# ============================================================
def extract_xsrf(html: str):
    m = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html)
    return m.group(1) if m else None


# ============================================================
# Python SAML login (Cypress port)
# ============================================================
def saml_login():
    sess = requests.Session()

    # STEP 1 /loginosoba
    r1 = sess.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)

    # STEP 2 redirect to IAM
    r2 = sess.get(r1.headers["Location"], allow_redirects=False)

    # STEP 3 IAM entry
    loc = r2.headers["Location"]
    if not loc.startswith("http"):
        loc = "https://tiamidsk.iedu.sk" + loc

    r3 = sess.get(loc, allow_redirects=False)
    html3 = r3.text

    # IAM chooser
    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\\-]+)", html3).group(1)
        r4 = sess.get(f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}",
                      allow_redirects=False)
        html4 = r4.text
    else:
        html4 = html3

    # login form
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

    # SAML final form
    if "SAMLResponse" in html6:
        soup = BeautifulSoup(html6, "html.parser")
        form = soup.find("form")
        saml_raw = form.find("input", {"name": "SAMLResponse"}).get("value")
        relay = form.find("input", {"name": "RelayState"})
        relay_val = relay.get("value") if relay else ""
        action = form.get("action")

        saml_decoded = decode_html_entities(saml_raw)

        sess.post(action,
                  data={"SAMLResponse": saml_decoded, "RelayState": relay_val},
                  allow_redirects=False)

        # now load profile with cookies
        final = follow_redirects(f"{HOST}/Moj-Profil2", sess.cookies.get_dict())
        html_final = final.text

        xsrf = extract_xsrf(html_final)
        cookie_dict = sess.cookies.get_dict()

        # also load homepage like browser
        browser_html = requests.get(f"{HOST}/", cookies=cookie_dict).text

        # try extract window.userData
        userdata = extract_window_userdata(browser_html)

        logged = None
        subj = None

        if userdata:
            person = userdata.get("person", {})
            logged = person.get("loggedInPersonGuid")
            subj = person.get("subjectGuid")

        return {
            "xsrfToken": xsrf,
            "cookies": cookie_dict,
            "iamToken": cookie_dict.get("IamTokenDescriptor"),
            "windowUserData": userdata,
            "loggedInPersonGuid": logged,
            "subjectGuid": subj,
            "html": browser_html
        }

    raise Exception("SAMLResponse not found")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":

    print("\n🔐 Spúšťam SAML login…\n")

    data = saml_login()

    print("🎉 Login OK\n")

    print("👉 XSRF Token:\n", data["xsrfToken"])
    print("\n👉 X-Token-Descriptor (IAM TOKEN):\n", data["iamToken"])

    print("\n👉 loggedInPersonGuid:\n", data["loggedInPersonGuid"])
    print("\n👉 subjectGuid:\n", data["subjectGuid"])

    print("\n👉 COOKIES:")
    print(json.dumps(data["cookies"], indent=2, ensure_ascii=False))

    html = data["html"]

    with open("last_profile_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n📄 Full HTML uložené do last_profile_page.html")

    print("\n🔥 Hotovo – všetky údaje extrahované.\n")
