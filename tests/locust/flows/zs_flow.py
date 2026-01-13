from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

from tests.prihlaska.payloads.zs.steps import (
    step_1,
    step_2,
    step_3_init,
    step_3_school,
    step_4_finalize,
    step_5_legal_guardian,
    step_10_finalize,
)
from tests.prihlaska.payloads.zs.submit import zs_submit_prihlaska
from tests.vyhladavanie.payloads.zs import build_search_payload_zs

from tests.locust.common.client import post
from tests.locust.common.logging import flow_start, flow_end
from tests.locust.common.failures import fail_request
from tests.locust.common.guards import expect_json_dict


def run_zs_flow(user):
    first, last = generate_random_name()
    flow_start("ZŠ PRIHLÁŠKA", f"{first} {last}")

    # ============================================================
    # CREATE CHILD (LOAD SAFE)
    # ============================================================
    child = build_base_child_payload(first, last)
    child["subjektGUID"] = user.login.subj_guid

    r = post(user, "/api/zapisAModifikaciaDietata", child, "ZS / Create child")
    data = expect_json_dict(user, r, "ZS / Create child", "ZŠ PRIHLÁŠKA – FAILED")

    if not isinstance(data, dict) or "dieta" not in data:
        fail_request(user, "POST", "ZS / Create child – missing dieta", r, data)
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    dieta_guid = data["dieta"].get("guid")
    if not dieta_guid:
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    # ============================================================
    # STEP 1
    # ============================================================
    r = post(
        user,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_1(dieta_guid, user.login.logged_guid),
        "ZS / Step 1",
    )
    data = expect_json_dict(user, r, "ZS / Step 1", "ZŠ PRIHLÁŠKA – FAILED")
    if not data or "prihlaska" not in data:
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    app_guid = data["prihlaska"].get("prihlaskaGUID")
    if not app_guid:
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    # ============================================================
    # STEP 2
    # ============================================================
    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_2(dieta_guid, app_guid, user.login.logged_guid),
         "ZS / Step 2")

    # ============================================================
    # STEP 3 INIT
    # ============================================================
    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_3_init(dieta_guid, app_guid, user.login.logged_guid),
         "ZS / Step 3 – Init")

    # ============================================================
    # SCHOOL SEARCH
    # ============================================================
    r = post(user, "/api/vyhladanieMSaZS",
             build_search_payload_zs(page_size=20),
             "ZS / School search")
    data = expect_json_dict(user, r, "ZS / School search", "ZŠ PRIHLÁŠKA – FAILED")
    if not data or not data.get("saSZ"):
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    school = data["saSZ"][0]
    eduid = school.get("eduid")
    if not eduid:
        flow_end("ZŠ PRIHLÁŠKA – FAILED")
        return

    # ============================================================
    # STEP 3 SAVE SCHOOL
    # ============================================================
    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_3_school(dieta_guid, app_guid, user.login.logged_guid, school),
         "ZS / Step 3 – Save school")

    sa_sz = {
        "saSZEDUID": eduid,
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
    }

    # ============================================================
    # STEP 4 / 5 / 10
    # ============================================================
    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_4_finalize(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
         "ZS / Step 4")

    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_5_legal_guardian(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
         "ZS / Step 5")

    post(user, "/api/zapisAModifikaciaKonceptuPrihlasky",
         step_10_finalize(dieta_guid, app_guid, user.login.logged_guid, sa_sz),
         "ZS / Step 10")

    # ============================================================
    # SUBMIT
    # ============================================================
    r = post(user, "/api/vratenieKonceptuPrihlasky",
             {"prihlaskaGUID": app_guid},
             "ZS / Fetch detail")
    data = expect_json_dict(user, r, "ZS / Fetch detail", "ZŠ PRIHLÁŠKA – FAILED")
    if not data:
        return

    post(
        user,
        "/api/zapisPrihlaskyInt",
        zs_submit_prihlaska(
            app_guid,
            first,
            last,
            data["prihlaska"]["prihlaskaIdentifikator"],
            data["prihlaska"]["saSZ"][0],
            {"statKod": "601", "adresaMimoSR": "AAA"},
        ),
        "ZS / Submit application",
    )

    flow_end("ZŠ PRIHLÁŠKA")
