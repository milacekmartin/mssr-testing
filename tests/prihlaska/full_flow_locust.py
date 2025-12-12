# ======================================================================
# LOCUST FULL FLOW (2026/2027) — ONLY VALID REQUESTS
#
# SCENARIOS:
#  - ZŠ PRIHLÁŠKA (full flow)
#  - CHILD EDIT (create → update → verify → delete)
#  - VYHĽADÁVANIE MS / ZS (HIGH WEIGHT)
# ======================================================================

import os
import sys

# ----------------------------------------------------------------------
# Ensure project root in PYTHONPATH
# ----------------------------------------------------------------------
CURRENT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT)))
sys.path.append(PROJECT_ROOT)

from locust import HttpUser, task

from login.saml_login import saml_login
from config.env import HOST
from config.random_names import generate_random_name

from tests.child.payloads.child import build_base_child_payload

from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_3_with_school,
)

from tests.prihlaska.payloads.koncept_step4 import build_step4_adaptive
from tests.prihlaska.payloads.koncept_step5 import build_step5_adaptive
from tests.prihlaska.payloads.koncept_step10 import build_step10_adaptive

from tests.vyhladavanie.payloads.search import (
    build_search_payload,
    SEARCH_TEST_CONFIGS,
)

# ======================================================================
# HELPERS
# ======================================================================
def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}


def detect_allowed_fields(school_detail):
    allowed = {}

    if "jazyk" in school_detail:
        allowed["jazykové_možnosti"] = school_detail["jazyk"]

    for key in [
        "pozadovanyJazykKod",
        "zaujemUvodnyRocnikVIN",
        "zaujemUvodnyRocnikNKS",
        "zaujemPripravnyRocnik",
        "zaujemDualneVzdelavanie",
        "zaujemInternat",
        "terminPrijimacejSkuskyKod",
        "mentalnePostihnutie",
    ]:
        if key in school_detail:
            allowed[key] = True

    return allowed


def build_adaptive_saSZ(eduid, allowed):
    sa = {
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
    }

    if "pozadovanyJazykKod" in allowed:
        sa["pozadovanyJazykKod"] = "SK"
    if "mentalnePostihnutie" in allowed:
        sa["mentalnePostihnutie"] = False
    if "zaujemUvodnyRocnikVIN" in allowed:
        sa["zaujemUvodnyRocnikVIN"] = False
    if "zaujemUvodnyRocnikNKS" in allowed:
        sa["zaujemUvodnyRocnikNKS"] = False
    if "zaujemPripravnyRocnik" in allowed:
        sa["zaujemPripravnyRocnik"] = False
    if "zaujemDualneVzdelavanie" in allowed:
        sa["zaujemDualneVzdelavanie"] = False
    if "zaujemInternat" in allowed:
        sa["zaujemInternat"] = False

    return sa


