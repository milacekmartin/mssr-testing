# tests/prihlaska/full_flow_locust.py
# FULL FIXED LOCUST FLOW – identical behaviour to full_flow.py

import json
import uuid
from config.random_names import generate_random_name

# Payload builders – use ONLY UI versions (always valid)
from tests.prihlaska.payloads.koncept import (
    koncept_krok_1,
    koncept_krok_2,
    koncept_krok_3,
    koncept_krok_3_with_school,
)

from tests.prihlaska.payloads.koncept_step4 import build_step4_fallback
from tests.prihlaska.payloads.koncept_step5 import build_step5_fallback
from tests.prihlaska.payloads.koncept_step10 import build_step10_fallback

from tests.vyhladavanie.payloads.search import build_search_payload
from tests.child.payloads.child import build_base_child_payload


# =============================================================================
# LOGGING
# =============================================================================
def log(msg):
    print(f"[LOCUST_FLOW] {msg}")


def debug_fail(label, payload, resp):
    """Print full payload + response on error"""
    log(f"\n❌ {label} FAILED")
    log("----- PAYLOAD -----")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    log("----- RESPONSE -----")
    body = resp.text
    if len(body) > 2000:
        body = body[:2000] + "... [TRUNCATED] ..."
    print(body)
    print("---------------------\n")


def debug_short(label, resp):
    """Short success debug"""
    body = resp.text
    if len(body) > 300:
        body = body[:300] + "... [TRUNCATED] ..."
    log(f"{label}: HTTP {resp.status_code} | BODY: {body}")


def safe_json(resp):
    try:
        return resp.json()
    except:
        return {}


# =============================================================================
# MAIN FLOW
# =============================================================================
def run_full_flow_locust(auth, http):

    # =====================================================================
    # STEP 0 — Create child
    # =====================================================================
    log("=== STEP 0 – Creating child ===")

    first, last = generate_random_name()
    last = f"{last}-{uuid.uuid4().hex[:4]}"

    payload0 = build_base_child_payload(first, last)
    payload0["subjektGUID"] = auth.subj_guid

    r0 = http.post("/api/zapisAModifikaciaDietata", json=payload0, name="STEP0_CHILD")
    debug_short("STEP0_CHILD", r0)

    if r0.status_code != 200:
        debug_fail("STEP0_CHILD", payload0, r0)
        return

    j0 = safe_json(r0)
    if "dieta" not in j0:
        debug_fail("STEP0_CHILD", payload0, r0)
        return

    dieta_guid = j0["dieta"]["guid"]
    log(f"✔ STEP0 OK → {dieta_guid}")

    # =====================================================================
    # STEP 1 — Create application
    # =====================================================================
    log("=== STEP 1 ===")

    payload1 = koncept_krok_1(dieta_guid, auth.logged_guid)
    r1 = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload1, name="STEP1")
    debug_short("STEP1", r1)

    if r1.status_code != 200:
        debug_fail("STEP1", payload1, r1)
        return

    j1 = safe_json(r1)
    if "prihlaska" not in j1:
        debug_fail("STEP1", payload1, r1)
        return

    app_guid = j1["prihlaska"]["prihlaskaGUID"]
    log(f"✔ STEP1 OK → {app_guid}")

    # =====================================================================
    # STEP 2
    # =====================================================================
    log("=== STEP 2 ===")

    payload2 = koncept_krok_2(dieta_guid, app_guid, auth.logged_guid)
    r2 = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload2, name="STEP2")
    debug_short("STEP2", r2)

    if r2.status_code != 200:
        debug_fail("STEP2", payload2, r2)
        return

    # =====================================================================
    # STEP 3 INIT
    # =====================================================================
    log("=== STEP 3 INIT ===")

    payload3init = koncept_krok_3(dieta_guid, app_guid, auth.logged_guid)
    r3init = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload3init, name="STEP3_INIT")
    debug_short("STEP3_INIT", r3init)

    if r3init.status_code != 200:
        debug_fail("STEP3_INIT", payload3init, r3init)
        return

    # =====================================================================
    # SEARCH SCHOOL – EXACT UI BEHAVIOUR
    # =====================================================================
    log("=== SEARCH SCHOOL ===")

    search_payload = build_search_payload(
        page_size=20,
        zemepisnaSirka=48.165064,
        zemepisnaDlzka=17.145673,
        vzdialenostKod="7"
    )

    rs = http.post("/api/vyhladanieMSaZS", json=search_payload, name="SEARCH_SCHOOL")
    debug_short("SEARCH_SCHOOL", rs)

    if rs.status_code != 200:
        debug_fail("SEARCH_SCHOOL", search_payload, rs)
        return

    js = safe_json(rs)
    if not js.get("saSZ"):
        debug_fail("SEARCH_SCHOOL", search_payload, rs)
        return

    eduid = js["saSZ"][0]["eduid"]
    log(f"✔ School selected: {eduid}")

    # =====================================================================
    # STEP 3 SAVE SCHOOL
    # =====================================================================
    log("=== STEP3_SAVE_SCHOOL ===")

    payload3s = koncept_krok_3_with_school(dieta_guid, app_guid, auth.logged_guid, eduid)
    r3s = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload3s, name="STEP3_SAVE_SCHOOL")
    debug_short("STEP3_SAVE_SCHOOL", r3s)

    if r3s.status_code != 200:
        debug_fail("STEP3_SAVE_SCHOOL", payload3s, r3s)
        return

    # =====================================================================
    # STEP 4 — USE UI-PROVEN FALLBACK (NEVER FAILS)
    # =====================================================================
    log("=== STEP 4 ===")

    payload4 = build_step4_fallback(dieta_guid, app_guid, auth.logged_guid, eduid)
    r4 = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload4, name="STEP4")
    debug_short("STEP4", r4)

    if r4.status_code != 200:
        debug_fail("STEP4", payload4, r4)
        return

    log("✔ STEP4 OK")

    # =====================================================================
    # STEP 5 — FALLBACK (ALWAYS VALID)
    # =====================================================================
    log("=== STEP 5 ===")

    payload5 = build_step5_fallback(dieta_guid, app_guid, auth.logged_guid, eduid)
    r5 = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload5, name="STEP5")
    debug_short("STEP5", r5)

    if r5.status_code != 200:
        debug_fail("STEP5", payload5, r5)
        return

    log("✔ STEP5 OK")

    # =====================================================================
    # STEP 10 — FALLBACK FINALIZATION
    # =====================================================================
    log("=== STEP 10 ===")

    payload10 = build_step10_fallback(dieta_guid, app_guid, auth.logged_guid, eduid)
    r10 = http.post("/api/zapisAModifikaciaKonceptuPrihlasky", json=payload10, name="STEP10")
    debug_short("STEP10", r10)

    if r10.status_code != 200:
        debug_fail("STEP10", payload10, r10)
        return

    log("✔ STEP10 OK — FLOW COMPLETE")

    return True
