# tests/prihlaska/payloads/vyhladavanie.py

def search_base_payload(limit):
    return {
        "skolskyRokKod": "2026/2027",
        "ms": False,
        "zs": True,
        "limit": limit
    }

def search_slovak_payload(limit):
    return {
        "skolskyRokKod": "2026/2027",
        "jazykKod": "J",
        "limit": limit
    }

def search_statne_payload(limit):
    return {
        "skolskyRokKod": "2026/2027",
        "formaKod": "3",
        "limit": limit
    }

def search_typy_payload(limit):
    return {
        "skolskyRokKod": "2026/2027",
        "typKod": "211",
        "limit": limit
    }

NEG_SEARCH_PAYLOADS = {
    "NEG-EMPTY": {},
    "NEG-NO-YEAR": {"zs": True, "limit": 20},
    "NEG-BAD-LIMIT": {"skolskyRokKod": "2026/2027", "limit": "AAAA"},
    "NEG-BAD-FORM": {"skolskyRokKod": "2026/2027", "formaKod": 999},
}
