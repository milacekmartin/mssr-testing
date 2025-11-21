# payloads/vyhladavanie.py
# ==========================
#
# Payloady pre všetky ZŠ/MŠ vyhľadávacie endpointy.
#
# Funkcie generujú payload spotrebovaný jednotlivými
# vyhľadávacími krokmi v ZŠ scenári (11–22).

from config.settings import SKOLSKY_ROK_KOD_2026


# ---------------------------------------------------------
#  KROK 10 – vyhľadávanie adresy
# ---------------------------------------------------------
def search_address_payload():
    return {
        "text": "Bratislava 2, Bratislava",
        "_": "1763398868392"
    }


# ---------------------------------------------------------
#  Base payload – všetky vyhľadávania začínajú tu
# ---------------------------------------------------------
def search_base_payload(count: int):
    return {
        "skolskyRokKod": SKOLSKY_ROK_KOD_2026,
        "ms": False,
        "zs": True,

        "pocetZaznamovNaStranku": count,
        "cisloStranky": 1,

        "zemepisnaSirka": 48.199036,
        "zemepisnaDlzka": 17.054286,
        "vzdialenostKod": "7"
    }


# ---------------------------------------------------------
#  Vyhľadávanie slovenských škôl
# ---------------------------------------------------------
def search_slovak_payload(count: int):
    payload = search_base_payload(count)
    payload["jazyk"] = []
    payload["slovensky"] = True
    return payload


# ---------------------------------------------------------
#  Vyhľadávanie štátnych škôl
# ---------------------------------------------------------
def search_statne_payload(count: int):
    payload = search_slovak_payload(count)
    payload["formaVlastnictva"] = [{"kod": "3"}]   # štátne
    return payload


# ---------------------------------------------------------
#  Vyhľadávanie podľa typov škôl
# ---------------------------------------------------------
def search_typy_payload(count: int):
    payload = search_statne_payload(count)
    payload["typSaSZ"] = [
        {"kod": "211"},   # Základná škola
        {"kod": "221"},   # ZŠ I. stupeň
        {"kod": "223"},   # ZŠ I. stupeň internátna
        {"kod": "231"},   # ZŠ II. stupeň
        {"kod": "233"},   # ZŠ II. stupeň internátna
        {"kod": "213"},   # ZŠ internátna
    ]
    return payload
