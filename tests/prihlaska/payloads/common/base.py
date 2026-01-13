# tests/prihlaska/payloads/common/base.py

from config.runtime import SKOLSKY_ROK

def base_payload(
    dieta_guid,
    prihlaska_guid,
    user_guid,
    krok,
    typ,
    kolo=1,
):
    """
    Base payload for all prihlaska steps.
    """
    return {
        "dietaGUID": dieta_guid,
        "krokZadavania": krok,
        "kolo": kolo,
        "zatvoreniePrihlasky": False,
        "typPrihlasky": typ,
        "skolskyRokKod": SKOLSKY_ROK,
        "prihlaskaGUID": prihlaska_guid,
        "prihlasenaOsobaGUID": user_guid,

        # flags (default false)
        "ulozitDoplnujucePotreby": False,
        "ulozitVyberSkoly": False,
        "ulozitZakonnyZastupca": False,
        "ulozitInformacieZS": False,
        "ulozitVysledkyVzdelavaniaZS": False,
        "ulozitSutaze": False,
    }
