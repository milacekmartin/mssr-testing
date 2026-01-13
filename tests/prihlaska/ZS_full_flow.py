# tests/prihlaska/ZS_full_flow.py
# ======================================================================
# FULL FLOW ZŠ – CAPABILITY DRIVEN (NEW PAYLOAD ARCHITECTURE)
# ======================================================================

import sys
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.runtime import DEFAULT_COUNTRY, SKOLSKY_ROK

from utils.cli import banner, section, bullet
from utils.http import post_strict
from utils.flow_common import create_child
from utils.report import (
    report_child,
    report_school_zs,
    report_finalize,
    report_submit,
)

from tests.prihlaska.payloads.builders.zs import (
    step_1,
    step_2,
    step_3_init,
    step_3_school,
    step_4_finalize,
    step_5_legal_guardian,
    step_10_finalize,
    zs_submit_prihlaska,
)

from tests.vyhladavanie.payloads.zs import build_search_payload_zs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-data", action="store_true")
    args = parser.parse_args()

    banner("FULL FLOW ZŠ – CAPABILITY DRIVEN")

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    login = saml_login()
    print("✔ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("User GUID:", login.logged_guid)

    # ------------------------------------------------------------------
    # CHILD
    # ------------------------------------------------------------------
    first, last, child = create_child(login, "2015-03-12")

    r = post_strict(
        login,
        "/api/zapisAModifikaciaDietata",
        child,
        "CHILD – create",
        args.show_data,
    )
    dieta = r["dieta"]

    report_child(first, last, {**dieta, "datumNarodenia": "2015-03-12"})

    # ------------------------------------------------------------------
    # STEP 1 – CREATE APPLICATION
    # ------------------------------------------------------------------
    r = post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_1(dieta["guid"], login.logged_guid),
        "STEP 1 – create application",
        args.show_data,
    )
    app_guid = r["prihlaska"]["prihlaskaGUID"]

    section("📘 STEP 1 – create application")
    bullet(f"prihlaska GUID: {app_guid}")
    bullet(f"školský rok: {SKOLSKY_ROK}")

    # ------------------------------------------------------------------
    # STEP 2 – COMPLEMENTARY (with defaults)
    # ------------------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_2(
            dieta["guid"],
            app_guid,
            login.logged_guid,
        ),
        "STEP 2 – complementary",
        args.show_data,
    )

    section("📘 STEP 2 – complementary")
    bullet("doplnkové údaje: uložené")

    # ------------------------------------------------------------------
    # STEP 3 – INIT SCHOOL
    # ------------------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_3_init(dieta["guid"], app_guid, login.logged_guid),
        "STEP 3 – init school",
        args.show_data,
    )

    schools = post_strict(
        login,
        "/api/vyhladanieMSaZS",
        build_search_payload_zs(page_size=20),
        "SEARCH ZŠ",
        args.show_data,
    )["saSZ"]

    school = schools[0]

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_3_school(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            school,
        ),
        "STEP 3 – save school",
        args.show_data,
    )

    report_school_zs(school)

    # ------------------------------------------------------------------
    # STEP 4 – FINALIZE (fallback style)
    # ------------------------------------------------------------------
    sa_sz = {
        "saSZEDUID": school["eduid"],
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
    }

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_4_finalize(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz,
        ),
        "STEP 4 – finalize",
        args.show_data,
    )

    # ------------------------------------------------------------------
    # STEP 5 – LEGAL GUARDIAN
    # ------------------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_5_legal_guardian(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz,
        ),
        "STEP 5 – legal guardian",
        args.show_data,
    )

    # ------------------------------------------------------------------
    # STEP 10 – FINALIZE
    # ------------------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_10_finalize(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz,
        ),
        "STEP 10 – finalize",
        args.show_data,
    )

    # ------------------------------------------------------------------
    # DETAIL – BEFORE SUBMIT
    # ------------------------------------------------------------------
    detail = post_strict(
        login,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": app_guid},
        "DETAIL – before submit",
        args.show_data,
    )

    report_finalize(detail)

    # ------------------------------------------------------------------
    # SUBMIT
    # ------------------------------------------------------------------
    submit = post_strict(
        login,
        "/api/zapisPrihlaskyInt",
        zs_submit_prihlaska(
            app_guid,
            first,
            last,
            detail["prihlaska"]["prihlaskaIdentifikator"],
            detail["prihlaska"]["saSZ"][0],
            DEFAULT_COUNTRY,
        ),
        "SUBMIT PRIHLASKY",
        args.show_data,
    )

    report_submit(
        detail["prihlaska"]["prihlaskaIdentifikator"],
        app_guid,
        school["nazov"],
        submit,
    )

    print("\n✅ PRIHLÁŠKA ODOSLANÁ\n")


if __name__ == "__main__":
    main()
