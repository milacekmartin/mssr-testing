from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import random
import string

class DataHelper:
    @staticmethod
    def generate_email():
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"loadtest_{random_part}@example.com"

class MixScenarioUser(HttpUser):
    # Main host
    host = "https://test-eprihlasky.iedu.sk"
    wait_time = between(1, 3)

    # def on_start(self):
    #     """
    #     Called when a simulated user starts. 
    #     Example: fetch an initial token from /Najst-skolu page.
    #     """
    #     self.email = DataHelper.generate_email()
    #     res = self.client.get("/Najst-skolu", name="GET /Najst-skolu")
    #     soup = BeautifulSoup(res.text, "html.parser")
    #     token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    #     self.token = token_input.get("value") if token_input else None
    #     print(f"Started user: {self.email}")

    # def _headers_json(self):
    #     """Headers for JSON-based requests (with dynamic token)."""
    #     return {
    #         "Content-Type": "application/json",
    #         "RequestVerificationToken": self.token or "",
    #         "X-Requested-With": "XMLHttpRequest"
    #     }

    #
    # Example tasks from your previous script
    #

    # @task(5)
    # def get_autocomplete(self):
    #     self.client.get(
    #         "/api/autocompleteComplex",
    #         params={"text": "Zamocka", "_": "1743069142573"},
    #         name="GET /api/autocompleteComplex"
    #     )

    # @task(5)
    # def get_reverse(self):
    #     self.client.get(
    #         "/api/reverse",
    #         params={"point.lon": "17.0514", "point.lat": "48.1629", "_": "1743068047974"},
    #         name="GET /api/reverse"
    #     )

    # @task(5)
    # def get_ciselniky(self):
    #     self.client.get("/api/vratCiselniky", name="GET /api/vratCiselniky")

    # @task(5)
    # def post_vyhladanie(self):
    #     payload = {
    #         "text": "",
    #         "zemepisnaSirka": 48.163005,
    #         "zemepisnaDlzka": 17.051447,
    #         "vzdialenost": "4",
    #         "skolskyRokKod": "2025/2026",
    #         "typSaSZ": "",
    #         "jazyk": "",
    #         "zPrihlasky": False,
    #         "pocetZaznamovNaStranku": 20,
    #         "cisloStranky": 1
    #     }
    #     self.client.post(
    #         "/api/vyhladanieSaSZ",
    #         json=payload,
    #         headers=self._headers_json(),
    #         name="POST /api/vyhladanieSaSZ"
    #     )

    # @task(2)
    # def registration_flow(self):
    #     """Example registration steps (if relevant to your scenario)."""
    #     self.codeGen2Fa()
    #     self.verify2FaCode()
    #     self.dokoncenieRegistracie()

    # def codeGen2Fa(self):
    #     self.client.post(
    #         "/api/codeGen2Fa",
    #         json={"email": self.email},
    #         headers=self._headers_json(),
    #         name="POST /api/codeGen2Fa"
    #     )

    # def verify2FaCode(self):
    #     # Hard-coded example code
    #     self.client.post(
    #         "/api/verify2FaCode",
    #         json={"code": "625161", "email": self.email},
    #         headers=self._headers_json(),
    #         name="POST /api/verify2FaCode"
    #     )

    # def dokoncenieRegistracie(self):
    #     payload = {
    #         "vstupZapisZRegistracieUcet": {
    #             "meno": "Martin",
    #             "priezvisko": "Klas",
    #             "datumNarodenia": "2000-12-23",
    #             "rodneCislo": None,
    #             "pohlavieKod": "2",
    #             "statKod": None,
    #             "email": self.email,
    #             "registrovatAjPriNestotozneniSRFO": True,
    #             "odoslatEmail": False
    #         },
    #         "druhDokladu": "34",
    #         "cisloDokladu": None,
    #         "obcanSR": False,
    #         "telefon": "+421911239774",
    #         "appID": True
    #     }
    #     self.client.post(
    #         "/api/dokoncenieRegistracieAD",
    #         json=payload,
    #         headers=self._headers_json(),
    #         name="POST /api/dokoncenieRegistracieAD"
    #     )

    #
    # NEW: Fully expanded POST /api/vratenieObdobiPodavaniaPrihlasok
    #

    @task(20)
    def post_vratenieEDUIDOblubenychSaSZ(self):
        """
        POST to /api/vratenieEDUIDOblubenychSaSZ
        with only the RequestVerificationToken and JSON body.
        """
        # Example payload; adjust to match what your server expects
        payload = {"guid":"fe338f20-b6c3-4db2-872d-b26b680566ed"}

        # The single token you mentioned
        token = "CfDJ8I1MH_0PH0tKgXc6aOlLly4-fKTr6ShLKqRu7rsFFMVlgI-tzaxHAOa0M2kyKwwilCaAPFmo13g391_5Q-PMl35pY0YVylnf_bX0aPOvvucPgCGaUOGGuGdYa5henT4lQeXyHQm5hDPal78HOI6IYcdAET2r1TlK0NzRak3_ah6qgOX8gYkgR19cEw0jwWZJTw"

        headers = {
            "Requestverificationtoken": token,
            "Content-Type": "application/json; charset=UTF-8",

            # "X-correlation-id": "c02a3219-a217-4ab3-ac4e-cdcae745b28c",
            "X-Token-Descriptor": "1c107b07-b41b-4392-9185-fbc77c888709:6921c3a20de4cf980e8a17a3c419597c5a8d5006487f371a3750b52dd15f3b5b",

            "Cookie": "_DC=c%3Dsk-SK%7Cuic%3Dsk-SK; .AspNetCore.Antiforgery.UaYXyBoyr8Q=CfDJ8I1MH_0PH0tKgXc6aOlLly6B2ytJcRkN4EiCWiEIugoTjCyZNbU4ZcRWetI4zqyauNulSuVGgBwDT5b3iXTsdMtcq_PVPUU2MM_Nk3gwj_-w7rtmKPciEQxnae4RYNqgoyBC_dCfk1GXfuaGKQXtEdA; Balanced_and_Offloaded=378929418.20480.0000; cookies-warning=true; _DSA=CfDJ8I1MH_0PH0tKgXc6aOlLly5-tzn684D-ELNPzliCa3F8DFL8av6Q62A0RFha-I5Hiqh_wrQwzifyaxJh-WvD1mOKbWFzPWaHkRDd4CuNKoDHdN2NANFfEVWCEe71Z4VCCyruykuOfq4lwrQUS_1yhRpPw2pYeeLd2-VF6ZS3jz5GBZba7TsVbvtDfvJiisIYuBgcC13Wn9NgQZ8YfiH3YQ6TRULqDzwGdxwJPdC6AcIbcl7yfeDEsYiCtMwpyLttfh2pJD07Ajnx8lMAcVlFJtQjgLiNOO3cCo7XTWyFGEgTfjcBLJFn5a_aABTKdCproA"
        }

        with self.client.post(
            "/api/vratenieEDUIDOblubenychSaSZ",
            json=payload,
            headers=headers,
            name="POST /api/vratenieEDUIDOblubenychSaSZ",
            catch_response=True

        ) as response:
            print("Status:", response.status_code)

            if response.status_code == 200:
                print("Body:", response.text)
                response.success()
            
            else:
                response.failure(f"Unexpected status code {response.status_code}")
