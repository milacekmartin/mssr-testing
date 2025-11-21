# helpers/http.py
# ================
#
# HTTP helper s detailným logovaním a UTF-8 support

import json
import uuid
import urllib.parse


def evaluate_scenario(resp, name):
    """
    Vyhodnotí response a označí ho ako success/failure.
    """
    if resp.status_code in [200, 201]:
        resp.success()
    else:
        resp.failure(f"{name} FAILED → {resp.status_code} | {resp.text[:100]}")


def safe_encode_header(value):
    """
    Bezpečne enkóduje header hodnotu pre latin-1.
    Slovenské znaky (ZŠ) konvertuje na URL encoding.
    """
    if isinstance(value, str):
        try:
            # Skúsi latin-1
            value.encode('latin-1')
            return value
        except UnicodeEncodeError:
            # Ak zlyhá, použije URL encoding
            return urllib.parse.quote(value, safe=':/?#[]@!$&\'()*+,;=')
    return value


class HTTPHelper:
    """
    Helper trieda pre HTTP requesty s logovaním a context switching.
    """

    def __init__(self, client):
        self.client = client
        self.context = "UNKNOWN"
        self.dynamic_referer = None

    def set_context(self, ctx):
        """Nastaví context pre logovanie."""
        self.context = ctx

    def set_referer(self, referer):
        """Nastaví dynamický referer pre extended requesty."""
        self.dynamic_referer = safe_encode_header(referer)
        print(f"🔧 Nastavujem Referer → {referer}")

    def _log(self, method, url, resp):
        """Loguje HTTP request."""
        print(f"[{self.context}] {method} {url} → {resp.status_code}")

    def _prepare_headers(self, base_headers):
        """Pripraví headers s bezpečným kódovaním."""
        headers = base_headers.copy()
        
        # Enkóduj všetky header hodnoty
        for key, value in headers.items():
            headers[key] = safe_encode_header(value)
            
        return headers

    # ================================================================
    # SCENARIO METHODS (COMMON HEADERS)
    # ================================================================

    def post_scenario(self, url, payload, name):
        """POST request ktorý NEVOLÁ evaluate_scenario - pre safe_extract."""
        from config.headers import COMMON_HEADERS

        headers = self._prepare_headers(COMMON_HEADERS)

        with self.client.post(
            url,
            json=payload,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._log("POST", url, resp)
            # NEVOLÁ evaluate_scenario - safe_extract si to vyhodnotí sám
            return resp

    def post_scenario_auto(self, url, payload, name):
        """POST request s automatickým vyhodnotením - pre requesty bez safe_extract."""
        from config.headers import COMMON_HEADERS

        headers = self._prepare_headers(COMMON_HEADERS)

        with self.client.post(
            url,
            json=payload,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._log("POST", url, resp)
            evaluate_scenario(resp, name)  # Automatické vyhodnotenie
            return resp

    def get_scenario(self, url, params, name):
        """GET request s automatickým vyhodnotením."""
        from config.headers import COMMON_HEADERS

        headers = self._prepare_headers(COMMON_HEADERS)

        with self.client.get(
            url,
            params=params,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._log("GET", url, resp)
            evaluate_scenario(resp, name)
            return resp

    # ================================================================
    # EXTENDED METHODS (EXTENDED HEADERS + dynamický referer)
    # ================================================================

    def post_extended_scenario(self, url, payload, name):
        """POST request s extended headers - automatické vyhodnotenie."""
        from config.headers import EXTENDED_HEADERS

        headers = self._prepare_headers(EXTENDED_HEADERS)
        headers["x-correlation-id"] = str(uuid.uuid4())

        if hasattr(self, "dynamic_referer") and self.dynamic_referer:
            headers["Referer"] = self.dynamic_referer

        if "/api/vyhladanieMSaZS" in url:
            print(f"🔍 DEBUG Headers pre {url}:")
            print(f"   Referer: {headers.get('Referer', 'MISSING')}")
            csrf_short = headers.get('RequestVerificationToken', 'MISSING')[:50] + "..."
            iam_short = headers.get('x-token-descriptor', 'MISSING')[:50] + "..."
            print(f"   CSRF: {csrf_short}")
            print(f"   IAM: {iam_short}")
            cookie_short = headers.get('Cookie', 'MISSING')[:100] + "..."
            print(f"   Cookie: {cookie_short}")

        with self.client.post(
            url,
            json=payload,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._log("POST", url, resp)
            evaluate_scenario(resp, name)  # Automatické vyhodnotenie
            return resp