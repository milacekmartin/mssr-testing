# tests/prihlaska/payloads/ss/submit.py
# FINAL SUBMIT – SŠ PRIHLÁŠKA

from tests.prihlaska.payloads.common.submit_base import submit_base

def ss_submit_prihlaska(
    prihlaska_guid,
    dieta_meno,
    dieta_priezvisko,
    identifikator_prihlasky,
    sa_sz_detail,
    adresa_zz1,
):
    payload = submit_base(
        prihlaska_guid,
        sa_sz_detail,
        adresa_zz1,
        include_odbor=True,
    )

    payload.update({
        "dietaMeno": dieta_meno,
        "dietaPriezvisko": dieta_priezvisko,
        "identifikatorPrihlasky": identifikator_prihlasky,
        "typPrihlaskyKod": "SŠ",
    })

    return payload
