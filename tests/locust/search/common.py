from config.env import HOST

LAT = 48.586405
LON = 19.14219
SK_ROK = "2026/2027"


def reverse_payload():
    return f"/api/reverse?point.lon={LON}&point.lat={LAT}"


def filter_payload(ms=False, zs=False, ss=False):
    return {
        "skolskyRokKod": SK_ROK,
        "ms": ms,
        "zs": zs,
        "ss": ss
    }
