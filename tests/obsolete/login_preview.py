import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import HOST

USERNAME = ""
PASSWORD = ""


def decode_html_entities(s: str):
    import html
    return html.unescape(s)


def follow_redirects(url, cookies, max_hops=15):
    sess = requests.Session()
    hops = 0
    while hops < max_hops:
        resp = sess.get(url, cookies=cookies, allow_redirects=False)
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


def extract_window_userdata(html: str):
    match = re.search(r"window\.userData\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not match:
        return None

    raw_json = match.group(1)

    try:
        return json.loads(raw_json.rstrip(";"))
    except:
        try:
            cleaned = raw_json.replace(";", "")
            return json.loads(cleaned)
        except:
            return None


def extract_xsrf(html: str):
    m = re.search(r'RequestVerificationToken"[^>]+value="([^"]+)"', html)
    return m.group(1) if m else None


def saml_login_preview():
    sess = requests.Session()

    # 1) GET /loginosoba
    r1 = sess.get(f"{HOST}/loginosoba?returnurl=%2F", allow_redirects=False)

    # 2) IAM redirect
    r2 = sess.get(r1.headers["Location"], allow_redirects=False)

    # 3) IAM entry
    loc = r2.headers["Location"]
    if not loc.startswith("http"):
        loc = "https://tiamidsk.iedu.sk" + loc

    r3 = sess.get(loc, allow_redirects=False)
    html3 = r3.text

    # 4) login form OR chooser
    if "authnGuid" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        r4 = sess.get(
            f"https://tiamidsk.iedu.sk/authn/lp?authnGuid={guid}",
            allow_redirects=False
        )
        html4 = r4.text
    else:
        html4 = html3

    # 5) login form
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

    # 6) SAML response
    if "SAMLResponse" not in html6:
        raise Exception("SAMLResponse form not found")

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

    # 7) load user profile
    final = follow_redirects(f"{HOST}/Moj-Profil2", sess.cookies.get_dict())
    html_final = final.text

    xsrf = extract_xsrf(html_final)
    cookie_dict = sess.cookies.get_dict()

    # load homepage
    homepage = requests.get(f"{HOST}/", cookies=cookie_dict).text
    userdata = extract_window_userdata(homepage)

    logged = userdata.get("person", {}).get("loggedInPersonGuid") if userdata else None
    subj = userdata.get("person", {}).get("subjectGuid") if userdata else None

    return {
        "success": True,
        "xsrfToken": xsrf,
        "cookies": cookie_dict,
        "iamToken": cookie_dict.get("IamTokenDescriptor"),
        "loggedInPersonGuid": logged,
        "subjectGuid": subj,
    }


if __name__ == "__main__":

    data = saml_login_preview()

    if "--json" in sys.argv:
        # vypíš len čistý JSON
        print(json.dumps(data, indent=2, ensure_ascii=False))
        sys.exit(0)

    # default verbose print
    print("\n🎉 Login OK\n")
    print("👉 XSRF Token:\n", data["xsrfToken"])
    print("\n👉 X-Token-Descriptor:\n", data["iamToken"])
    print("\n👉 loggedInPersonGuid:\n", data["loggedInPersonGuid"])
    print("\n👉 subjectGuid:\n", data["subjectGuid"])
    print("\n👉 COOKIES:")
    print(json.dumps(data["cookies"], indent=2, ensure_ascii=False))
    print("\n🔥 Hotovo.\n")
