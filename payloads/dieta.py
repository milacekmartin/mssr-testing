# payloads/dieta.py
# =================
#
# Payload pre vytvorenie dieťaťa.
# first_name a last_name sú dynamické hodnoty
# generované v scenároch.

from config.settings import SUBJEKT_GUID


def create_dieta_payload(first_name: str, last_name: str):
    """
    Vytvorí payload pre zápis dieťaťa.
    Meno aj priezvisko sú dynamicky generované.
    Ostatné hodnoty sú fixné tak, ako boli pozorované v API.
    """

    return {
        "subjektGUID": SUBJEKT_GUID,
        "dietaGUID": None,
        "rodneCislo": None,

        "meno": first_name,
        "priezvisko": last_name,
        "rodnePriezvisko": None,

        "datumNarodenia": "2020-01-25",
        "miestoNarodenia": "Bratislava",

        "pohlavieKod": "1",
        "narodnostKod": "2",

        "statnaPrislusnost": [
            {"statnaPrislusnostKod": "211"}
        ],

        "materinskyJazykKod": "SK",
        "inyMaterinskyJazykKod": None,

        "rozpracovane": False,
        "platne": True,

        # Trvalý pobyt (TP)
        "tpStatKod": "211",
        "tpObecKod": "582000",
        "tppsc": "84104",
        "tpUlicaKod": None,
        "tpSupisneCislo": "2",
        "tpOrientacneCislo": None,
        "tpAdresaMimoSR": None,
        "adresaTPZhodnaSTPRodica": False,

        # Zvyčajný pobyt (ZP)
        "zpStatKod": "211",
        "zpObecKod": "582000",
        "zppsc": "84104",
        "zpUlicaKod": None,
        "zpSupisneCislo": "2",
        "zpOrientacneCislo": None,
        "zpAdresaMimoSR": None,
        "adresaObvyklaZhodnaSTP": True,

        # Príznaky z RFO / ZRFO
        "narodnostZRFO": False,
        "miestoNarodeniaZRFO": False
    }
