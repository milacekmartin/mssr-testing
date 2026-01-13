# tests/vyhladavanie/search_cases/ms.py

from config.runtime import SKOLSKY_ROK

LAT = 48.1486
LON = 17.1077

MS_SEARCH_CASES = [
    # --------------------------------------------------
    # BASIC
    # --------------------------------------------------
    ("MS / BASE 20", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "4",
    }),

    ("MS / BASE 100k", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "4",
    }),

    # --------------------------------------------------
    # MS ONLY
    # --------------------------------------------------
    ("MS / ONLY 20", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
    }),

    ("MS / ONLY 100k", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # TEXT SEARCH
    # --------------------------------------------------
    ("MS / TEXT bratislava", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "text": "bratislava",
    }),

    ("MS / TEXT bratislava 100k", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
        "text": "bratislava",
    }),

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------
    ("MS / PAGE 2", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 2,
    }),

    ("MS / PAGE 3", {
        "skolskyRokKod": SKOLSKY_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 3,
    }),
]
