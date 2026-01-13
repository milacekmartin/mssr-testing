def build_base_child_payload(first, last):
    return {
        "subjektGUID": None,
        "dietaGUID": None,
        "rodneCislo": None,
        "meno": first,
        "priezvisko": last,
        "rodnePriezvisko": None,
        "datumNarodenia": "2020-01-25",
        "miestoNarodenia": "Bratislava",
        "pohlavieKod": "1",
        "narodnostKod": "2",
        "statnaPrislusnost": [{"statnaPrislusnostKod": "211"}],
        "materinskyJazykKod": "SK",
        "inyMaterinskyJazykKod": None,
        "rozpracovane": False,
        "platne": True,

        "tpStatKod": "601",
        "tpObecKod": None,
        "tppsc": None,
        "tpUlicaKod": None,
        "tpUlica": None,
        "tpSupisneCislo": None,
        "tpOrientacneCislo": None,
        "tpAdresaMimoSR": "AAA",
        "adresaTPZhodnaSTPRodica": False,

        "zpStatKod": "601",
        "zpObecKod": None,
        "zppsc": None,
        "zpUlicaKod": None,
        "zpUlica": None,
        "zpSupisneCislo": None,
        "zpOrientacneCislo": None,
        "zpAdresaMimoSR": "AAA",
        "adresaObvyklaZhodnaSTP": True,

        "narodnostZRFO": False,
        "miestoNarodeniaZRFO": False
    }

def build_child_payload(first, last):
    return build_base_child_payload(first, last)
