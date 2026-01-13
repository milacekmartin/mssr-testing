from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

from tests.prihlaska.payloads.ss.steps import (
    step_1,
    step_2,
    step_3_school,
    step_4_adaptive,
    step_5_legal_guardian,
    step_6_zs_info,
    step_7_grades,
    step_8_competitions,
    step_10_finalize,
)
from tests.prihlaska.payloads.ss.submit import ss_submit_prihlaska
from tests.vyhladavanie.payloads.ss import build_search_payload_ss

from tests.locust.common.client import post
from tests.locust.common.logging import flow_start, flow_end
from tests.locust.common.failures import fail_request
from tests.locust.common.guards import expect_json_dict


def run_ss_flow(user):
    first, last = generate_random_name()
    flow_start("SŠ PRIHLÁŠKA", f"{first} {last}")

    # ============================================================
    # STEP 0 – CREATE CHILD (LOAD SAFE)
    # ============================================================
    child = build_base_child_payload(first, last)
    child["subjektGUID"] = user.login.subj_guid

    r = post(user, "/api/zapisAModifikaciaDietata", child, "SS / Create child")
    data = expect_json_dict(user, r, "SS / Create child", "SŠ PRIHLÁŠKA – FAILED")

    if not isinstance(data, dict) or "dieta" not in data:
        fail_request(user, "POST", "SS / Create child – missing dieta", r, data)
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    dieta = data["dieta"]
    dieta_guid = dieta.get("guid")
    if not dieta_guid:
        fail_request(user, "POST", "SS / Create child – missing guid", r, dieta)
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    # ============================================================
    # STEP 1 – CREATE APPLICATION
    # ============================================================
    r = post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_1(dieta_guid, user.login.logged_guid),
        "SS / Step 1 – Create application",
    )
    data = expect_json_dict(user, r, "SS / Step 1", "SŠ PRIHLÁŠKA – FAILED")
    if not data or "prihlaska" not in data:
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    app_guid = data["prihlaska"].get("prihlaskaGUID")
    if not app_guid:
        fail_request(user, "POST", "SS / Step 1 – missing prihlaskaGUID", r, data)
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    # ============================================================
    # STEP 2 – COMPLEMENTARY
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_2(dieta_guid, app_guid, user.login.logged_guid),
        "SS / Step 2 – Complementary",
    )

    # ============================================================
    # SEARCH SCHOOL + FIELD
    # ============================================================
    r = post(
        user,
        "/api/vyhladanieSaSZSS",
        build_search_payload_ss(),
        "SS / School search",
    )
    data = expect_json_dict(user, r, "SS / School search", "SŠ PRIHLÁŠKA – FAILED")
    if not data or not isinstance(data.get("saSZ_SS"), list) or not data["saSZ_SS"]:
        fail_request(user, "POST", "SS / School search – empty", r, data)
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    school = data["saSZ_SS"][0]
    odbory = school.get("saUO")
    if not school.get("eduid") or not odbory:
        fail_request(user, "POST", "SS / Invalid school object", r, school)
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    odbor = odbory[0]

    # ============================================================
    # STEP 3 – SCHOOL + FIELD
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_3_school(dieta_guid, app_guid, user.login.logged_guid, school, odbor),
        "SS / Step 3 – School + field",
    )

    sa_sz = {
        "saSZEDUID": school["eduid"],
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
        "odbor": {"odborPrePrihlaskyGUID": odbor["saUOGuid"]},
    }

    # ============================================================
    # STEP 4 – ADAPTIVE
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_4_adaptive(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
        "SS / Step 4 – Adaptive",
    )

    # ============================================================
    # STEP 5 – LEGAL GUARDIAN
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_5_legal_guardian(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
        "SS / Step 5 – Legal guardian",
    )

    # ============================================================
    # STEP 6 – ZŠ INFO
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_6_zs_info(
            dieta_guid,
            app_guid,
            user.login.logged_guid,
            sa_sz,
            {
                "SaSZEDUID": "910017103",
                "prichodZoZSNaSVK": True,
                "trieda": "9.A",
                "rokSkolskejDochadzky": "9",
                "vyucovaciJazykKod": "SK",
                "rocnikKod": "9",
            },
        ),
        "SS / Step 6 – ZŠ info",
    )

    # ============================================================
    # STEP 7 – GRADES
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_7_grades(
            dieta_guid,
            app_guid,
            user.login.logged_guid,
            sa_sz,
            [{
                "rocnikKod": "9",
                "polrokKod": "2P",
                "klasifikaciaKod": "1",
                "predmetKod": "MAT",
                "evidovanePouzivatelom": True,
            }],
        ),
        "SS / Step 7 – Grades",
    )

    # ============================================================
    # STEP 8 – COMPETITIONS
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_8_competitions(dieta_guid, app_guid, user.login.logged_guid, sa_sz, []),
        "SS / Step 8 – Competitions",
    )

    # ============================================================
    # STEP 10 – FINALIZE
    # ============================================================
    post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_10_finalize(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
        "SS / Step 10 – Finalize",
    )

    # ============================================================
    # DETAIL + SUBMIT
    # ============================================================
    r = post(
        user,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": app_guid},
        "SS / Fetch detail",
    )
    data = expect_json_dict(user, r, "SS / Fetch detail", "SŠ PRIHLÁŠKA – FAILED")
    if not data or "prihlaska" not in data:
        flow_end("SŠ PRIHLÁŠKA – FAILED")
        return

    post(
        user,
        "/api/zapisPrihlaskyInt",
        ss_submit_prihlaska(
            app_guid,
            first,
            last,
            data["prihlaska"]["prihlaskaIdentifikator"],
            data["prihlaska"]["saSZ"][0],
            {"statKod": "601", "adresaMimoSR": "AAA"},
        ),
        "SS / Submit application",
    )

    flow_end("SŠ PRIHLÁŠKA")
