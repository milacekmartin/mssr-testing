import sys, os, uuid
from locust import HttpUser, task, between

# FIX PYTHON PATH
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from login.saml_login import saml_login
from helpers.http_wrapper import HttpWrapper
from scenarios.zs_prihlaska import run_zs_scenario
from config.env import HOST


class ZsScenarioUser(HttpUser):
    host = HOST
    wait_time = between(1, 2)

    def on_start(self):
        # unique user id (pre logovanie + debug)
        self.user_id = f"ZSUSER-{uuid.uuid4().hex[:6].upper()}"

        # do SAML login only once per test
        if not hasattr(self.environment, "auth"):
            print("🔐 Performing SAML login (cached for all users)…")
            self.environment.auth = saml_login()

        # každý user používa rovnaký login objekt
        self.auth = self.environment.auth

        # HTTP wrapper pre volania API
        self.http = HttpWrapper(self)

        print(f"👤 {self.user_id} READY (ZŠ scenár)")

    @task
    def run_scenario(self):
        run_zs_scenario(self, self.http)
