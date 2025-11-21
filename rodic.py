# rodic.py
# ===========================================
#
# Hlavný Locust runner obsahujúci 3 samostatné scenáre:
#   1) ZŠ-FLOW (1–31 krokov)
#   2) CREATE+DELETE (dieťa)
#   3) CREATE-APP+DELETE (dieťa + prihláška)
#
# Scenáre sú uložené v priečinku scenarios/
# a importované do tohto hlavného súboru.

from locust import HttpUser, task, between
from locust import tag

# config host + wait time
from config.settings import HOST, WAIT_TIME_MIN, WAIT_TIME_MAX

# HTTP helper s detailným logovaním
from helpers.http import HTTPHelper

# SCENÁRE
from scenarios.zs_prihlaska import run_zs_scenario
from scenarios.create_delete_child import run_create_delete_child
from scenarios.create_app_delete import run_create_app_delete


class MixScenarioUser(HttpUser):
    """
    Tento užívateľ vykonáva viacero scenárov s rôznymi váhami.
    """

    host = HOST
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)

    # --------------------------------------------------------------
    #  SCENÁR 0 – kompletná ZŠ prihláška (1–31 krokov)
    # --------------------------------------------------------------
    @tag("zs")
    @task(weight=3)
    def scenar_zs_prihlaska(self):
        http = HTTPHelper(self.client)
        http.set_context("ZS-FLOW")

        try:
            run_zs_scenario(self, http)
        except Exception as e:
            print(f"❌ Neočakávaná chyba ZS-FLOW: {e}")

    # --------------------------------------------------------------
    #  SCENÁR 1 – vytvorenie dieťaťa → zmazanie dieťaťa
    # --------------------------------------------------------------
    @tag("child_create_delete")
    @task(weight=2)
    def scenar_vytvor_a_zmaz_dieta(self):
        http = HTTPHelper(self.client)
        http.set_context("CREATE+DELETE")

        try:
            run_create_delete_child(self, http)
        except Exception as e:
            print(f"❌ Neočakávaná chyba CREATE+DELETE: {e}")

    # --------------------------------------------------------------
    #  SCENÁR 2 – vytvoriť dieťa -> prihláška -> zmazanie -> delete
    # --------------------------------------------------------------
    @tag("app_delete")
    @task(weight=2)
    def scenar_create_app_delete(self):
        http = HTTPHelper(self.client)
        http.set_context("CREATE-APP+DELETE")

        try:
            run_create_app_delete(self, http)
        except Exception as e:
            print(f"❌ Neočakávaná chyba CREATE-APP+DELETE: {e}")
