# tests/prihlaska/payloads/common/submit_base.py

def build_sa_sz_entry(sa_sz_detail, *, include_odbor=False):
    """
    Build single saSZ entry for submit payload.
    Works for both ZŠ and SŠ.
    """
    entry = {
        "saSZEDUID": sa_sz_detail["saSZEDUID"],
        "poradie": sa_sz_detail["poradie"],
        "kolo": sa_sz_detail["kolo"],
        "poradieNaPrihlaske": sa_sz_detail["poradieNaPrihlaske"],

        "zaujemPripravnyRocnik": sa_sz_detail.get("zaujemPripravnyRocnik"),
        "zaujemUvodnyRocnikNKS": sa_sz_detail.get("zaujemUvodnyRocnikNKS"),
        "zaujemUvodnyRocnikVIN": sa_sz_detail.get("zaujemUvodnyRocnikVIN"),
        "zaujemDualneVzdelavanie": sa_sz_detail.get("zaujemDualneVzdelavanie"),
        "zaujemInternat": sa_sz_detail.get("zaujemInternat"),
        "terminPrijimacejSkuskyKod": sa_sz_detail.get("terminPrijimacejSkuskyKod"),
        "pozadovanyJazykKod": sa_sz_detail.get("pozadovanyJazykKod"),
        "mentalnePostihnutie": sa_sz_detail.get("mentalnePostihnutie", False),

        "nazov": sa_sz_detail["nazov"],
        "nazovOficialny": sa_sz_detail["nazovOficialny"],
    }

    if include_odbor:
        entry["odbor"] = sa_sz_detail["odbor"]

    return entry


def submit_base(
    prihlaska_guid,
    sa_sz_detail,
    adresa_zz1,
    *,
    include_odbor=False,
):
    """
    Base submit payload for both ZŠ and SŠ.
    """
    return {
        "vstupZapisPrihlasky": {
            "prihlaskaGUID": prihlaska_guid,
            "adresaZZ1": adresa_zz1,
            "saSZ": [
                build_sa_sz_entry(
                    sa_sz_detail,
                    include_odbor=include_odbor,
                )
            ],
            "doruceniePostou": False,
        }
    }
