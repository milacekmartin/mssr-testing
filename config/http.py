# config/http.py
# ============================================================
# HTTP CONFIGURATION (shared across project)
# ============================================================

from config.env import HOST

# ------------------------------------------------------------
# STATIC DEFAULTS
# ------------------------------------------------------------
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}

USER_AGENT = "Mozilla/5.0 (Habitable Test Client)"


# ------------------------------------------------------------
# AUTHENTICATED HEADERS BUILDER
# ------------------------------------------------------------
def build_headers(login, *, referer_suffix="/Moj-profil2"):
    """
    Build authenticated headers for API calls.
    """
    headers = dict(DEFAULT_HEADERS)

    headers.update({
        "Origin": HOST,
        "Referer": f"{HOST}{referer_suffix}",
        "RequestVerificationToken": login.csrf,
        "x-token-descriptor": login.token_desc,
        "Cookie": login.cookie_bundle,
        "User-Agent": USER_AGENT,
    })

    return headers
