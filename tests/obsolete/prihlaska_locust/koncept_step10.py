# tests/prihlaska/payloads/koncept_step10.py
# Step 10 – Finalization (Adaptive + Fallback Builders)

from tests.prihlaska.payloads.common import SKOLSKY_ROK


# =====================================================================
# Step 10 – Adaptive minimal finalization payload
# =====================================================================
def build_step10_adaptive(
    dieta_guid,
    prihlaska_guid,
    prihlasenaOsobaGUID,
    saSZ_object
):
    """
    Builds the minimal allowed adaptive Step 10 payload.
    This version sends only the fields that the API always accepts.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,   # ← FIXED
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,

        "krokZadavania": 10,
        "saSZ": [saSZ_object],

        "ulozitVyberSkoly": False,
        "zatvoreniePrihlasky": False
    }


# =====================================================================
# Step 10 – 100% valid fallback payload (guaranteed by real API data)
# =====================================================================
def build_step10_fallback(
    dieta_guid,
    prihlaska_guid,
    prihlasenaOsobaGUID,
    eduid
):
    """
    Full guaranteed-valid payload for Step 10.
    Based directly on confirmed successful API requests from ePrihlášky.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 10,

        "saSZ": [
            {
                "saSZEDUID": eduid,
                "poradie": 1,
                "kolo": 1,
                "pridal": None,
                "pridalDna": None,
                "poradieNaPrihlaske": 1,
                "zaujemPripravnyRocnik": None,
                "zaujemUvodnyRocnikNKS": None,
                "zaujemUvodnyRocnikVIN": False,
                "zaujemDualneVzdelavanie": None,
                "zaujemInternat": None,
                "terminPrijimacejSkuskyKod": None,
                "terminPrijimacejSkuskyNazov": None,
                "terminPrijimacejSkuskyPopis": None,
                "pozadovanyJazykKod": "SK",
                "pozadovanyJazykNazov": "slovenský",
                "mentalnePostihnutie": False,
                "nazov": "ZŠ",
                "nazovOficialny": "ZŠ Názov"
            }
        ],

        "zZ1DoplnujuceUdaje": {
            "telefon": "+421933994999",
            "vyhradnaKomunikacia": None,
            "adresa": {
                "statKod": "601",
                "adresaMimoSR": "AAA"
            }
        },

        "zZ2DoplnujuceUdaje": {
            "existujeZZ2": False,
            "suhlasZZ2": False,
            "dovodNesuhlasuKod": None
        },

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

        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False,

        "zatvoreniePrihlasky": False
    }
