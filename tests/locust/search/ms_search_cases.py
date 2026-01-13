from tests.locust.search.common import SK_ROK, LAT, LON

MS_SEARCH_CASES = [
    ("MS / BASE 20 / 4km", 3, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "4"
    }),

    ("MS / BASE 100k / 4km", 1, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "4"
    }),

    ("MS / BASE 20 / 30km", 3, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "7"
    }),

    ("MS / BASE 100k / 30km", 1, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 100000,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "7"
    }),

    ("MS / JAZYK Anglický", 2, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "7",
        "jazyk": [{"dopInfo": "J", "poznamka": "Anglický"}]
    }),

    ("MS / SÚKROMNÉ", 2, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "7",
        "formaVlastnictva": [{"kod": "2"}]
    }),

    ("MS / KOMBI JAZYK + SÚKROMNÉ + TYP", 1, {
        "skolskyRokKod": SK_ROK,
        "ms": True,
        "zs": False,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": LAT,
        "zemepisnaDlzka": LON,
        "vzdialenostKod": "7",
        "jazyk": [{"dopInfo": "J", "poznamka": "Anglický"}],
        "formaVlastnictva": [{"kod": "2"}],
        "typSaSZ": [
            {"kod": "115"},
            {"kod": "116"},
            {"kod": "111"},
            {"kod": "112"},
            {"dopInfo": "6NKS"}
        ]
    }),
]
