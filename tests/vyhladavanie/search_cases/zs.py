# tests/vyhladavanie/search_cases/zs.py

from config.runtime import SKOLSKY_ROK

ZS_SEARCH_CASES = [
    # --------------------------------------------------
    # BASIC
    # --------------------------------------------------
    ("ZŠ / BASE 20", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "text": "",
    }),

    ("ZŠ / BASE 100k", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
        "text": "",
    }),

    # --------------------------------------------------
    # ZŠ ONLY
    # --------------------------------------------------
    ("ZŠ / ONLY 20", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
    }),

    ("ZŠ / ONLY 100k", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # TEXT
    # --------------------------------------------------
    ("ZŠ / TEXT Bratislava", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "text": "Bratislava",
    }),

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------
    ("ZŠ / PAGE 2", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 2,
    }),

    ("ZŠ / PAGE 3", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 3,
    }),
]
