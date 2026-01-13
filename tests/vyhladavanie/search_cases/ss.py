# tests/vyhladavanie/search_cases/ss.py

from config.runtime import SKOLSKY_ROK

LAT = 48.1486
LON = 17.1077

SS_SEARCH_CASES = [
    # --------------------------------------------------
    # BASIC SEARCH
    # --------------------------------------------------
    ("SŠ / BASE 20", {
        "skolskyRok": SKOLSKY_ROK,
        "cisloStranky": 1,
        "pocetZaznamovNaStranku": 20,
    }),

    ("SŠ / BASE 100", {
        "skolskyRok": SKOLSKY_ROK,
        "cisloStranky": 1,
        "pocetZaznamovNaStranku": 100,
    }),

    # --------------------------------------------------
    # REGION + DISTRICTS
    # --------------------------------------------------
    ("SŠ / BA kraj + okresy", {
        "skolskyRok": SKOLSKY_ROK,
        "cisloStranky": 1,
        "kraj": [{
            "krajKod": "1",
            "okres": [
                {"okresKod": "6101"},
                {"okresKod": "6102"},
                {"okresKod": "6103"},
            ],
        }],
    }),

    # --------------------------------------------------
    # TALENT-BASED PROGRAMS
    # --------------------------------------------------
    ("SŠ / TALENTOVÉ", {
        "skolskyRok": SKOLSKY_ROK,
        "talentovy": True,
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # DUAL EDUCATION
    # --------------------------------------------------
    ("SŠ / DUAL", {
        "skolskyRok": SKOLSKY_ROK,
        "dualneVzdelavanie": True,
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # ENTRANCE EXAM REQUIRED
    # --------------------------------------------------
    ("SŠ / PRIJIMACIA SKUSKA", {
        "skolskyRok": SKOLSKY_ROK,
        "prijimaciaSkuska": True,
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # LANGUAGE FILTER
    # --------------------------------------------------
    ("SŠ / ANGLICKÝ JAZYK", {
        "skolskyRok": SKOLSKY_ROK,
        "jazykKategoria": [{
            "dopInfo": "J",
            "poznamka": "Anglický",
        }],
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # STUDY DURATION
    # --------------------------------------------------
    ("SŠ / 4 ROCNE", {
        "skolskyRok": SKOLSKY_ROK,
        "dlzkaStudia": ["4 ročné"],
        "cisloStranky": 1,
    }),

    # --------------------------------------------------
    # COMBINED REAL-WORLD SCENARIO
    # --------------------------------------------------
    ("SŠ / KOMBI BA + ANJ + TALENT", {
        "skolskyRok": SKOLSKY_ROK,
        "talentovy": True,
        "jazykKategoria": [{
            "dopInfo": "J",
            "poznamka": "Anglický",
        }],
        "kraj": [{
            "krajKod": "1",
        }],
        "cisloStranky": 1,
    }),
]
