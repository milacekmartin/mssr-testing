# tests/prihlaska/payloads/koncept.py

def koncept_krok_1(dieta_guid):
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": 1,
        "typPrihlasky": "ZŠ",
        "skolskyRokKod": "2026/2027",
    }

def koncept_krok_2(dieta_guid, prihlaska_guid):
    return {
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "krokZadavania": 2,
        "typPrihlasky": "ZŠ",
        "skolskyRokKod": "2026/2027",
        "ulozitDoplnujucePotreby": True,
        "doplnujucePotreby": {
            "stravovanie": True,
            "druzina": True
        }
    }

def koncept_krok_3(dieta_guid, prihlaska_guid):
    return {
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "krokZadavania": 3,
        "ulozitVyberSkoly": True
    }

def koncept_krok_4(dieta_guid, prihlaska_guid):
    return {
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "krokZadavania": 4,
        "ulozitZakonnyZastupca": True
    }

def koncept_krok_5(dieta_guid, prihlaska_guid):
    return {
        "dietaGUID": dieta_guid,
        "prihlaskaGUID": prihlaska_guid,
        "krokZadavania": 5,
        "ulozitInformacieZS": True
    }

NEG_KONCEPT_PAYLOADS = {
    "NEG-NO-GUID": {"dietaGUID": None},
    "NEG-BAD-KROK": {"krokZadavania": "AAAA"},
    "NEG-EMPTY": {},
}
