import sys, os, json, time, uuid
from datetime import datetime

from locust import HttpUser, task, between

# --------------------------------------------------------------------
# FIX PYTHON PATH
# --------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.random_names import generate_random_name
from config.env import HOST

# tvoje payloady – využívame ich namiesto ručného JSONu
from tests.child.payloads.child import build_base_child_payload
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_4,
    koncept_krok_5
)
from tests.vyhladavanie.payloads.search import build_search_payload


# ====================================================================
# USER LOGGER – každý používateľ má vlastný súbor
# ====================================================================
def create_user_logger(user_id: str):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    filename = os.path.join(log_dir, f"{user_id}.log")
    return open(filename, "a", encoding="utf-8")


# ====================================================================
# LOGOVACIA FUNKCIA (JSON STRUCTURED)
# ====================================================================
def log_json(logfile, user_id, step, url, payload, status, response):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_id,
        "step": step,
        "url": url,
        "payload": payload,
        "status": status,
        "response": response
    }
    logfile.write(json.dumps(entry, ensure_ascii=False, indent=2) + "\n\n")
    logfile.flush()


# ====================================================================
#  HLAVNÝ SCENÁR
# ====================================================================
class MixScenarioUser(HttpUser):
    host = HOST
    wait_time = between(1, 3)

    def on_start(self):
        """
        Každý user dostane unique ID + vlastný logovací súbor.
        SAML login sa robí raz pre celý test → caching v environment.
        """
        self.user_id = f"USER-{uuid.uuid4().hex[:6].upper()}"
        self.log = create_user_logger(self.user_id)

        # SAML LOGIN cez shared session (BEZ duplicít)
        if not hasattr(self.environment, "auth"):
            print("🔐 Performing SAML login once for all users…")
            self.environment.auth = saml_login()

        self.auth = self.environment.auth

        print(f"👤 {self.user_id} READY")

    # ----------------------------------------------------------------
    # UNIFIED REQUEST FUNCTION
    # ----------------------------------------------------------------
    def api_post(self, step_name, endpoint, payload):
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "RequestVerificationToken": self.auth.csrf,
            "X-Requested-With": "XMLHttpRequest",
            "x-token-descriptor": self.auth.token_desc,
            "Cookie": self.auth.cookie_bundle,
        }

        with self.client.post(
            endpoint,
            json=payload,
            headers=headers,
            catch_response=True,
            name=step_name
        ) as resp:

            # logovanie do súboru
            try:
                resp_json = resp.json()
            except:
                resp_json = resp.text

            log_json(
                self.log,
                self.user_id,
                step_name,
                endpoint,
                payload,
                resp.status_code,
                resp_json
            )

            if resp.status_code != 200:
                resp.failure(f"Status {resp.status_code}")

            return resp

    # ====================================================================
    # SCENÁR: ZŠ PRIHLÁŠKA
    # ====================================================================
    @task(weight=3)
    def scenar_zs(self):
        step = "SCENÁR ZŠ"

        # 1. Generujeme dieťa
        fn, ln = generate_random_name()
        payload_child = build_base_child_payload(fn, ln)
        payload_child["subjektGUID"] = self.auth.subj_guid

        resp_child = self.api_post(f"{step} 1/30 - Vytvorenie dieťaťa",
                                   "/api/zapisAModifikaciaDietata",
                                   payload_child)

        try:
            dieta_guid = resp_child.json().get("dieta", {}).get("guid")
        except:
            dieta_guid = None

        if not dieta_guid:
            dieta_guid = uuid.uuid4().hex
            print(f"⚠️ {self.user_id}: fallback GUID → {dieta_guid}")

        # 2. Koncept krok 1
        payload_k1 = koncept_krok_1(dieta_guid)
        resp_k1 = self.api_post(f"{step} 2/30 - Koncept krok 1",
                                "/api/zapisAModifikaciaKonceptuPrihlasky",
                                payload_k1)

        prihlaska_guid = None
        try:
            prihlaska_guid = resp_k1.json().get("prihlaska", {}).get("prihlaskaGUID")
        except:
            pass

        if not prihlaska_guid:
            prihlaska_guid = uuid.uuid4().hex

        # 3. Koncept krok 2
        payload_k2 = koncept_krok_2(dieta_guid, prihlaska_guid)
        self.api_post(f"{step} 3/30 - Koncept krok 2",
                      "/api/zapisAModifikaciaKonceptuPrihlasky",
                      payload_k2)

        # 4. Vyhľadávanie MS/ZS  (tvoj payload builder)
        search_payload = build_search_payload(page_size=20, text="bratislava")
        self.api_post(f"{step} 4/30 - Vyhľadávanie ZŠ",
                      "/api/vyhladanieMSaZS",
                      search_payload)

        # 5. Koncept krok 3
        payload_k3 = koncept_krok_3(dieta_guid, prihlaska_guid)
        self.api_post(f"{step} 5/30 - Koncept krok 3",
                      "/api/zapisAModifikaciaKonceptuPrihlasky",
                      payload_k3)

        print(f"🏁 {self.user_id}: SCENÁR ZŠ dokončený.")


    # ====================================================================
    # JEDNODUCHÝ MŠ SCENÁR (pridanie dieťaťa)
    # ====================================================================
    @task(weight=2)
    def scenar_ms(self):
        step = "SCENÁR MŠ"

        fn, ln = generate_random_name()

        payload = build_base_child_payload(fn, ln)
        payload["subjektGUID"] = self.auth.subj_guid

        self.api_post(f"{step} 1/3 - Zápis dieťaťa",
                      "/api/zapisAModifikaciaDietata",
                      payload)

        self.api_post(f"{step} 2/3 - Zoznam detí",
                      "/api/vratenieZoznamuDeti",
                      {"guid": self.auth.subj_guid, "lenPlatne": True})

        self.api_post(f"{step} 3/3 - Zoznam prihlášok",
                      "/api/vratenieZoznamuPrihlasokSubjektu",
                      {"SubjektGUID": self.auth.subj_guid})

        print(f"🏁 {self.user_id}: SCENÁR MŠ dokončený.")
