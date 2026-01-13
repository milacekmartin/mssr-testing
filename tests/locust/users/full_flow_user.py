# tests/locust/users/full_flow_user.py

from locust import HttpUser, task
from locust.exception import StopUser

from config.env import HOST
from tests.locust.common.shared_login import get_shared_login

from tests.locust.flows.child_flow import run_child_flow
from tests.locust.flows.zs_flow import run_zs_flow
from tests.locust.flows.ss_flow import run_ss_flow
from tests.locust.flows.search_flow import run_search_flow
from tests.locust.flows.cleanup_flow import run_random_cleanup_flow


class FullFlowUser(HttpUser):
    host = HOST

    def on_start(self):
        print("\n=====================================================")
        print(" LOCUST FULL FLOW — CHILD + ZS + SS + SEARCH ")
        print("=====================================================")

        try:
            self.login = get_shared_login()

        except Exception as e:
            print("\n❌ SHARED LOGIN FAILED")
            print(f"   {type(e).__name__}: {e}\n")
            raise StopUser()

    # ----------------------------------------------------------
    # TASKS – BUSINESS / MAINTENANCE LOAD
    # ----------------------------------------------------------

    # 🔹 ZŠ flow
    @task(1)
    def zs(self):
        run_zs_flow(self)

    # 🔹 SŠ flow
    @task(10)
    def ss(self):
        run_ss_flow(self)

    # 🔹 SEARCH-only load
    @task(1)
    def search(self):
        run_search_flow(self)

    # 🔹 CHILD-only CRUD
    @task(1)
    def child(self):
        run_child_flow(self)

    # 🔹 RANDOM CLEANUP (ZŠ + SŠ)
    @task(5)
    def cleanup(self):
        run_random_cleanup_flow(self)
