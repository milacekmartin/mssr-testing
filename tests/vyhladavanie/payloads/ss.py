# tests/vyhladavanie/payloads/ss.py

from config.runtime import SKOLSKY_ROK

def build_search_payload_ss(**kwargs):
    payload = {
        "skolskyRok": kwargs.get("skolskyRok", SKOLSKY_ROK),
        "cisloStranky": kwargs.get("cisloStranky", 1),
        "pocetZaznamovNaStranku": kwargs.get("pocetZaznamovNaStranku", 20),
    }

    if "kraj" in kwargs:
        payload["kraj"] = kwargs["kraj"]

    if "jazyk" in kwargs:
        payload["jazyk"] = kwargs["jazyk"]

    if "talentovy" in kwargs:
        payload["talentovy"] = kwargs["talentovy"]

    if "dualneVzdelavanie" in kwargs:
        payload["dualneVzdelavanie"] = kwargs["dualneVzdelavanie"]

    if "prijimaciaSkuska" in kwargs:
        payload["prijimaciaSkuska"] = kwargs["prijimaciaSkuska"]

    if "dlzkaStudiaKod" in kwargs:
        payload["dlzkaStudiaKod"] = kwargs["dlzkaStudiaKod"]

    return payload
