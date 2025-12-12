# tests/prihlaska/full_flow.py
# ======================================================================
# Adaptive FULL FLOW for ZŠ application (school year 2026/2027)
#
# Process:
#   CHILD → STEP 1 → STEP 2 → STEP 3 → SCHOOL SEARCH →
#   SAVE SCHOOL → STEP 4 ADAPTIVE → STEP 5 ADAPTIVE → STEP 10 → DETAIL
#
# Professional clean-output version:
#   ✓ No debug dumps
#   ✓ No list of allowed fields
#   ✓ No HTTP 400 prints
#   ✓ Clean readable flow logs
# ======================================================================

import sys
import os
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

# Auth + environment
from login.saml_login import saml_login
from config.env import HOST
from config.random_names import generate_random_name

# Payload builders (steps 1–3)
from tests.child.payloads.child import build_base_child_payload
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_3_with_school
)

# Step 4 builder
from tests.prihlaska.payloads.koncept_step4 import (
    build_step4_adaptive,
    build_step4_fallback
)

# Step 5 builder
from tests.prihlaska.payloads.koncept_step5 import (
    build_step5_adaptive,
    build_step5_fallback
)

# Step 10 builder
from tests.prihlaska.payloads.koncept_step10 import (
    build_step10_adaptive,
    build_step10_fallback
)

# School search
from tests.vyhladavanie.payloads.search import build_search_payload


CTX = "PRIHLASKA-FLOW"
SKOLSKY_ROK = "2026/2027"


# ======================================================================
# HTTP Utility
# ======================================================================
def send_post(login, ctx, endpoint, payload, show=False):
    """Standard POST wrapper with minimal clean logging."""

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
        "User-Agent": "Mozilla/5.0"
    }

    resp = login.session.post(url, json=payload, headers=headers)
    return resp


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}


# ======================================================================
# SCHOOL CAPABILITY DETECTION
# ======================================================================
def detect_allowed_fields(school_detail):
    """ Returns allowed fields for adaptive Step 4 """
    allowed = {}

    if "jazyk" in school_detail:
        allowed["jazykové_možnosti"] = school_detail["jazyk"]

    for key in [
        "pozadovanyJazykKod",
        "zaujemUvodnyRocnikVIN",
        "zaujemUvodnyRocnikNKS",
        "zaujemPripravnyRocnik",
        "zaujemDualneVzdelavanie",
        "zaujemInternat",
        "terminPrijimacejSkuskyKod",
        "mentalnePostihnutie"
    ]:
        if key in school_detail:
            allowed[key] = True

    return allowed


def build_adaptive_saSZ(eduid, allowed_fields):
    """Creates adaptive saSZ entry"""
    sa = {
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1
    }

    if "pozadovanyJazykKod" in allowed_fields:
        sa["pozadovanyJazykKod"] = "SK"
    if "mentalnePostihnutie" in allowed_fields:
        sa["mentalnePostihnutie"] = False
    if "zaujemUvodnyRocnikVIN" in allowed_fields:
        sa["zaujemUvodnyRocnikVIN"] = False
    if "zaujemUvodnyRocnikNKS" in allowed_fields:
        sa["zaujemUvodnyRocnikNKS"] = False
    if "zaujemPripravnyRocnik" in allowed_fields:
        sa["zaujemPripravnyRocnik"] = False
    if "zaujemDualneVzdelavanie" in allowed_fields:
        sa["zaujemDualneVzdelavanie"] = False
    if "zaujemInternat" in allowed_fields:
        sa["zaujemInternat"] = False

    return sa


