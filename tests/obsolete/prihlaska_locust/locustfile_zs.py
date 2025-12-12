import sys, os, uuid
from locust import HttpUser, task, between, events

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from login.saml_login import saml_login
from helpers.http_wrapper import HttpWrapper
from config.env import HOST
from tests.obsolete.prihlaska_locust.full_flow_locust import run_full_flow_locust


class ZsScenarioUser(HttpUser):
    host = HOST
    wait_time = between(1, 2)

    def on_start(self):
        self.user_id = f"ZSUSER-{uuid.uuid4().hex[:6].upper()}"

        if not hasattr(self.environment, "auth"):
            print("🔐 Performing SAML login (shared for all Locust users)…")
            self.environment.auth = saml_login()

        self.auth = self.environment.auth
        self.http = HttpWrapper(self)

        print(f"👤 {self.user_id} READY → running adaptive ZŠ scenario")

    @task
    def run_scenario(self):
        try:
            run_full_flow_locust(self.auth, self.http)
        except Exception as e:
            events.request_failure.fire(
                request_type="FLOW",
                name="ZS Full Flow",
                response_time=0,
                exception=e
            )
