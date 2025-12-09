import json
from config.env import HOST

class HttpWrapper:
    def __init__(self, user):
        self.user = user
        self.context = ""
        self.referer = f"{HOST}/Moj-profil2"

    def set_context(self, ctx):
        self.context = ctx

    def set_referer(self, url):
        self.referer = url

    def _headers(self):
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "RequestVerificationToken": self.user.auth.csrf,
            "x-token-descriptor": self.user.auth.token_desc,
            "Cookie": self.user.auth.cookie_bundle,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.referer
        }

    def post_scenario(self, endpoint, payload, name):
        with self.user.client.post(
            endpoint,
            json=payload,
            headers=self._headers(),
            name=f"{self.context} | {name}",
            catch_response=True
        ) as resp:
            return resp

    def post_extended_scenario(self, endpoint, payload, name):
        headers = self._headers()
        headers["Accept"] = "application/json"
        with self.user.client.post(
            endpoint,
            json=payload,
            headers=headers,
            name=f"{self.context} | {name}",
            catch_response=True
        ) as resp:
            return resp

    def get_scenario(self, endpoint, params, name):
        with self.user.client.get(
            endpoint,
            params=params,
            headers=self._headers(),
            name=f"{self.context} | {name}",
            catch_response=True
        ) as resp:
            return resp
