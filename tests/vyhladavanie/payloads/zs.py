# tests/vyhladavanie/payloads/zs.py

from config.runtime import SKOLSKY_ROK

def build_search_payload_zs(**kwargs):
    payload = {
        "skolskyRokKod": kwargs.get("skolskyRokKod", SKOLSKY_ROK),
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": kwargs.get("pocetZaznamovNaStranku", 20),
        "cisloStranky": kwargs.get("cisloStranky", 1),
        "text": kwargs.get("text", ""),
    }

    if "kraj" in kwargs:
        payload["kraj"] = kwargs["kraj"]

    if "okres" in kwargs:
        payload["okres"] = kwargs["okres"]

    if "formaVlastnictva" in kwargs:
        payload["formaVlastnictva"] = kwargs["formaVlastnictva"]

    if "jazyk" in kwargs:
        payload["jazyk"] = kwargs["jazyk"]

    if "typSaSZ" in kwargs:
        payload["typSaSZ"] = kwargs["typSaSZ"]

    return payload
