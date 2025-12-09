# config/saml.py

from config.env import TIAM_BASE, LOGIN_OSOBA_URL, ACS_URL

SAML_LOGIN_CONFIG = {
    "tiam_base": TIAM_BASE,
    "login_osoba": LOGIN_OSOBA_URL,
    "tiam_login": f"{TIAM_BASE}/authn/lp",
    "acs_url": ACS_URL,
}
