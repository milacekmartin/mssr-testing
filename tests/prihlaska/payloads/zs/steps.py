# tests/prihlaska/payloads/zs/steps.py
# ============================================================
# ZŠ PRIHLÁŠKA – PAYLOAD STEPS (SAFE DEFAULTS)
# ============================================================

from tests.prihlaska.payloads.common.base import base_payload
from tests.prihlaska.payloads.common.flags import (
    flags_step2,
    flags_step3,
)

TYP = "ZŠ"


def default_doplnujuce_potreby():
    return {
        "druhVychovyKod": "1",
        "stravovanie": True,
        "druzina": True,
    }


def default_specialne_vvp():
    return {
        "dietaSoSVVP": False,
        "popisSVVP": None,
        "dietaSNadanim": False,
        "popisNadania": None,
        "poznamka": None,
        "pokracovaniePPV": False,
    }


# ------------------------------------------------------------
# STEP 1 – CREATE APPLICATION
# ------------------------------------------------------------
def step_1(dieta_guid, user_guid):
    return base_payload(dieta_guid, None, user_guid, krok=1, typ=TYP)


# ------------------------------------------------------------
# STEP 2 – COMPLEMENTARY
# ------------------------------------------------------------
def step_2(
    dieta_guid,
    prihlaska_guid,
    user_guid,
    doplnujuce_potreby=None,
    specialne_vvp=None,
):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=2, typ=TYP)
    p.update(flags_step2())

    p["doplnujucePotreby"] = (
        doplnujuce_potreby
        if doplnujuce_potreby is not None
        else default_doplnujuce_potreby()
    )

    p["specialneVVP"] = (
        specialne_vvp
        if specialne_vvp is not None
        else default_specialne_vvp()
    )

    return p


# ------------------------------------------------------------
# STEP 3 – INIT SCHOOL
# ------------------------------------------------------------
def step_3_init(dieta_guid, prihlaska_guid, user_guid):
    return base_payload(dieta_guid, prihlaska_guid, user_guid, krok=3, typ=TYP)


# ------------------------------------------------------------
# STEP 3 – SAVE SCHOOL
# ------------------------------------------------------------
def step_3_school(dieta_guid, prihlaska_guid, user_guid, school):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=3, typ=TYP)
    p.update(flags_step3())

    p["saSZ"] = [{
        "saSZEDUID": school["eduid"],
        "poradie": 1,
        "kolo": 1,
        "poradieNaPrihlaske": 1,
    }]
    return p


# ------------------------------------------------------------
# STEP 4 – FINALIZE (fallback)
# ------------------------------------------------------------
def step_4_finalize(dieta_guid, prihlaska_guid, user_guid, sa_sz):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=4, typ=TYP)
    p["saSZ"] = [sa_sz]
    return p


# ------------------------------------------------------------
# STEP 5 – LEGAL GUARDIAN
# ------------------------------------------------------------
def step_5_legal_guardian(dieta_guid, prihlaska_guid, user_guid, sa_sz):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=5, typ=TYP)
    p["saSZ"] = [sa_sz]
    return p


# ------------------------------------------------------------
# STEP 10 – FINALIZE
# ------------------------------------------------------------
def step_10_finalize(dieta_guid, prihlaska_guid, user_guid, sa_sz):
    p = base_payload(dieta_guid, prihlaska_guid, user_guid, krok=10, typ=TYP)
    p["saSZ"] = [sa_sz]
    return p