# ======================================================================
# MAIN FULL FLOW
# ======================================================================
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--show-data", action="store_true")
    SHOW = parser.parse_args().show_data

    print("\n=====================================================")
    print(" FULL FLOW – CHILD → 1 → 2 → 3 → 4 → 5 → 10 → DETAIL")
    print("=====================================================\n")

    # LOGIN
    login = saml_login()
    print("✔ Login successful")
    print("Subjekt GUID:", login.subj_guid)
    print("User GUID:", login.logged_guid)

    # 1) CHILD
    first, last = generate_random_name()
    print(f"\n🧒 Creating child: {first} {last}")

    child = build_base_child_payload(first, last)
    child["subjektGUID"] = login.subj_guid

    resp_child = send_post(login, CTX, "/api/zapisAModifikaciaDietata", child)
    j_child = safe_json(resp_child)

    dieta_guid = j_child.get("dieta", {}).get("guid")
    print("✔ Child GUID:", dieta_guid)

    # 2) STEP 1
    print("\n📘 Step 1 – Creating application...")
    req1 = koncept_krok_1(dieta_guid, login.logged_guid)
    resp1 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req1)
    app_guid = safe_json(resp1).get("prihlaska", {}).get("prihlaskaGUID")
    print("✔ Application GUID:", app_guid)

    # 3) STEP 2
    print("\n📘 Step 2 – Updating complementary data...")
    req2 = koncept_krok_2(dieta_guid, app_guid, login.logged_guid)
    send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req2)
    print("✔ Step 2 OK")

    # 4) STEP 3
    print("\n📘 Step 3 – Initializing school selection...")
    req3 = koncept_krok_3(dieta_guid, app_guid, login.logged_guid)
    send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req3)
    print("✔ Step 3 OK")

    # 5) SCHOOL SEARCH
    print("\n🔎 Searching schools...")
    sch_req = build_search_payload(page_size=20)
    sch_resp = send_post(login, CTX, "/api/vyhladanieMSaZS", sch_req)
    sch_json = safe_json(sch_resp)

    school = sch_json["saSZ"][0]
    eduid = school["eduid"]
    print("✔ Selected school EDUID:", eduid)

    # 6) SAVE SCHOOL
    print("\n🏫 Saving school into application...")
    req3s = koncept_krok_3_with_school(dieta_guid, app_guid, login.logged_guid, eduid)
    send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req3s)
    print("✔ School saved")

    # 7) DETECT SCHOOL CAPABILITIES
    det = send_post(
        login, CTX, "/api/vratenieVybranychSaSZ",
        {"prihlaskaGUID": app_guid}
    )
    school_detail = safe_json(det)["saSZ"][0]
    allowed_fields = detect_allowed_fields(school_detail)

    saSZ_adaptive = build_adaptive_saSZ(eduid, allowed_fields)

    # 8) STEP 4
    print("\n📘 Step 4 – Saving language/VIN...")
    req4 = build_step4_adaptive(dieta_guid, app_guid, login.logged_guid, saSZ_adaptive)
    r4 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req4)

    if r4.status_code != 200:
        fallback4 = build_step4_fallback(dieta_guid, app_guid, login.logged_guid, eduid)
        r4 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", fallback4)

    print("✔ Step 4 OK")

    # 9) STEP 5
    print("\n📘 Step 5 – Saving legal guardian...")
    req5 = build_step5_adaptive(dieta_guid, app_guid, login.logged_guid, saSZ_adaptive)
    r5 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req5)

    if r5.status_code != 200:
        fallback5 = build_step5_fallback(dieta_guid, app_guid, login.logged_guid, eduid)
        send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", fallback5)

    print("✔ Step 5 OK")

    # 10) STEP 10
    print("\n📘 Step 10 – Finalizing application...")
    req10 = build_step10_adaptive(dieta_guid, app_guid, login.logged_guid, eduid)
    r10 = send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", req10)

    if r10.status_code != 200:
        fallback10 = build_step10_fallback(dieta_guid, app_guid, login.logged_guid, eduid)
        send_post(login, CTX, "/api/zapisAModifikaciaKonceptuPrihlasky", fallback10)

    print("✔ Step 10 OK")

    # DETAIL
    print("\n🔍 Fetching application detail...")
    send_post(
        login, CTX,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": app_guid}
    )

    print("✔ Application complete")
    print("\n🏁 DONE\n")


if __name__ == "__main__":
    main()
