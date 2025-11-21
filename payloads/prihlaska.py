# payloads/prihlaska.py
# ======================
#
# Payloady pre jednotlivé kroky vytvárania ZŠ prihlášky.

from config.settings import (
    PRIHLASENA_OSOBA_GUID,
    SKOLSKY_ROK_KOD_2026,
)


# ---------------------------------------------------------
#  KROK 1 – vytvorenie konceptu (prvý zápis)
# ---------------------------------------------------------
def koncept_krok_1(dieta_guid: str):
    return {
        "dietaGUID": dieta_guid,
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


# ---------------------------------------------------------
#  KROK 2 – doplnkové potreby (strava, družina, etická)
# ---------------------------------------------------------
def koncept_krok_2(dieta_guid: str, prihlaska_guid: str):
    return {
        "dietaGUID": dieta_guid,
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
            "druhVychovyKod": "1",     # Etická výchova
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


# ---------------------------------------------------------
#  KROK 3 – výber školy (ZŠ)
# ---------------------------------------------------------
def koncept_krok_3(dieta_guid: str, prihlaska_guid: str):
    return {
        "dietaGUID": dieta_guid,
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

        # Zoznam škôl priradených k prihláške
        "saSZ": [
            {
                "saSZEDUID": 910000787,
                "poradie": 1,
                "kolo": 1,
                "poradieNaPrihlaske": 1
            }
        ],

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


# ---------------------------------------------------------
#  KROK 4 – jazyk + VIN (výber úvodného ročníka VIN)
# ---------------------------------------------------------
def koncept_krok_4(dieta_guid: str, prihlaska_guid: str):
    return {
        "dietaGUID": dieta_guid,
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


# ---------------------------------------------------------
#  KROK 5 – zákonný zástupca + adresa
# ---------------------------------------------------------
def koncept_krok_5(dieta_guid: str, prihlaska_guid: str):
    return {
        "dietaGUID": dieta_guid,
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
