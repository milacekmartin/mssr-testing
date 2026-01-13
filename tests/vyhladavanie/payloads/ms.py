# tests/vyhladavanie/payloads/search.py
# ============================================================
# PAYLOAD BUILDER – MS SEARCH
# ============================================================

def build_search_payload(**kwargs):
    """
    Build payload for MS search (/api/vyhladanieMSaZS)
    """

    payload = {
        "skolskyRokKod": kwargs.get("skolskyRokKod"),
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": kwargs.get("pocetZaznamovNaStranku", 20),
        "cisloStranky": kwargs.get("cisloStranky", 1),
        "zemepisnaSirka": kwargs.get("zemepisnaSirka"),
        "zemepisnaDlzka": kwargs.get("zemepisnaDlzka"),
        "vzdialenostKod": kwargs.get("vzdialenostKod"),
        "text": kwargs.get("text", ""),
    }

    # voliteľné filtre
    for key in [
        "kraj",
        "okres",
        "jazyk",
        "formaVlastnictva",
        "typSaSZ",
    ]:
        if key in kwargs:
            payload[key] = kwargs[key]

    return payload
