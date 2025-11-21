#!/usr/bin/env python3
import requests
import json
import sys
import time

# ----------------------------------------------------------
#  IMPORTY Z CONFIG
# ----------------------------------------------------------
from config.settings import (
    HOST,
    CSRF,
    IAM_TOKEN,
    COOKIE_BUNDLE,
    SUBJEKT_GUID
)


# ----------------------------------------------------------
#  HLAVIČKY – rovnaké ako COMMON_HEADERS
# ----------------------------------------------------------
HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Requestverificationtoken": CSRF,
    "X-Token-Descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE
}


# ----------------------------------------------------------
#  PRÁCA S PRIHLÁŠKAMI
# ----------------------------------------------------------

def get_prihlasky():
    """Načíta zoznam prihlášok pre subjekt."""
    url = f"{HOST}/api/vratenieZoznamuPrihlasokSubjektu"
    payload = {"SubjektGUID": SUBJEKT_GUID}

    resp = requests.post(url, json=payload, headers=HEADERS)

    if resp.status_code != 200:
        print(f"❌ Chyba pri načítaní prihlášok: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    prihlasky = data.get("prihlaska", [])

    print(f"🔍 Našiel som {len(prihlasky)} prihlášok.")
    return prihlasky


def delete_prihlaska(guid):
    """Vymaže prihlášku podľa GUID."""

    url = f"{HOST}/api/vymazPrihlasky"
    payload = {"PrihlaskaGUID": guid}

    resp = requests.post(url, json=payload, headers=HEADERS)

    if resp.status_code != 200:
        print(f"❌ Chyba pri mazaní prihlášky {guid}:")
        print(resp.text)
        return False

    print(f"🗑️  Vymazaná prihláška: {guid}")
    return True


# ----------------------------------------------------------
#  PRÁCA S DEŤMI
# ----------------------------------------------------------

def get_deti():
    """Načíta všetky deti v subjekte."""
    url = f"{HOST}/api/vratenieZoznamuDeti"
    payload = {"guid": SUBJEKT_GUID, "lenPlatne": True}

    resp = requests.post(url, json=payload, headers=HEADERS)

    if resp.status_code != 200:
        print(f"❌ Chyba pri načítaní detí: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    deti = data.get("dieta", [])

    print(f"🧒 Našiel som {len(deti)} detí.")
    return deti


def delete_dieta(guid):
    """Vymaže dieťa podľa GUID."""
    url = f"{HOST}/api/vymazDietata"
    payload = {"guid": guid}

    resp = requests.post(url, json=payload, headers=HEADERS)

    if resp.status_code != 200:
        print(f"❌ Chyba pri mazaní dieťaťa {guid}:")
        print(resp.text)
        return False

    print(f"🗑️  Vymazané dieťa: {guid}")
    return True


# ----------------------------------------------------------
#  MAIN – PRIHLÁŠKY → DETI
# ----------------------------------------------------------

if __name__ == "__main__":
    print("\n🧼 Spúšťam čistenie prihlášok a detí...\n")

    # 1) Vymazanie prihlášok
    prihlasky = get_prihlasky()

    for p in prihlasky:
        delete_prihlaska(p["prihlaskaGUID"])

    print("⏳ Čakám 1 sekundu, kým sa zmeny prejavia...")
    time.sleep(1)

    # 2) Vymazanie detí
    deti = get_deti()

    for d in deti:
        if not d.get("existujeNezrusenaPrihlaska", False):
            delete_dieta(d["guid"])
        else:
            print(f"⚠️ Dieťa {d['guid']} nemožno vymazať – má aktívnu prihlášku.")

    print("\n✨ Hotovo – všetky prihlášky aj deti sú vymazané.\n")
