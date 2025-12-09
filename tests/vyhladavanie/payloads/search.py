# tests/vyhladavanie/payloads/search.py

def build_search_payload(
    page_size=20,
    page_number=1,
    ms=False,
    zs=True,
    text=""
):
    """Universal payload builder for MS/ZS vyhľadávanie."""
    return {
        "skolskyRokKod": "2026/2027",
        "ms": ms,
        "zs": zs,
        "pocetZaznamovNaStranku": page_size,
        "cisloStranky": page_number,
        "text": text
    }


# Pre-definované testy (kopírované z pôvodného súboru)
SEARCH_TEST_CONFIGS = [
    ("base 20", {"page_size": 20}),
    ("base 100k", {"page_size": 100000}),
    ("MS only 20", {"page_size": 20, "ms": True, "zs": False}),
    ("MS only 100k", {"page_size": 100000, "ms": True, "zs": False}),
    ("ZS only 20", {"page_size": 20, "ms": False, "zs": True}),
    ("ZS only 100k", {"page_size": 100000, "ms": False, "zs": True}),
    ("Both MS+ZS 20", {"page_size": 20, "ms": True, "zs": True}),
    ("Both MS+ZS 100k", {"page_size": 100000, "ms": True, "zs": True}),
    ("Text search 20", {"page_size": 20, "text": "bratislava"}),
    ("Text search 100k", {"page_size": 100000, "text": "bratislava"}),
    ("Page 2 test", {"page_size": 20, "page_number": 2}),
    ("Page 3 test", {"page_size": 20, "page_number": 3}),
]