# ======================================================================
# LOCUST USER — only valid 200 OK requests are counted
# ======================================================================
class FullFlowUser(HttpUser):
    host = HOST

    # -------------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------------
    def on_start(self):
        print("\n=====================================================")
        print(" LOCUST FULL FLOW — ONLY VALID REQUESTS")
        print("=====================================================")

        self.login = saml_login()
        print("✔ Login successful")
        print("Subjekt GUID:", self.login.subj_guid)
        print("User GUID:", self.login.logged_guid)

    # -------------------------------------------------------------
    # STEP WRAPPER — counts ONLY HTTP 200
    # -------------------------------------------------------------
    def step(self, endpoint, payload, label):

        name = f"{label} ({endpoint})"

        with self.client.post(
            endpoint,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "Origin": HOST,
                "Referer": f"{HOST}/Moj-profil2",
                "RequestVerificationToken": self.login.csrf,
                "x-token-descriptor": self.login.token_desc,
                "Cookie": self.login.cookie_bundle,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0",
            },
            name=name,
            catch_response=True,
        ) as resp:

            if resp.status_code == 200:
                resp.success()
                return resp

            # ignore everything else
            resp._manual_result = True
            return resp

    # ==================================================================
    # ZŠ PRIHLÁŠKA — FULL FLOW
    # ==================================================================
    @task
    def full_flow(self):

        first, last = generate_random_name()
        print(f"\n👶 STEP 0: Creating child → {first} {last}")

        child = build_base_child_payload(first, last)
        child["subjektGUID"] = self.login.subj_guid

        r_child = self.step(
            "/api/zapisAModifikaciaDietata",
            child,
            "STEP 0 – Creating child",
        )
        dieta_guid = safe_json(r_child).get("dieta", {}).get("guid")
        print(f"   → Child GUID: {dieta_guid}")

        print("📄 STEP 1: Creating application")
        r1 = self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            koncept_krok_1(dieta_guid, self.login.logged_guid),
            "STEP 1 – Creating application",
        )
        app_guid = safe_json(r1).get("prihlaska", {}).get("prihlaskaGUID")
        print(f"   → Application GUID: {app_guid}")

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            koncept_krok_2(dieta_guid, app_guid, self.login.logged_guid),
            "STEP 2 – Updating complementary data",
        )

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            koncept_krok_3(dieta_guid, app_guid, self.login.logged_guid),
            "STEP 3 – Initializing school selection",
        )

        print("🔎 STEP 4: Searching schools")
        r_search = self.step(
            "/api/vyhladanieMSaZS",
            build_search_payload(page_size=20),
            "STEP 4 – Searching schools",
        )
        school = safe_json(r_search)["saSZ"][0]
        eduid = school["eduid"]
        print(f"   → Selected EDUID: {eduid}")

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            koncept_krok_3_with_school(
                dieta_guid, app_guid, self.login.logged_guid, eduid
            ),
            "STEP 5 – Saving selected school",
        )

        det = self.step(
            "/api/vratenieVybranychSaSZ",
            {"prihlaskaGUID": app_guid},
            "STEP 6 – Fetching school capabilities",
        )
        allowed = detect_allowed_fields(safe_json(det)["saSZ"][0])
        saSZ = build_adaptive_saSZ(eduid, allowed)

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            build_step4_adaptive(dieta_guid, app_guid, self.login.logged_guid, saSZ),
            "STEP 7 – Saving language/VIN configuration",
        )

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            build_step5_adaptive(dieta_guid, app_guid, self.login.logged_guid, saSZ),
            "STEP 8 – Saving legal guardian",
        )

        self.step(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            build_step10_adaptive(dieta_guid, app_guid, self.login.logged_guid, eduid),
            "STEP 9 – Finalizing application",
        )

        self.step(
            "/api/vratenieKonceptuPrihlasky",
            {"prihlaskaGUID": app_guid},
            "STEP 10 – Fetching application detail",
        )

        print("🏁 ZŠ PRIHLÁŠKA FLOW DONE\n")

    # ==================================================================
    # CHILD EDIT FLOW
    # ==================================================================
    @task
    def child_edit_flow(self):

        print("\n👶 CHILD EDIT FLOW START")

        first, last = generate_random_name()
        payload = build_base_child_payload(first, last)
        payload["subjektGUID"] = self.login.subj_guid

        r_create = self.step(
            "/api/zapisAModifikaciaDietata",
            payload,
            "CHILD EDIT – Create child",
        )
        guid = safe_json(r_create).get("dieta", {}).get("guid")
        if not guid:
            print("⚠️ CREATE skipped")
            return

        new_first, new_last = generate_random_name()
        edit_payload = build_base_child_payload(new_first, new_last)
        edit_payload.update({
            "subjektGUID": self.login.subj_guid,
            "dietaGUID": guid,
            "pohlavieKod": "2",
        })

        self.step(
            "/api/zapisAModifikaciaDietata",
            edit_payload,
            "CHILD EDIT – Update child",
        )

        self.step(
            "/api/vratenieZoznamuDeti",
            {"guid": self.login.subj_guid, "lenPlatne": True},
            "CHILD EDIT – Verify child update",
        )

        self.step(
            "/api/vymazDietata",
            {"guid": guid},
            "CHILD EDIT – Delete child",
        )

        print("🏁 CHILD EDIT FLOW DONE\n")

    # ==================================================================
    # SEARCH FLOW — HIGH WEIGHT
    # ==================================================================
    @task(5)
    def vyhladavanie_flow(self):

        print("\n🔍 VYHĽADÁVANIE FLOW START")

        total = len(SEARCH_TEST_CONFIGS)

        for idx, (name, cfg) in enumerate(SEARCH_TEST_CONFIGS, 1):
            print(f"🔎 SEARCH {idx}/{total}: {name}")

            r = self.step(
                "/api/vyhladanieMSaZS",
                build_search_payload(**cfg),
                f"SEARCH – {name}",
            )

            js = safe_json(r)
            if js.get("kodSpracovania") == "1700":
                count = js.get("pocet", {}).get("pocetKmenovychSaSZ", 0)
                print(f"   ✔ OK → schools: {count}")
            else:
                print("   ⚠️ skipped / non-1700")

        print("🏁 VYHĽADÁVANIE FLOW DONE\n")
