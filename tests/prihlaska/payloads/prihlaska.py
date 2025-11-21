# locust/tests/prihlaska/payloads/prihlaska.py

from config.settings import SUBJEKT_GUID, SKOLSKY_ROK_KOD_2026


def build_base_prihlaska_payload(child_guid=None):
    """
    Základný payload pre vytvorenie prihlášky do ZŠ.
    Toto je MINIMÁLNY payload ktorý server bežne očakáva.
    """

    return {
        "guidPrihlasky": None,
        "subjektGuid": SUBJEKT_GUID,
        "dietaGuid": child_guid,           # môže byť null, ak sa ešte nevytvára prihláška na dieťa
        "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
        "typPrihlasky": "ZS",              # alebo "MS" alebo "SS"
        "rozpracovane": False,
        "platne": True,

        # minimálne údaje o škole (ZŠ)
        "saszEduId": None,
        "saszNazov": None,
        "saszTypPouzivatelaKod": None,
        "saszTypKod": None,

        # rozsirené — dá sa doplniť neskôr
        "udajeOZiajateli": {},
        "udajeODietati": {},
        "suhlasy": {},
        "prilohy": [],

        # metadata
        "narodnostZRFO": False,
        "adresaZRFO": False,
        "datumNarodeniaZRFO": False
    }
