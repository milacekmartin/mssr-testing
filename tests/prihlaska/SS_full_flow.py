# tests/prihlaska/SS_full_flow.py
# ============================================================
# FULL FLOW SŠ – REFACTORED (new payload architecture)
# ============================================================

import sys
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from login.saml_login import saml_login
from config.runtime import SKOLSKY_ROK, DEFAULT_COUNTRY

from utils.cli import banner, section, bullet
from utils.http import post_strict
from utils.flow_common import create_child
from utils.report import (
    report_child,
    report_school_ss,
    report_finalize,
    report_submit,
)

from tests.prihlaska.payloads.builders.ss import (
    step_1,
    step_2,
    step_3_school,
    step_4_adaptive,
    step_5_legal_guardian,
    step_6_zs_info,
    step_7_grades,
    step_8_competitions,
    step_10_finalize,
    ss_submit_prihlaska,
)

from tests.vyhladavanie.payloads.ss import build_search_payload_ss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-data", action="store_true")
    args = parser.parse_args()

    banner("FULL FLOW SŠ – CAPABILITY DRIVEN")

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------
    login = saml_login()
    print("✔ Login OK")
    print("Subjekt GUID:", login.subj_guid)
    print("User GUID:", login.logged_guid)

    # --------------------------------------------------------
    # CHILD
    # --------------------------------------------------------
    first, last, child = create_child(login, "2010-01-25")
    r = post_strict(login, "/api/zapisAModifikaciaDietata", child,
                    "CHILD – create", args.show_data)
    dieta = r["dieta"]

    report_child(first, last, {**dieta, "datumNarodenia": "2010-01-25"})

    # --------------------------------------------------------
    # STEP 1 – CREATE APPLICATION
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # STEP 2 – COMPLEMENTARY
    # --------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_2(
            dieta["guid"],
            app_guid,
            login.logged_guid
        ),
        "STEP 2 – complementary",
        args.show_data,
    )

    section("📘 STEP 2 – complementary")
    bullet("doplnkové údaje: uložené")

    # --------------------------------------------------------
    # STEP 3 – SCHOOL + FIELD
    # --------------------------------------------------------
    schools = post_strict(
        login,
        "/api/vyhladanieSaSZSS",
        build_search_payload_ss(),
        "SEARCH SŠ",
        args.show_data,
    )["saSZ_SS"]

    school = schools[0]
    odbor = school["saUO"][0]

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_3_school(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            school,
            odbor,
        ),
        "STEP 3 – school + field",
        args.show_data,
    )

    report_school_ss(school, odbor)

    # --------------------------------------------------------
    # STEP 4 – ADAPTIVE (capability-driven)
    # --------------------------------------------------------
    sa_sz_adaptive = {
        "saSZEDUID": school["eduid"],
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
        "odbor": {"odborPrePrihlaskyGUID": odbor["saUOGuid"]},
    }

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_4_adaptive(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
        ),
        "STEP 4 – adaptive",
        args.show_data,
    )

    # --------------------------------------------------------
    # STEP 5 – LEGAL GUARDIAN
    # --------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_5_legal_guardian(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
        ),
        "STEP 5 – legal guardian",
        args.show_data,
    )

    # --------------------------------------------------------
    # STEP 6 – ZŠ INFO
    # --------------------------------------------------------
    prichod_zo_zs = {
        "SaSZEDUID": "910017103",
        "prichodZoZSNaSVK": True,
        "trieda": "9.A",
        "rokSkolskejDochadzky": "9",
        "vyucovaciJazykKod": "SK",
        "rocnikKod": "9",
    }

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_6_zs_info(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
            prichod_zo_zs,
        ),
        "STEP 6 – ZŠ info",
        args.show_data,
    )

    # --------------------------------------------------------
    # STEP 7 – GRADES
    # --------------------------------------------------------
    hodnotenie = [
        {
            "rocnikKod": "9",
            "polrokKod": "2P",
            "klasifikaciaKod": "1",
            "predmetKod": "MAT",
            "evidovanePouzivatelom": True,
        }
    ]

    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_7_grades(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
            hodnotenie,
        ),
        "STEP 7 – grades",
        args.show_data,
    )

    # --------------------------------------------------------
    # STEP 8 – COMPETITIONS
    # --------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_8_competitions(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
            sutaze=[],
        ),
        "STEP 8 – competitions",
        args.show_data,
    )

    # --------------------------------------------------------
    # STEP 10 – FINALIZE
    # --------------------------------------------------------
    post_strict(
        login,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        step_10_finalize(
            dieta["guid"],
            app_guid,
            login.logged_guid,
            sa_sz_adaptive,
        ),
        "STEP 10 – finalize",
        args.show_data,
    )

    # --------------------------------------------------------
    # DETAIL
    # --------------------------------------------------------
    detail = post_strict(
        login,
        "/api/vratenieKonceptuPrihlasky",
        {"prihlaskaGUID": app_guid},
        "DETAIL – before submit",
        args.show_data,
    )

    report_finalize(detail)

    # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------
    submit = post_strict(
        login,
        "/api/zapisPrihlaskyInt",
        ss_submit_prihlaska(
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
        odbor=odbor["saUONazov"],
    )

    print("\n✅ PRIHLÁŠKA ODOSLANÁ\n")


if __name__ == "__main__":
    main()
