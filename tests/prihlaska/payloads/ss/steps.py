# tests/prihlaska/payloads/ss/steps.py
# ============================================================
# SŠ PRIHLÁŠKA – PAYLOAD STEPS 1–10
# ============================================================

from tests.prihlaska.payloads.common.base import base_payload
from tests.prihlaska.payloads.common.flags import (
    flags_step2,
    flags_step3,
    flags_step5,
    flags_step6,
    flags_step7,
    flags_step8,
)

TYP = "SŠ"


# ------------------------------------------------------------
# STEP 1 – CREATE APPLICATION
# ------------------------------------------------------------
def step_1(dieta_guid, user_guid):
    return base_payload(
        dieta_guid=dieta_guid,
        prihlaska_guid=None,
        user_guid=user_guid,
        krok=1,
        typ=TYP,
    )


# ------------------------------------------------------------
# STEP 2 – COMPLEMENTARY (SS specific)
# ------------------------------------------------------------
def default_doplnujuce_ss():
    return {
        "zdravotnePostihnutie": {
            "mentalne": False,
            "mentalneSInym": False
        },
        "zmenenaPracSchopnost": False,
        "specialnePotreby": False,
        "sPZdravotneZnevyhodnenie": False,
        "sPSocialneZnevyhodnenie": False,
        "sPNadanie": False,
        "poznamka": None,
    }


def step_2(dieta_guid, prihlaska_guid, user_guid, doplnujuce_ss=None):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=2, typ=TYP)
    p.update(flags_step2())

    p["doplnujuceInformacieSS"] = (
        doplnujuce_ss if doplnujuce_ss is not None else default_doplnujuce_ss()
    )

    return p


# ------------------------------------------------------------
# STEP 3 – SCHOOL + FIELD
# ------------------------------------------------------------
def step_3_school(dieta_guid, prihlaska_guid, user_guid, school, odbor):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=3, typ=TYP)
    p.update(flags_step3())

    p["saSZ"] = [{
        "saSZEDUID": school["eduid"],
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
        "odbor": {
            "odborPrePrihlaskyGUID": odbor["saUOGuid"]
        }
    }]
    return p


# ------------------------------------------------------------
# STEP 4 – ADAPTIVE (termín / voľby)
# ------------------------------------------------------------
def step_4_adaptive(dieta_guid, prihlaska_guid, user_guid, sa_sz_adaptive):
    """
    sa_sz_adaptive = dict built in flow (capability driven)
    """
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=4, typ=TYP)
    p["saSZ"] = [sa_sz_adaptive]
    return p


# ------------------------------------------------------------
# STEP 5 – LEGAL GUARDIAN
# ------------------------------------------------------------
def step_5_legal_guardian(dieta_guid, prihlaska_guid, user_guid, sa_sz):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=5, typ=TYP)
    p.update(flags_step5())
    p["saSZ"] = [sa_sz]
    return p


# ------------------------------------------------------------
# STEP 6 – ZŠ INFO
# ------------------------------------------------------------
def step_6_zs_info(dieta_guid, prihlaska_guid, user_guid, sa_sz, prichod_zo_zs):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=6, typ=TYP)
    p.update(flags_step6())
    p["saSZ"] = [sa_sz]
    p["prichodUchadzaca"] = prichod_zo_zs
    return p


# ------------------------------------------------------------
# STEP 7 – GRADES
# ------------------------------------------------------------
def step_7_grades(dieta_guid, prihlaska_guid, user_guid, sa_sz, hodnotenie):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=7, typ=TYP)
    p.update(flags_step7())
    p["saSZ"] = [sa_sz]
    p["hodnotenie"] = hodnotenie
    return p


# ------------------------------------------------------------
# STEP 8 – COMPETITIONS
# ------------------------------------------------------------
def step_8_competitions(dieta_guid, prihlaska_guid, user_guid, sa_sz, sutaze):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=8, typ=TYP)
    p.update(flags_step8())
    p["saSZ"] = [sa_sz]
    p["olympiadySutaze"] = sutaze
    return p


# ------------------------------------------------------------
# STEP 10 – FINALIZE
# ------------------------------------------------------------
def step_10_finalize(dieta_guid, prihlaska_guid, user_guid, sa_sz):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=10, typ=TYP)
    p["saSZ"] = [sa_sz]
    return p
