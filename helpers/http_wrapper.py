# helpers/http_wrapper.py
# Unified HttpWrapper for Locust compatibility

from config.env import HOST

class HttpWrapper:
    """
    Thin wrapper over locust's self.client:
    - adds correct headers (UI-identical)
    - reuses SAML auth cookies & tokens
    - provides http.post() and http.get()
    """

    def __init__(self, user):
        self.user = user              # Locust user (HttpUser)
        self.context = ""             # optional reporting context
        self.referer = f"{HOST}/Moj-profil2"

    # ---------------------------------------------------------
    # Context / referer setters (optional)
    # ---------------------------------------------------------
    def set_context(self, ctx: str):
        self.context = ctx

    def set_referer(self, url: str):
        self.referer = url

    # ---------------------------------------------------------
    # Build UI-level request headers
    # ---------------------------------------------------------
    def _headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": HOST,
            "Referer": self.referer,
            "RequestVerificationToken": self.user.auth.csrf,
            "x-token-descriptor": self.user.auth.token_desc,
            "Cookie": self.user.auth.cookie_bundle,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0",
        }

    # ---------------------------------------------------------
    # POST wrapper for Locust
    # ---------------------------------------------------------
    def post(self, endpoint: str, json=None, name=None):
        name = name or endpoint
        label = f"{self.context} | {name}" if self.context else name

        with self.user.client.post(
            endpoint,
            json=json,
            headers=self._headers(),
            name=label,
            catch_response=True
        ) as resp:

            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:300]}")
            return resp

    # ---------------------------------------------------------
    # GET wrapper for Locust
    # ---------------------------------------------------------
    def get(self, endpoint: str, params=None, name=None):
        name = name or endpoint
        label = f"{self.context} | {name}" if self.context else name

        with self.user.client.get(
            endpoint,
            params=params,
            headers=self._headers(),
            name=label,
            catch_response=True
        ) as resp:

            if resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:300]}")
            return resp
