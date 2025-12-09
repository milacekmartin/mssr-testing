# login/saml_login.py

import re, html, json, requests
from bs4 import BeautifulSoup

from config.credentials import USERNAME, PASSWORD
from config.env import HOST, IMPORTANT_COOKIES
from config.saml import SAML_LOGIN_CONFIG


class SamlLoginResult:
    def __init__(self, session, csrf, token_desc, subj_guid, logged_guid, cookie_bundle):
        self.session = session
        self.csrf = csrf
        self.token_desc = token_desc
        self.subj_guid = subj_guid
        self.logged_guid = logged_guid
        self.cookie_bundle = cookie_bundle


def saml_login():
    print("🔐 SAML LOGIN...")

    session = requests.Session()

    # 1) GET /loginosoba
    r1 = session.get(SAML_LOGIN_CONFIG["login_osoba"], allow_redirects=False)
    redirect1 = r1.headers.get("Location")

    # 2) GET redirect1 → bude to TIAM redirect
    r2 = session.get(redirect1, allow_redirects=False)
    redirect2 = r2.headers.get("Location")
    if not redirect2.startswith("http"):
        redirect2 = SAML_LOGIN_CONFIG["tiam_base"] + redirect2

    # 3) Získame TIAM login page
    r3 = session.get(redirect2, allow_redirects=False)
    html3 = r3.text

    # Niekedy tam je výber prihlasovania
    if "Vyberte spôsob prihlásenia" in html3:
        guid = re.search(r"authnGuid=([a-f0-9\-]+)", html3).group(1)
        redirect3 = f"{SAML_LOGIN_CONFIG['tiam_base']}/authn/lp?authnGuid={guid}"
        r3 = session.get(redirect3, allow_redirects=False)
        html3 = r3.text

    # Extrakcia polí
    authn_guid = re.search(r'name="AuthnGuid"[^>]+value="([^"]+)"', html3).group(1)
    request_ver_token = re.search(
        r'RequestVerificationToken"[^>]+value="([^"]+)"', html3
    ).group(1)

    # 4) POST prihlasovanie
    r4 = session.post(
        SAML_LOGIN_CONFIG["tiam_login"],
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
        redirect3 = SAML_LOGIN_CONFIG["tiam_base"] + redirect3

    # 5) Získame SAML Response
    r5 = session.get(redirect3, allow_redirects=False)
    soup = BeautifulSoup(r5.text, "html.parser")

    saml_raw = soup.find("input", {"name": "SAMLResponse"}).get("value")
    relay = soup.find("input", {"name": "RelayState"}).get("value")

    # 6) Odoslanie na ACS
    acs_result = session.post(
        SAML_LOGIN_CONFIG["acs_url"],
        data={"RelayState": relay, "SAMLResponse": html.unescape(saml_raw)},
        allow_redirects=False,
    )

    # 7) Finalizácia loginu
    home = session.get(acs_result.headers["Location"])

    # 8) extrakcia tokenov
    profile = session.get(f"{HOST}/Moj-profil2")
    html_profile = profile.text

    # CSRF
    csrf_match = re.search(
        r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html_profile
    )
    csrf = csrf_match.group(1) if csrf_match else None

    # userData
    m_user = re.search(
        r"window\.userData\s*=\s*(\{.*?\});", html_profile, re.DOTALL
    )
    userdata = json.loads(m_user.group(1))

    token_desc = userdata.get("tokenDescriptor")

    person = userdata.get("person", {})
    subj_guid = person.get("subjectGuid")
    logged_guid = person.get("loggedInPersonGuid")

    # Cookies
    parts = []
    for cookie in session.cookies:
        if cookie.name in IMPORTANT_COOKIES:
            parts.append(f"{cookie.name}={cookie.value}")

    cookie_bundle = "; ".join(parts)

    return SamlLoginResult(
        session,
        csrf,
        token_desc,
        subj_guid,
        logged_guid,
        cookie_bundle
    )
