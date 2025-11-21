# payloads/oblubene.py
# =====================
#
# Payloady pre obľúbené školy (ZŠ).

from config.settings import PRIHLASENA_OSOBA_GUID


# ---------------------------------------------------------
#  Načítanie obľúbených ZŠ
# ---------------------------------------------------------
def payload_oblubene_zs():
    return {
        "guid": PRIHLASENA_OSOBA_GUID,
        "typSaSZ": {
            "skratenaDoplnkovaInformacia": "ZŠ"
        }
    }


# ---------------------------------------------------------
#  Pridanie obľúbenej ZŠ školy (EDUID = 910000787)
# ---------------------------------------------------------
def payload_add_favorite_school():
    return {
        "guid": PRIHLASENA_OSOBA_GUID,
        "oblubenaSaSZ": [
            {"eduid": 910000787}
        ]
    }
