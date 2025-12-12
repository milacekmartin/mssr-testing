# tests/prihlaska/payloads/koncept_base.py
# Base (static) payloads for steps 1–3 of ZŠ application

from tests.prihlaska.payloads.common import (
    SKOLSKY_ROK, PRIHLASKA_TYP,
    KROK_1, KROK_2, KROK_3
)

# -------------------------------------------------------------
# STEP 1 – Create base application concept
# -------------------------------------------------------------
def payload_step_1(child_guid, person_guid):
    """
    Minimal and valid payload for Step 1.
    This initializes the application and must contain all 'ulozit*' fields.
    """
    return {
        "dietaGUID": child_guid,
        "krokZadavania": KROK_1,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": None,
        "prihlasenaOsobaGUID": person_guid,

        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False
    }


# -------------------------------------------------------------
# STEP 2 – Additional needs (VVP)
# -------------------------------------------------------------
def payload_step_2(child_guid, app_guid, person_guid):
    return {
        "dietaGUID": child_guid,
        "krokZadavania": KROK_2,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": app_guid,
        "prihlasenaOsobaGUID": person_guid,

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


# -------------------------------------------------------------
# STEP 3 – Initialize school selection (empty)
# -------------------------------------------------------------
def payload_step_3_init(child_guid, app_guid, person_guid):
    return {
        "dietaGUID": child_guid,
        "krokZadavania": KROK_3,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": app_guid,
        "prihlasenaOsobaGUID": person_guid,

        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False,

        "saSZ": []
    }


# -------------------------------------------------------------
# STEP 3 – Save selected school
# -------------------------------------------------------------
def payload_step_3_select(child_guid, app_guid, person_guid, eduid):
    data = payload_step_3_init(child_guid, app_guid, person_guid)
    data["saSZ"] = [{
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1
    }]
    data["ulozitVyberSkoly"] = True
    return data
