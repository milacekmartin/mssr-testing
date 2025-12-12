# tests/prihlaska/payloads/koncept_step5.py
# Step 5 – Legal Guardian (Adaptive + Fallback Builders)

from tests.prihlaska.payloads.common import SKOLSKY_ROK


# =====================================================================
# Step 5 – Adaptive payload
# =====================================================================
def build_step5_adaptive(
    dieta_guid,
    prihlaska_guid,
    prihlasenaOsobaGUID,
    saSZ_object
):
    """
    Builds an adaptive Step 5 payload. Uses dynamic saSZ_object coming
    from Step 4 detection. Does not include fields not required by API.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 5,

        "saSZ": [saSZ_object],

        "zZ1DoplnujuceUdaje": {
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
        },

        "ulozitZakonnyZastupca": True,
        "zatvoreniePrihlasky": False
    }


# =====================================================================
# Step 5 – 100% valid fallback payload
# =====================================================================
def build_step5_fallback(
    dieta_guid,
    prihlaska_guid,
    prihlasenaOsobaGUID,
    eduid
):
    """
    Full guaranteed-valid fallback Step 5 payload for ZŠ,
    based on verified working API flows.
    """

    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": SKOLSKY_ROK,
        "typPrihlasky": "ZŠ",
        "kolo": 1,
        "krokZadavania": 5,

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

        "ulozitVyberSkoly": False,
        "zatvoreniePrihlasky": False,

        "ulozitZakonnyZastupca": True,
        "ulozitDoplnujucePotreby": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False
    }
