# tests/vyhladavanie/payloads/search.py
# FULLY UPDATED payloads for MS/ZS search (2025 API)

def build_search_payload(
    page_size=20,
    page_number=1,
    ms=False,
    zs=True,
    text="",
    vzdialenostKod=None,
    jazykKod=None,
    formaKod=None,
    typKod=None,
    zemepisnaSirka=None,
    zemepisnaDlzka=None,
):
    return {
        "skolskyRokKod": "2026/2027",
        "ms": ms,
        "zs": zs,
        "pocetZaznamovNaStranku": page_size,
        "cisloStranky": page_number,
        "text": text,
        "zemepisnaSirka": zemepisnaSirka,
        "zemepisnaDlzka": zemepisnaDlzka,
        "vzdialenostKod": vzdialenostKod,
        "jazykKod": jazykKod,
        "formaKod": formaKod,
        "typKod": typKod
    }


SEARCH_TEST_CONFIGS = [
    ("BASE 20", {"page_size": 20}),
    ("BASE 100k", {"page_size": 100000}),
    ("SLOVAK 20", {"page_size": 20, "jazykKod": "J"}),
    ("STATNE 20", {"page_size": 20, "formaKod": "3"}),
    ("TYP KOD 211", {"page_size": 20, "typKod": "211"}),
    ("TEXT BRATISLAVA", {"page_size": 20, "text": "bratislava"}),
    ("PAGE 2", {"page_size": 20, "page_number": 2}),
    ("PAGE 3", {"page_size": 20, "page_number": 3}),
]
