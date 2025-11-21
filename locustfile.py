from locust import HttpUser, task, between
import json
import time
import uuid

import random
import string

# ════════════════════════════════════════════════════════════════
#  REALNE ZNEJÚCE NÁHODNÉ MENÁ A PRIEZVISKÁ
# ════════════════════════════════════════════════════════════════

RANDOM_FIRST_NAMES = [
    "Adam", "Oliver", "Tobias", "Samuel", "Daniel", "Marek",
    "Dominik", "Lukáš", "Matúš", "David", "Richard", "Martin",
    "Patrik", "Jakub", "Sebastián", "Viktor", "Tomáš"
]

RANDOM_LAST_NAMES = [
    "Kováč", "Blažek", "Toman", "Ševčík", "Král", "Peterka",
    "Marek", "Novák", "Urban", "Petráš", "Bielik", "Varga",
    "Hlavatý", "Havel", "Sedláček", "Kučera", "Horák"
]

def generate_random_name():
    """Vráti unikátne reálne meno + priezvisko s náhodným suffixom."""
    base_first = random.choice(RANDOM_FIRST_NAMES)
    base_last = random.choice(RANDOM_LAST_NAMES)

    # náhodný 4-znakový suffix z [A-Z0-9]
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f"{base_first}-{suffix}", f"{base_last}-{suffix}"


# ════════════════════════════════════════════════════════════════
#  KONFIGURAČNÉ PREMENNÉ – NIŽŠIE NECHÁVAM TVOJE POVODNÉ
# ════════════════════════════════════════════════════════════════

HOST = "https://test-eprihlasky.iedu.sk"
WAIT_TIME_MIN = 1
WAIT_TIME_MAX = 3

CSRF = "CfDJ8AiBhEooU4RKqHIeRs_9xFcnZa0iyjaeoktHkKO8v-iW2Nxz_kfVXaxbt616tdtm5ct2GD4svbioV4dyZdi4lYU54Ij-s5eUFZT7Os56jb_6KdM59alqOOwptzJeCM9cqbEwRbQLQrzi9_7-0b0vx3jZtcuKVc9h6AeIYJeqZS6odE3aTCsq3xl6tgnANZf53g"
CSRF_NEW = "CfDJ8AiBhEooU4RKqHIeRs_9xFcnZa0iyjaeoktHkKO8v-iW2Nxz_kfVXaxbt616tdtm5ct2GD4svbioV4dyZdi4lYU54Ij-s5eUFZT7Os56jb_6KdM59alqOOwptzJeCM9cqbEwRbQLQrzi9_7-0b0vx3jZtcuKVc9h6AeIYJeqZS6odE3aTCsq3xl6tgnANZf53g"

IAM_TOKEN = "21bc6b57-7693-45ef-88b0-7e2950fbfb3f:422f5b21b7e46e8d88c35659ff43209cd760751818c0ed37f72afad71385f1d0"

COOKIE_BUNDLE = (
    "_DC=c%3Dsk-SK%7Cuic%3Dsk-SK; Balanced_and_Offloaded=378929418.20480.0000; cookies-warning=true; .AspNetCore.Antiforgery.UaYXyBoyr8Q=CfDJ8AiBhEooU4RKqHIeRs_9xFfB5apsSZE9hCOlR4kbKYfiIGRtvHqsA0pds5qtAgxWlGLZYLn_7xVceXI2SZ3sXw-kU8gRO6HLwuHxtOgIbpxjzsDdGmrV0uC2yYrHC4aLSyuDeX8Pefl2o7VyDiXr6Wo; last_non_error_path=%2F; _DS=CfDJ8AiBhEooU4RKqHIeRs%2F9xFcRnu8pKILDKo4LmTYRoPI4ZRgRvnq4Azt05DI7uBBrwOALPt3rpHmYtFMQrrMtdO1evOOwFNH5yRfKE2u35v04Brji%2BOLadCmB5dZof9TxrLbtxgqHA6u3A7t6dnwQEcgsJFnHFTNLx9tzcgtkWcLR; _DSA=CfDJ8AiBhEooU4RKqHIeRs_9xFdpU2Vb75_oBpFNFLGqE-iZqVzlDj_ndOvhEK5moyw17J5dAzGQDDcHSo0zB5X5UbW4SIFzJw4wkza50urQLWzRK8VON1K4JTHdvFOVAumBX6FIXYvRxLLhtJ57_GX5C8cqi5ngJnUZ-ESZSJq0Q81ARaIVWf15hSTQjtjg7Ep6aRwFByAQWHxAzX4ubYs66R3_imbv6TpI2K7LwY-KP0SAaq_kcpU6wAc5gkPB6qovjuTiJH3Dpp5w9IGfWsPR7vpptxsKd1QmE9yM8VXFEyxl5XyJH0GCmufzO3d_LcbyeA"
)

