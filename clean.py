#!/usr/bin/env python3
import sys
import os
import time
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ROOT)
sys.path.append(PARENT)

from login.saml_login import saml_login
from config.env import HOST


CTX = "CLEAN"


def send_post(login, ctx, endpoint, payload, show_data=False):
    url = f"{HOST}{endpoint}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": HOST,
        "Referer": f"{HOST}/Moj-profil2",
        "RequestVerificationToken": login.csrf,
        "x-token-descriptor": login.token_desc,
        "Cookie": login.cookie_bundle,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
    }

    print(f"[{ctx}] POST {endpoint}")

    if show_data:
        print("\n📤 REQUEST PAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    resp = login.session.post(url, json=payload, headers=headers)
    print(f"[{ctx}] → {resp.status_code}")

    if show_data:
        print("\n📥 RESPONSE:")
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except:
            print(resp.text)
        print()

    return resp


def get_prihlasky(login, show_data=False):
    payload = {"SubjektGUID": login.subj_guid}

    resp = send_post(login, CTX, "/api/vratenieZoznamuPrihlasokSubjektu", payload, show_data)

    if resp.status_code != 200:
        print(f"❌ Nepodarilo sa načítať prihlášky!")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    prihlasky = data.get("prihlaska", [])
    print(f"🔍 Našiel som {len(prihlasky)} prihlášok.")
    return prihlasky


def delete_prihlaska(login, guid, show_data=False):
    payload = {"PrihlaskaGUID": guid}

    resp = send_post(login, CTX, "/api/vymazPrihlasky", payload, show_data)

    if resp.status_code != 200:
        print(f"❌ Chyba pri mazaní prihlášky {guid}:")
        print(resp.text)
        return False

    print(f"🗑️  Vymazaná prihláška: {guid}")
    return True


def get_deti(login, show_data=False):
    payload = {"guid": login.subj_guid, "lenPlatne": True}

    resp = send_post(login, CTX, "/api/vratenieZoznamuDeti", payload, show_data)

    if resp.status_code != 200:
        print(f"❌ Chyba pri načítaní detí!")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    deti = data.get("dieta", [])
    print(f"🧒 Našiel som {len(deti)} detí.")
    return deti


def delete_dieta(login, guid, show_data=False):
    payload = {"guid": guid}

    resp = send_post(login, CTX, "/api/vymazDietata", payload, show_data)

    if resp.status_code != 200:
        print(f"❌ Chyba pri mazaní dieťaťa {guid}:")
        print(resp.text)
        return False

    print(f"🗑️  Vymazané dieťa: {guid}")
    return True


if __name__ == "__main__":
    SHOW = "--show-data" in sys.argv

    print("\n=======================================")
    print(" 🧼 CLEANUP TOOL — DELETE ALL DATA")
    print(" Prihlášky + Deti podľa prihlásenej osoby")
    print("=======================================\n")

    # LOGIN
    login = saml_login()
    print("✔️ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("Prihl. osoba GUID:", login.logged_guid)

    print("\n➡️ Začínam čistenie prihlášok...\n")

    prihlasky = get_prihlasky(login, SHOW)

    for p in prihlasky:
        delete_prihlaska(login, p.get("prihlaskaGUID"), SHOW)

    print("\n⏳ Čakám 1 sekundu na propagáciu zmien...")
    time.sleep(1)

    print("\n➡️ Začínam čistenie detí...\n")

    deti = get_deti(login, SHOW)

    for d in deti:
        if not d.get("existujeNezrusenaPrihlaska", False):
            delete_dieta(login, d.get("guid"), SHOW)
        else:
            print(f"⚠️ Dieťa {d.get('guid')} nemožno vymazať – má aktívnu prihlášku.")

    print("\n✨ Hotovo — všetky dáta boli vymazané.\n")
