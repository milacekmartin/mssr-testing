# ======================================================================
# LOCUST – SEARCH (MS / ZS / SS)
# SINGLE SOURCE OF TRUTH: /api/vrateniePoloziekFiltrov
# ======================================================================

import os
import sys
import re
import random
from locust import HttpUser, TaskSet, task, between

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.env import HOST

# ----------------------------------------------------------------------
SCHOOL_YEAR = "2026/2027"
LAT = 48.586405
LON = 19.14219

BASE_MS_ZS = {
    "skolskyRokKod": SCHOOL_YEAR,
    "pocetZaznamovNaStranku": 20,
    "cisloStranky": 1,
    "zemepisnaSirka": LAT,
    "zemepisnaDlzka": LON,
}

SS_SEARCH_URL = "/api/vyhladanieSaSZSS"

# ======================================================================
class SearchTasks(TaskSet):

    # ------------------------------------------------------------------
    def on_start(self):
        print("\n=========================================")
        print(" 🔍 LOCUST SEARCH – MS / ZS / SS")
        print("=========================================\n")

        print("🔐 SAML LOGIN...")
        self.user.login = saml_login()
        print("✔ LOGIN OK")

        self.client.cookies.clear()
        for c in self.user.login.session.cookies:
            self.client.cookies.set(c.name, c.value)

        self.filters = {}

        self.refresh_csrf()
        self.load_filters()

    # ------------------------------------------------------------------
    def headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": HOST,
            "Referer": f"{HOST}/Najst-skolu",
            "RequestVerificationToken": self.user.csrf,
            "X-Requested-With": "XMLHttpRequest",
            "x-token-descriptor": self.user.login.token_desc,
        }

    # ------------------------------------------------------------------
    def refresh_csrf(self):
        r = self.client.get("/Najst-skolu", name="INIT CSRF")
        m = re.search(r'value="([^"]+)"', r.text)
        if not m:
            raise RuntimeError("CSRF token not found")
        self.user.csrf = m.group(1)

    # ------------------------------------------------------------------
    def load_filters(self):
        print("▶ LOAD FILTERS (MS + ZS + SS)")
        with self.client.post(
            "/api/vrateniePoloziekFiltrov",
            json={"skolskyRokKod": SCHOOL_YEAR, "ms": True, "zs": True},
            headers=self.headers(),
            name="FILTERS MS+ZS",
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure("filters load failed")
                return

            d = r.json()

            # 🔒 SINGLE SOURCE OF TRUTH
            self.filters["distance"] = d.get("vzdialenost") or []
            self.filters["languages"] = d.get("jazyk") or []
            self.filters["ownership"] = d.get("formaVlastnictva") or []
            self.filters["ms_types"] = d.get("skola") or []
            self.filters["special"] = d.get("specialnaSkola") or []

            r.success()

    # ==============================================================
    @task(3)
    def ms_basic(self):
        if not self.filters["distance"]:
            return

        dist = random.choice(self.filters["distance"])
        print(f"▶ MS / BASIC – {dist['nazov']}")

        payload = {
            **BASE_MS_ZS,
            "ms": True,
            "zs": False,
            "vzdialenostKod": dist["kod"],
        }

        self.client.post(
            "/api/vyhladanieMSaZS",
            json=payload,
            headers=self.headers(),
            name="MS / SEARCH (BASIC)",
        )

    # ==============================================================
    @task(4)
    def ms_all_filters(self):
        if not self.filters["distance"]:
            return

        dist = random.choice(self.filters["distance"])

        payload = {
            **BASE_MS_ZS,
            "ms": True,
            "zs": False,
            "vzdialenostKod": dist["kod"],
        }

        if self.filters["languages"]:
            l = random.choice(self.filters["languages"])
            payload["jazyk"] = [{
                "dopInfo": l["jazykDopInfo"],
                "poznamka": l["jazykPoznamka"],
            }]

        if self.filters["ownership"]:
            o = random.choice(self.filters["ownership"])
            payload["formaVlastnictva"] = [{"kod": o["kod"]}]

        if self.filters["ms_types"]:
            types = random.sample(
                self.filters["ms_types"],
                k=min(2, len(self.filters["ms_types"]))
            )
            payload["typSaSZ"] = [{"kod": t["typSaSZKod"]} for t in types]

        print(f"▶ MS / ALL FILTERS – {dist['nazov']}")

        self.client.post(
            "/api/vyhladanieMSaZS",
            json=payload,
            headers=self.headers(),
            name="MS / SEARCH (ALL FILTERS)",
        )

    # ==============================================================
    @task(3)
    def zs_basic(self):
        if not self.filters["distance"]:
            return

        dist = random.choice(self.filters["distance"])
        print(f"▶ ZS / BASIC – {dist['nazov']}")

        payload = {
            **BASE_MS_ZS,
            "ms": False,
            "zs": True,
            "slovensky": True,
            "vzdialenostKod": dist["kod"],
        }

        self.client.post(
            "/api/vyhladanieMSaZS",
            json=payload,
            headers=self.headers(),
            name="ZS / SEARCH (BASIC)",
        )

    # ==============================================================
    @task(4)
    def zs_all_filters(self):
        if not self.filters["distance"]:
            return

        dist = random.choice(self.filters["distance"])

        payload = {
            **BASE_MS_ZS,
            "ms": False,
            "zs": True,
            "slovensky": True,
            "vzdialenostKod": dist["kod"],
        }

        if self.filters["ownership"]:
            o = random.choice(self.filters["ownership"])
            payload["formaVlastnictva"] = [{"kod": o["kod"]}]

        print(f"▶ ZS / ALL FILTERS – {dist['nazov']}")

        self.client.post(
            "/api/vyhladanieMSaZS",
            json=payload,
            headers=self.headers(),
            name="ZS / SEARCH (ALL FILTERS)",
        )

    # ==============================================================
    @task(2)
    def ss_basic(self):
        print("▶ SS / BASIC")

        payload = {
            "skolskyRok": SCHOOL_YEAR,
            "cisloStranky": 1,
            "volnaKapacita": True,
        }

        self.client.post(
            SS_SEARCH_URL,
            json=payload,
            headers=self.headers(),
            name="SS / SEARCH (BASIC)",
        )

    # ==============================================================
    @task(5)
    def ss_all_filters(self):
        print("▶ SS / ALL FILTERS")

        payload = {
            "skolskyRok": SCHOOL_YEAR,
            "cisloStranky": 1,
            "volnaKapacita": True,
        }

        if self.filters["languages"]:
            l = random.choice(self.filters["languages"])
            payload["jazykKategoria"] = [{
                "kategoria": l["jazykDopInfo"],
                "jazyk": [{"jazykKod": l["jazykPoznamka"]}],
            }]

        if self.filters["ownership"]:
            payload["zriadovatel"] = random.sample(
                [{"zriadovatelKod": o["kod"]} for o in self.filters["ownership"]],
                k=random.randint(1, len(self.filters["ownership"])),
            )

        if self.filters["special"]:
            s = random.choice(self.filters["special"])
            payload["kategoriaSaSZ"] = [{
                "kategoriaKod": s["typSaSZDopInfo"],
                "podkategoriaSaSZ": [{"podkategoriaKod": s["typSaSZPoznamka"]}],
            }]

        self.client.post(
            SS_SEARCH_URL,
            json=payload,
            headers=self.headers(),
            name="SS / SEARCH (ALL FILTERS)",
        )

# ======================================================================
class SearchUser(HttpUser):
    host = HOST
    tasks = [SearchTasks]
    wait_time = between(1, 3)