SUBJEKT_GUID = "8dba7ecd-b18b-4a92-a5fb-ae06fabc2055"
PRIHLASENA_OSOBA_GUID = "4f176d30-9aad-4cce-9f22-aaead87b786c"

SKOLSKY_ROK_KOD_2026 = "2026/2027"


# ════════════════════════════════════════════════════════════════
#  COMMON A EXTENDED HEADERS
# ════════════════════════════════════════════════════════════════

COMMON_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Requestverificationtoken": CSRF,
    "X-Token-Descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE
}

EXTENDED_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://test-eprihlasky.iedu.sk",
    "Referer": "https://test-eprihlasky.iedu.sk/",
    "RequestVerificationToken": CSRF_NEW,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "x-token-descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE
}


# ════════════════════════════════════════════════════════════════
#        POKRAČOVANIE BUDE V ČASTI 2 (HLAVNÝ ZŠ SCENÁR)
# ════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════
#  HLAVNÝ ROZŠÍRENÝ SCENÁR ZŠ – KROKY 1 až 23
# ════════════════════════════════════════════════════════════════

class MixScenarioUser(HttpUser):
    host = HOST
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)

    # ==================================================================
    #  ROZŠÍRENÝ SCENÁR: Kompletná ZŠ prihláška s vyhľadávaním škôl
    # ==================================================================
    @task(weight=3)
    def scenar_zs_prihlaska(self):

        # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        #  KROK 0 – GENEROVANIE DIEŤAŤA (REALISTIC RANDOM NAME)
        # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        first_name, last_name = generate_random_name()
        print(f"🧒 Generujem dieťa: {first_name} {last_name}")

        # Údaje sú rovnaké ako pri Richardovi, iba meno/priezvisko sú random
        RANDOM_DIETA = {
            "meno": first_name,
            "priezvisko": last_name,
            "datumNarodenia": "2020-01-25",
            "miestoNarodenia": "Bratislava",
            "pohlavieKod": "1",
            "narodnostKod": "2",
            "statnaPrislusnostKod": "211",
            "materinskyJazykKod": "SK",
            "tpStatKod": "211",
            "tpObecKod": "582000",
            "tpPsc": "84104",
            "tpSupisneCislo": "2",
            "zpStatKod": "211",
            "zpObecKod": "582000",
            "zpPsc": "84104",
            "zpSupisneCislo": "2"
        }

        print("🎓 Spúšťam ZŠ scenár prihlášky")

        # ----------------------------------------------------------
        # 1. Načítanie oznámení
        # ----------------------------------------------------------
        payload_oznamenia = {
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "precitana": False,
            "pocetZaznamovNaStranku": 50,
            "cisloStranky": 1
        }
        self._send_in_scenario("/api/vratenieZoznamuOznameniPreZZ",
                               payload_oznamenia,
                               "SCENÁR ZŠ: 1/23 - Načítanie oznámení")
        self.wait()

        # ----------------------------------------------------------
        # 2. Načítanie existujúcich detí
        # ----------------------------------------------------------
        payload_deti_pred = {
            "guid": SUBJEKT_GUID,
            "lenPlatne": True
        }
        self._send_in_scenario("/api/vratenieZoznamuDeti",
                               payload_deti_pred,
                               "SCENÁR ZŠ: 2/23 - Zoznam detí")
        self.wait()

        # ----------------------------------------------------------
        # 3. Pridanie nového dieťaťa – RANDOM NAME
        # ----------------------------------------------------------
        payload_add_child = {
            "subjektGUID": SUBJEKT_GUID,
            "dietaGUID": None,
            "rodneCislo": None,
            "meno": RANDOM_DIETA["meno"],
            "priezvisko": RANDOM_DIETA["priezvisko"],
            "rodnePriezvisko": None,
            "datumNarodenia": RANDOM_DIETA["datumNarodenia"],
            "miestoNarodenia": RANDOM_DIETA["miestoNarodenia"],
            "pohlavieKod": RANDOM_DIETA["pohlavieKod"],
            "narodnostKod": RANDOM_DIETA["narodnostKod"],
            "statnaPrislusnost": [
                {"statnaPrislusnostKod": RANDOM_DIETA["statnaPrislusnostKod"]}
            ],
            "materinskyJazykKod": RANDOM_DIETA["materinskyJazykKod"],
            "inyMaterinskyJazykKod": None,
            "rozpracovane": False,
            "platne": True,
            "tpStatKod": RANDOM_DIETA["tpStatKod"],
            "tpObecKod": RANDOM_DIETA["tpObecKod"],
            "tppsc": RANDOM_DIETA["tpPsc"],
            "tpUlicaKod": None,
            "tpSupisneCislo": RANDOM_DIETA["tpSupisneCislo"],
            "tpOrientacneCislo": None,
            "tpAdresaMimoSR": None,
            "adresaTPZhodnaSTPRodica": False,
            "zpStatKod": RANDOM_DIETA["zpStatKod"],
            "zpObecKod": RANDOM_DIETA["zpObecKod"],
            "zppsc": RANDOM_DIETA["zpPsc"],
            "zpUlicaKod": None,
            "zpSupisneCislo": RANDOM_DIETA["zpSupisneCislo"],
            "zpOrientacneCislo": None,
            "zpAdresaMimoSR": None,
            "adresaObvyklaZhodnaSTP": True,
            "narodnostZRFO": False,
            "miestoNarodeniaZRFO": False
        }

        resp_add_child = self._send_in_scenario_with_response(
            "/api/zapisAModifikaciaDietata",
            payload_add_child,
            "SCENÁR ZŠ: 3/23 - Pridanie dieťaťa"
        )

        # Extrahujeme GUID
        try:
            response_json = resp_add_child.json()

            if (
                "dieta" in response_json
                and response_json["dieta"]
                and "guid" in response_json["dieta"]
                and response_json["dieta"]["guid"]
            ):
                richard_guid = response_json["dieta"]["guid"]
                print("🆔 Dieťa GUID:", richard_guid)
            else:
                raise KeyError("GUID not found in response.")

        except Exception as e:
            print("❌ NEPODARILO SA EXTRAHOVAŤ GUID DIEŤAŤA!")
            print("   Dôvod:", str(e))
            print("   Response body:", resp_add_child.text[:500], "...")
            richard_guid = str(uuid.uuid4())
            print("   👉 Používam fallback GUID:", richard_guid)

        # ----------------------------------------------------------
        # 4. Refresh detí
        # ----------------------------------------------------------
        self._send_in_scenario(
            "/api/vratenieZoznamuDeti",
            payload_deti_pred,
            "SCENÁR ZŠ: 4/23 - Refresh detí"
        )
        self.wait()

        # ----------------------------------------------------------
        # 5. Detail dieťaťa
        # ----------------------------------------------------------
        self._send_in_scenario(
            "/api/vratenieUdajovDietata",
            {"guid": richard_guid},
            "SCENÁR ZŠ: 5/23 - Detail dieťaťa"
        )
        self.wait()

        # ----------------------------------------------------------
        # 6. Koncept krok 1
        # ----------------------------------------------------------
        payload_k1 = {
            "dietaGUID": richard_guid,
            "krokZadavania": 1,
            "kolo": 1,
            "zatvoreniePrihlasky": False,
            "typPrihlasky": "ZŠ",
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "prihlaskaGUID": None,
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "ulozitDoplnujucePotreby": False,
            "ulozitVyberSkoly": False,
            "ulozitZakonnyZastupca": False,
            "ulozitInformacieZS": False,
            "ulozitVysledkyVzdelavaniaZS": False,
            "ulozitSutaze": False
        }

        resp_k1 = self._send_in_scenario_with_response(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            payload_k1,
            "SCENÁR ZŠ: 6/23 - Koncept krok 1"
        )

        try:
            response_json = resp_k1.json()

            if (
                "prihlaska" in response_json
                and response_json["prihlaska"]
                and "prihlaskaGUID" in response_json["prihlaska"]
                and response_json["prihlaska"]["prihlaskaGUID"]
            ):
                prihlaska_guid = response_json["prihlaska"]["prihlaskaGUID"]
                print("📄 Prihláška GUID:", prihlaska_guid)
            else:
                raise KeyError("prihlaskaGUID not found in response.")

        except Exception as e:
            print("❌ NEPODARILO SA EXTRAHOVAŤ GUID PRIHLÁŠKY!")
            print("   Dôvod:", str(e))
            print("   Response body:", resp_k1.text[:500], "...")
            prihlaska_guid = str(uuid.uuid4())
            print("   👉 Používam fallback GUID:", prihlaska_guid)

        self.wait()

        # ----------------------------------------------------------
        # 7. Koncept krok 2
        # ----------------------------------------------------------
        payload_k2 = {
            "dietaGUID": richard_guid,
            "krokZadavania": 2,
            "kolo": 1,
            "zatvoreniePrihlasky": False,
            "typPrihlasky": "ZŠ",
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "prihlaskaGUID": prihlaska_guid,
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "ulozitDoplnujucePotreby": True,
            "ulozitVyberSkoly": False,
            "ulozitZakonnyZastupca": False,
            "ulozitInformacieZS": False,
            "ulozitVysledkyVzdelavaniaZS": False,
            "ulozitSutaze": False,
            "doplnujucePotreby": {
                "druhVychovyKod": "1",
                "stravovanie": True,
                "druzina": True
            },
            "specialneVVP": {
                "dietaSoSVVP": False,
                "popiSVVP": None,
                "dietaSNadanim": False,
                "popisNadania": None,
                "poznamka": None,
                "pokracovaniePPV": False
            }
        }

        self._send_in_scenario(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            payload_k2,
            "SCENÁR ZŠ: 7/23 - Koncept krok 2"
        )
        self.wait()

        # ----------------------------------------------------------
        # 8: Obľúbene ZŠ
        # ----------------------------------------------------------
        payload_oblubene = {
            "guid": PRIHLASENA_OSOBA_GUID,
            "typSaSZ": {"skratenaDoplnkovaInformacia": "ZŠ"}
        }

        self._send_in_scenario(
            "/api/vratenieEDUIDOblubenychSaSZ",
            payload_oblubene,
            "SCENÁR ZŠ: 8/23 - Obľúbené ZŠ"
        )
        self.wait()

        # ----------------------------------------------------------
        # 9: Filtrovanie ZŠ
        # ----------------------------------------------------------
        self._send_extended_in_scenario(
            "/api/vrateniePoloziekFiltrov",
            {"skolskyRokKod": SKOLSKY_ROK_KOD_2026, "ms": False, "zs": True},
            "SCENÁR ZŠ: 9/23 - Filtrovanie ZŠ"
        )
        self.wait()

        # ----------------------------------------------------------
        # 10: Vyhľadávanie adries
        # ----------------------------------------------------------
        self._send_get_in_scenario(
            "/api/search",
            {"text": "Bratislava 2, Bratislava", "_": "1763398868392"},
            "SCENÁR ZŠ: 10/23 - Vyhľadávanie adries"
        )
        self.wait()

        # ----------------------------------------------------------
        # 11-22: Tvoje pôvodné ZŠ vyhľadávacie scenáre
        # ----------------------------------------------------------
        print("🔍 Spúšťam sériu vyhľadávaní ZŠ...")

        payload_search_base = {
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "ms": False,
            "zs": True,
            "cisloStranky": 1,
            "zemepisnaSirka": 48.199036,
            "zemepisnaDlzka": 17.054286,
            "vzdialenostKod": "7"
        }

        # Vyhľadávanie 1 (20)
        payload_11 = payload_search_base | {"pocetZaznamovNaStranku": 20}
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_11,
            "SCENÁR ZŠ: 11/23 - Vyhľadávanie 20"
        )
        self.wait()

        # Vyhľadávanie 2 (100k)
        payload_12 = payload_search_base | {"pocetZaznamovNaStranku": 100000}
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_12,
            "SCENÁR ZŠ: 12/23 - Vyhľadávanie 100k"
        )
        self.wait()

        # Vyhľadávanie 3 (slovensky 20)
        payload_13 = payload_search_base | {
            "pocetZaznamovNaStranku": 20,
            "jazyk": [],
            "slovensky": True
        }
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_13,
            "SCENÁR ZŠ: 13/23 - Slovensky 20"
        )
        self.wait()

        # Vyhľadávanie 4 (slovensky 100k)
        payload_14 = payload_13 | {"pocetZaznamovNaStranku": 100000}
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_14,
            "SCENÁR ZŠ: 14/23 - Slovensky 100k"
        )
        self.wait()

        # 15
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_13,
            "SCENÁR ZŠ: 15/23 - Slovensky 20 opakovane"
        )
        self.wait()

        # 16
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_14,
            "SCENÁR ZŠ: 16/23 - Slovensky 100k opakovane"
        )
        self.wait()

        # 17 – štátne 20
        payload_17 = payload_13 | {
            "formaVlastnictva": [{"kod": "3"}]
        }
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_17,
            "SCENÁR ZŠ: 17/23 - Štátne 20"
        )
        self.wait()

        # 18 – štátne 100k
        payload_18 = payload_17 | {"pocetZaznamovNaStranku": 100000}
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_18,
            "SCENÁR ZŠ: 18/23 - Štátne 100k"
        )
        self.wait()

        # 19 – typy škôl
        payload_19 = payload_17 | {
            "typSaSZ": [
                {"kod": "211"},
                {"kod": "221"},
                {"kod": "223"},
                {"kod": "231"},
                {"kod": "233"},
                {"kod": "213"}
            ]
        }
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_19,
            "SCENÁR ZŠ: 19/23 - Typy škôl 20"
        )
        self.wait()

        # 20 – typy škôl 100k
        payload_20 = payload_19 | {"pocetZaznamovNaStranku": 100000}
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_20,
            "SCENÁR ZŠ: 20/23 - Typy škôl 100k"
        )
        self.wait()

        # 21
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_19,
            "SCENÁR ZŠ: 21/23 - Typy škôl 20 (opak)"
        )
        self.wait()

        # 22
        self._send_extended_in_scenario(
            "/api/vyhladanieMSaZS", payload_20,
            "SCENÁR ZŠ: 22/23 - Typy škôl 100k (opak)"
        )
        self.wait()

        # ----------------------------------------------------------
        # 23 – FINÁLNE načítanie obľúbených škôl
        # ----------------------------------------------------------
        self._send_in_scenario(
            "/api/vratenieEDUIDOblubenychSaSZ",
            payload_oblubene,
            "SCENÁR ZŠ: 23/31 - Finálne načítanie obľúbených škôl"
        )
        self.wait()

        # ==========================================================
        #  KROK 24 – Zapísanie obľúbenej ZŠ školy
        # ==========================================================
        payload_24 = {
            "guid": PRIHLASENA_OSOBA_GUID,
            "oblubenaSaSZ": [{"eduid": 910000787}]
        }

        self._send_in_scenario(
            "/api/zapisOblubenychSaSZ",
            payload_24,
            "SCENÁR ZŠ: 24/31 - Pridanie obľúbenej školy 910000787"
        )
        self.wait()

        # ==========================================================
        #  KROK 25 – Načítanie obľúbených ZŠ
        # ==========================================================
        payload_25 = {
            "guid": PRIHLASENA_OSOBA_GUID,
            "typSaSZ": {"skratenaDoplnkovaInformacia": "ZŠ"}
        }

        self._send_in_scenario(
            "/api/vratenieEDUIDOblubenychSaSZ",
            payload_25,
            "SCENÁR ZŠ: 25/31 - Overenie obľúbených škôl ZŠ"
        )
        self.wait()

        # ==========================================================
        #  KROK 26 – Koncept krok 3 (výber školy)
        # ==========================================================
        payload_26 = {
            "dietaGUID": richard_guid,
            "krokZadavania": 3,
            "kolo": 1,
            "zatvoreniePrihlasky": False,
            "typPrihlasky": "ZŠ",
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "prihlaskaGUID": prihlaska_guid,
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "ulozitDoplnujucePotreby": False,
            "ulozitVyberSkoly": True,
            "ulozitZakonnyZastupca": False,
            "ulozitInformacieZS": False,
            "ulozitVysledkyVzdelavaniaZS": False,
            "ulozitSutaze": False,
            "doplnujucePotreby": {
                "druhVychovyKod": "1",
                "stravovanie": True,
                "druzina": True
            },
            "specialneVVP": {
                "dietaSoSVVP": False,
                "popiSVVP": None,
                "dietaSNadanim": False,
                "popisNadania": None,
                "poznamka": None,
                "pokracovaniePPV": False
            },
            "saSZ": [
                {
                    "saSZEDUID": 910000787,
                    "poradie": 1,
                    "kolo": 1,
                    "poradieNaPrihlaske": 1
                }
            ]
        }

        self._send_in_scenario(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            payload_26,
            "SCENÁR ZŠ: 26/31 - Uloženie výberu školy (krok 3)"
        )
        self.wait()

        # ==========================================================
        #  KROK 27 – Načítanie vybraných škôl
        # ==========================================================
        payload_27 = {"prihlaskaGUID": prihlaska_guid}

        self._send_in_scenario(
            "/api/vratenieVybranychSaSZ",
            payload_27,
            "SCENÁR ZŠ: 27/31 - Načítanie vybranej školy"
        )
        self.wait()

        # ==========================================================
        #  KROK 28 – Koncept krok 4 (jazyk + VIN)
        # ==========================================================
        payload_28 = {
            "dietaGUID": richard_guid,
            "krokZadavania": 4,
            "kolo": 1,
            "zatvoreniePrihlasky": False,
            "typPrihlasky": "ZŠ",
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "prihlaskaGUID": prihlaska_guid,
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "ulozitDoplnujucePotreby": False,
            "ulozitVyberSkoly": True,
            "ulozitZakonnyZastupca": False,
            "ulozitInformacieZS": False,
            "ulozitVysledkyVzdelavaniaZS": False,
            "ulozitSutaze": False,
            "doplnujucePotreby": {
                "druhVychovyKod": "1",
                "stravovanie": True,
                "druzina": True
            },
            "specialneVVP": {
                "dietaSoSVVP": False,
                "popiSVVP": None,
                "dietaSNadanim": False,
                "popisNadania": None,
                "poznamka": None,
                "pokracovaniePPV": False
            },
            "saSZ": [
                {
                    "saSZEDUID": 910000787,
                    "poradie": 1,
                    "kolo": 1,
                    "poradieNaPrihlaske": 1,
                    "pozadovanyJazykKod": "SK",
                    "zaujemUvodnyRocnikVIN": True
                }
            ]
        }

        self._send_in_scenario(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            payload_28,
            "SCENÁR ZŠ: 28/31 - Jazyk + VIN (krok 4)"
        )
        self.wait()

        # ==========================================================
        #  KROK 29 – Koncept krok 5 (zákonný zástupca)
        # ==========================================================
        payload_29 = {
            "dietaGUID": richard_guid,
            "krokZadavania": 5,
            "kolo": 1,
            "zatvoreniePrihlasky": False,
            "typPrihlasky": "ZŠ",
            "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
            "prihlaskaGUID": prihlaska_guid,
            "prihlasenaOsobaGUID": PRIHLASENA_OSOBA_GUID,
            "ulozitDoplnujucePotreby": False,
            "ulozitVyberSkoly": False,
            "ulozitZakonnyZastupca": True,
            "ulozitInformacieZS": False,
            "ulozitVysledkyVzdelavaniaZS": False,
            "ulozitSutaze": False,
            "doplnujucePotreby": {
                "druhVychovyKod": "1",
                "stravovanie": True,
                "druzina": True
            },
            "specialneVVP": {
                "dietaSoSVVP": False,
                "popiSVVP": None,
                "dietaSNadanim": False,
                "popisNadania": None,
                "poznamka": None,
                "pokracovaniePPV": False
            },
            "saSZ": [
                {
                    "saSZEDUID": 910000787,
                    "poradie": 1,
                    "kolo": 1,
                    "poradieNaPrihlaske": 1,
                    "pozadovanyJazykKod": "SK",
                    "zaujemUvodnyRocnikVIN": True
                }
            ],
            "zZ1DoplnujuceUdaje": {
                "rodnePriezvisko": None,
                "telefon": "+421933994999",
                "adresaTotoznaSDefaultnouAdresou": False,
                "adresa": {
                    "statKod": "601",
                    "adresaMimoSR": "AAA"
                }
            },
            "zZ2DoplnujuceUdaje": {
                "existujeZZ2": False,
                "suhlasZZ2": False,
                "dovodNesuhlasuKod": None
            }
        }

        self._send_in_scenario(
            "/api/zapisAModifikaciaKonceptuPrihlasky",
            payload_29,
            "SCENÁR ZŠ: 29/31 - Zákonný zástupca (krok 5)"
        )
        self.wait()

        # ==========================================================
        #  KROK 30 – Kontrola konceptu
        # ==========================================================
        payload_30 = {"prihlaskaGUID": prihlaska_guid}

        self._send_extended_in_scenario(
            "/api/vratenieKonceptuPrihlasky",
            payload_30,
            "SCENÁR ZŠ: 30/31 - Kontrola konceptu"
        )
        self.wait()

        # ==========================================================
        #  KROK 31 – Finálna kontrola konceptu
        # ==========================================================
        self._send_extended_in_scenario(
            "/api/vratenieKonceptuPrihlasky",
            payload_30,
            "SCENÁR ZŠ: 31/31 - Finálna kontrola konceptu"
        )

        print("🏁 Scenár ZŠ (1–31) úspešne dokončený.")

    # ==================================================================
    #  Pôvodný scenár – pridanie jedného dieťaťa (MŠ)
    # ==================================================================
    @task(weight=2)
    def scenar_pridanie_noveho_dietata(self):

        print("🔄 Spúšťam scenár: Pridanie nového dieťaťa (MŠ)")

        # náhodné meno pre tento jednoduchý scenár
        fn, ln = generate_random_name()

        payload_dieta = {
            "subjektGUID": SUBJEKT_GUID,
            "dietaGUID": None,
            "rodneCislo": None,
            "meno": fn,
            "priezvisko": ln,
            "rodnePriezvisko": None,
            "datumNarodenia": "2020-01-25",
            "miestoNarodenia": "Bratislava",
            "pohlavieKod": "1",
            "narodnostKod": "2",
            "statnaPrislusnost": [{"statnaPrislusnostKod": "211"}],
            "materinskyJazykKod": "SK",
            "inyMaterinskyJazykKod": None,
            "rozpracovane": False,
            "platne": True,
            "tpStatKod": "211",
            "tpObecKod": "582000",
            "tppsc": "84104",
            "tpUlicaKod": None,
            "tpSupisneCislo": "3",
            "tpOrientacneCislo": None,
            "tpAdresaMimoSR": None,
            "adresaTPZhodnaSTPRodica": False,
            "zpStatKod": "211",
            "zpObecKod": "582000",
            "zppsc": "84104",
            "zpUlicaKod": None,
            "zpSupisneCislo": "3",
            "zpOrientacneCislo": None,
            "zpAdresaMimoSR": None,
            "adresaObvyklaZhodnaSTP": True,
            "narodnostZRFO": False,
            "miestoNarodeniaZRFO": False
        }

        self._send_in_scenario(
            "/api/zapisAModifikaciaDietata",
            payload_dieta,
            "MŠ scenár 1/3 - zápis dieťaťa"
        )

        self.wait()

        # načítanie zoznamu detí
        self._send_in_scenario(
            "/api/vratenieZoznamuDeti",
            {"guid": SUBJEKT_GUID, "lenPlatne": True},
            "MŠ scenár 2/3 - refresh detí"
        )

        self.wait()

        # načítanie prihlášok
        self._send_in_scenario(
            "/api/vratenieZoznamuPrihlasokSubjektu",
            {"SubjektGUID": SUBJEKT_GUID},
            "MŠ scenár 3/3 - zoznam prihlášok"
        )

        print("✅ Scenár MŠ úspešne dokončený.")



    # ==================================================================
    #  OSTATNÉ TASKY – tvoje pôvodné
    # ==================================================================

    @task(weight=3)
    def post_vratenie_oblubenych(self):
        self._send(
            "/api/vratenieEDUIDOblubenychSaSZ",
            {"guid": PRIHLASENA_OSOBA_GUID},
            "POST /vratenieEDUIDOblubenychSaSZ"
        )

    @task(weight=3)
    def post_vratenie_zoznamu_deti(self):
        self._send(
            "/api/vratenieZoznamuDeti",
            {"guid": SUBJEKT_GUID, "lenPlatne": True},
            "POST /vratenieZoznamuDeti"
        )

    @task(weight=3)
    def post_vratenie_zoznamu_prihlasok(self):
        self._send(
            "/api/vratenieZoznamuPrihlasokSubjektu",
            {"SubjektGUID": SUBJEKT_GUID},
            "POST /vratenieZoznamuPrihlasokSubjektu"
        )

    @task(weight=2)
    def post_vratenie_udajov_dietata(self):
        self._send(
            "/api/vratenieUdajovDietata",
            {"guid": "c719a9bd-ecc8-4c7e-be7c-0cf19ae296bb"},
            "POST /vratenieUdajovDietata"
        )

    @task(weight=1)
    def get_autocomplete(self):
        self._send_get(
            "/api/autocompleteComplex",
            {"text": "Pekna", "_": "1763396429868"},
            "GET /autocompleteComplex"
        )

    @task(weight=1)
    def post_vratenie_obdobia_podavania(self):
        payload = {"skolskyRokKod": SKOLSKY_ROK_KOD_2026}
        self._send_extended(
            "/api/vratenieObdobiPodavaniaPrihlasok",
            payload,
            "POST /vratenieObdobiPodavaniaPrihlasok"
        )

    @task(weight=1)
    def get_konfiguracne_udaje(self):
        self._send_get_extended(
            "/api/vratKonfiguracneUdajePrihlasok",
            {"_": "1763396790023"},
            "GET /vratKonfiguracneUdajePrihlasok"
        )



    # ==================================================================
    #  POMOCNÉ FUNKCIE – POST/GET wrappery
    # ==================================================================

    def _send(self, url, payload, name):
        with self.client.post(
            url,
            data=json.dumps(payload),
            headers=COMMON_HEADERS,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate(resp, name)

    def _send_extended(self, url, payload, name):
        with self.client.post(
            url,
            data=json.dumps(payload),
            headers=EXTENDED_HEADERS,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate(resp, name)

    def _send_in_scenario(self, url, payload, name):
        with self.client.post(
            url,
            data=json.dumps(payload),
            headers=COMMON_HEADERS,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate_scenario(resp, name)

    def _send_in_scenario_with_response(self, url, payload, name):
        with self.client.post(
            url,
            data=json.dumps(payload),
            headers=COMMON_HEADERS,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate_scenario(resp, name)
            return resp

    def _send_extended_in_scenario(self, url, payload, name):
        with self.client.post(
            url,
            data=json.dumps(payload),
            headers=EXTENDED_HEADERS,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate_scenario(resp, name)

    def _send_get(self, url, params, name):
        headers = {
            "Requestverificationtoken": CSRF,
            "X-Token-Descriptor": IAM_TOKEN,
            "Cookie": COOKIE_BUNDLE
        }
        with self.client.get(
            url,
            params=params,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate(resp, name)

    def _send_get_extended(self, url, params, name):
        headers = EXTENDED_HEADERS.copy()
        with self.client.get(
            url,
            params=params,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate(resp, name)

    def _send_get_in_scenario(self, url, params, name):
        headers = {
            "Requestverificationtoken": CSRF,
            "X-Token-Descriptor": IAM_TOKEN,
            "Cookie": COOKIE_BUNDLE
        }
        with self.client.get(
            url,
            params=params,
            headers=headers,
            name=name,
            catch_response=True
        ) as resp:
            self._evaluate_scenario(resp, name)



    # ==================================================================
    #  EVALUÁCIA ODPOVEDÍ
    # ==================================================================

    def _evaluate(self, resp, name):
        status = resp.status_code
        print(f"{name} → {status}")
        if status == 200:
            resp.success()
        else:
            resp.failure(f"Status {status} | body: {resp.text[:250]}")

    def _evaluate_scenario(self, resp, name):
        status = resp.status_code
        print(f"    {name} → {status}")
        if status == 200:
            resp.success()
        else:
            print(f"    ❌ Chyba v scenári: {name}")
            resp.failure(f"Status {status} | body: {resp.text[:250]}")

