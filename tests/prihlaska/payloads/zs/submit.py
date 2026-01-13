# tests/prihlaska/payloads/zs/submit.py
# FINAL SUBMIT – ZŠ PRIHLÁŠKA

from tests.prihlaska.payloads.common.submit_base import submit_base


def zs_submit_prihlaska(
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
        include_odbor=False,
    )

    payload.update({
        "dietaMeno": dieta_meno,
        "dietaPriezvisko": dieta_priezvisko,
        "identifikatorPrihlasky": identifikator_prihlasky,
        "typPrihlaskyKod": "ZŠ",
    })

    return payload
