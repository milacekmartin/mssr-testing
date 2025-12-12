# tests/prihlaska/payloads/koncept_step4.py
# Step 4 – Adaptive & fallback payload builders (English comments)

from tests.prihlaska.payloads.common import SKOLSKY_ROK


# =====================================================================
# 1) UI FULL FLOW – Adaptive payload (caller already builds saSZ_object)
# =====================================================================
def build_step4_adaptive(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID, saSZ_object):
    """
    Adaptive Step 4 payload used by UI full_flow.py.
    Caller constructs saSZ_object dynamically from school metadata.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 4,
        "saSZ": [saSZ_object],
        "ulozitVyberSkoly": True,
        "zatvoreniePrihlasky": False
    }


# =====================================================================
# 2) LOCUST VERSION – Adaptive payload (builds saSZ from allowed fields)
# =====================================================================
def build_step4_adaptive_locust(dietaGUID, prihlaskaGUID, prihlasenaOsobaGUID, eduid, allowed_fields):
    """
    Adaptive Step 4 payload used by Locust load test.
    This builder must derive allowed fields and construct the saSZ block itself.
    """

    sa = {
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1
    }

    # optional fields based on allowed_fields
    if "pozadovanyJazykKod" in allowed_fields:
        sa["pozadovanyJazykKod"] = "SK"

    if "zaujemUvodnyRocnikVIN" in allowed_fields:
        sa["zaujemUvodnyRocnikVIN"] = False

    if "zaujemDualneVzdelavanie" in allowed_fields:
        sa["zaujemDualneVzdelavanie"] = False

    if "zaujemInternat" in allowed_fields:
        sa["zaujemInternat"] = False

    if "mentalnePostihnutie" in allowed_fields:
        sa["mentalnePostihnutie"] = False

    payload = {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dietaGUID,
        "prihlaskaGUID": prihlaskaGUID,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 4,
        "saSZ": [sa],
        "ulozitVyberSkoly": True,
        "zatvoreniePrihlasky": False
    }

    return payload


# =====================================================================
# 3) Fallback payload (UI + Locust – always valid)
# =====================================================================
def build_step4_fallback(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID, eduid):
    """
    Guaranteed-valid fallback payload based on real API examples.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 4,

        "saSZ": [
            {
                "saSZEDUID": eduid,
                "poradie": 1,
                "kolo": 1,
                "poradieNaPrihlaske": 1,
                "pozadovanyJazykKod": "SK",
                "zaujemUvodnyRocnikVIN": False
            }
        ],

        # Required (even empty)
        "zZ1DoplnujuceUdaje": {},
        "zZ2DoplnujuceUdaje": {
            "existujeZZ2": None,
            "suhlasZZ2": None,
            "dovodNesuhlasuKod": None
        },

        # FE-required fields
        "doplnujucePotreby": {
            "stravovanie": True,
            "druzina": True,
            "druhVychovyKod": "1",
            "typNabozVychovy": None,
            "nabozenskaVychovaKod": None,
            "nabozenskaVychovaNazov": None
        },

        "specialneVVP": {
            "dietaSoSVVP": False,
            "popiSVVP": None,
            "dietaSNadanim": False,
            "popisNadania": None,
            "poznamka": None,
            "pokracovaniePPV": False,
            "celodennaVychova": None,
            "pozadDatumPrijatia": None
        },

        "ulozitVyberSkoly": True,
        "zatvoreniePrihlasky": False,
        "ulozitDoplnujucePotreby": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledavaniaZS": False,
        "ulozitSutaze": False
    }

# =====================================================================
# FULL LOCUST STEP 4 — guaranteed valid (matches UI payload exactly)
# =====================================================================

def build_step4_locust(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID, eduid):
    """
    This payload is 100% identical to the successful UI Step 4 request.
    It ALWAYS passes — no matter which school is selected.
    """

    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 4,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": "ZŠ",
        "skolskyRokKod": "2026/2027",
        "prihlaskaGUID": prihlaska_guid,
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,

        # MUST ALWAYS EXIST
        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": True,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False,

        # FULL REQUIRED STRUCTURES
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

        # SCHOOL BLOCK — must contain these fields
        "saSZ": [
            {
                "saSZEDUID": eduid,
                "poradie": 1,
                "kolo": 1,
                "poradieNaPrihlaske": 1,
                "pozadovanyJazykKod": "SK",
                "zaujemUvodnyRocnikVIN": False
            }
        ]
    }

