# tests/vyhladavanie/payloads/search_locust.py
# Fully working search payload used in working full_flow.py.
# Locust must use the SAME payload to get valid schools.


def build_search_payload_locust():
    return {
        "skolskyRokKod": "2026/2027",
        "ms": False,
        "zs": True,
        "pocetZaznamovNaStranku": 20,
        "cisloStranky": 1,
        "zemepisnaSirka": 48.165064,
        "zemepisnaDlzka": 17.145673,
        "vzdialenostKod": "7"
    }
