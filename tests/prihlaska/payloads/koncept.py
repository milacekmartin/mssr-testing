# tests/prihlaska/payloads/koncept.py
# Kompletné payloady prihlášky podľa aktuálneho API ePrihlášky

from tests.prihlaska.payloads.common import SKOLSKY_ROK, PRIHLASKA_TYP


# ============================================================
# KROK 1 – Vytvorenie konceptu prihlášky
# ============================================================
def koncept_krok_1(dieta_guid, prihlasenaOsobaGUID):
    """
    Krok 1 (vytvorenie prihlášky) – podľa reálneho API:
    - musí obsahovať všetky 'ulozit*' polia
    - musí obsahovať 'kolo', 'zatvoreniePrihlasky', 'prihlaskaGUID'
    """
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 1,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,       # "ZŠ"
        "skolskyRokKod": SKOLSKY_ROK,        # "2026/2027"
        "prihlaskaGUID": None,
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,

        # všetky tieto polia MUSIA byť prítomné v Krok 1
        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False
    }


# ============================================================
# KROK 2 – Doplnujúce potreby
# ============================================================
def koncept_krok_2(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID):
    """
    Krok 2 – doplnujuce potreby + špeciálne VVP
    """
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 2,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": prihlaska_guid,
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,

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


# ============================================================
# KROK 3 – Vyber školy (bez výberu)
# ============================================================
def koncept_krok_3(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID):
    """
    Krok 3 – zatiaľ bez školy, iba prázdne pole saSZ
    """
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 3,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": prihlaska_guid,
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,

        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False,

        "saSZ": []     # žiadna škola zatiaľ
    }


# ============================================================
# KROK 3 – Vyber školy (s uložením školy)
# ============================================================
def koncept_krok_3_with_school(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID, eduid):
    """
    Krok 3 – s konkrétnou školou (eduid)
    """
    base = koncept_krok_3(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID)
    base["saSZ"] = [{
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1
    }]
    base["ulozitVyberSkoly"] = True
    return base


# ============================================================
# KROK 4 – Jazyk / VIN (musí obsahovať kompletne FE payload)
# ============================================================
def koncept_krok_4(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID, eduid):
    return {
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "skolskyRokKod": "2026/2027",
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

        # musia existovať, aj keď sú prázdne:
        "zZ1DoplnujuceUdaje": {},
        "zZ2DoplnujuceUdaje": {
            "existujeZZ2": None,
            "suhlasZZ2": None,
            "dovodNesuhlasuKod": None
        },

        # musia byť prítomné aj v kroku 4
        "doplnujucePotreby": {
            "strpozemna": True,
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
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False
    }




# ============================================================
# KROK 5 – Informácie ZŠ (môže byť prázdne)
# ============================================================
def koncept_krok_5(dieta_guid, prihlaska_guid, prihlasenaOsobaGUID):
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 5,
        "kolo": 1,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": PRIHLASKA_TYP,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": prihlaska_guid,
        "prihlasenaOsobaGUID": prihlasenaOsobaGUID,
        "ulozitInformacieZS": True
    }


# ============================================================
# NEGATÍVNE PAYLOADY
# ============================================================
NEG_KONCEPT_PAYLOADS = {
    "NEG-NO-GUID": {"dietaGUID": None},
    "NEG-BAD-KROK": {"krokZadavania": "AAAA"},
    "NEG-EMPTY": {},
}
