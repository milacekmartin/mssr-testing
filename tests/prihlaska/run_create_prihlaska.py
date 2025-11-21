# locust/tests/prihlaska/run_create_prihlaska.py

import sys, os, json

# PATH FIX
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from tests.common import send_post_raw
from tests.prihlaska.payloads.prihlaska import build_base_prihlaska_payload
from config.random_names import generate_random_name


# =============================================
# Helper – extrahuje GUID prihlášky
# =============================================
def extract_prihlaska_guid(resp_json):
    """
    Hľadáme:
      - prihlaska.guid
      - guidPrihlasky
    """
    if isinstance(resp_json, dict):
        # 1) prihlaska.guid
        if "prihlaska" in resp_json and isinstance(resp_json["prihlaska"], dict):
            if "guid" in resp_json["prihlaska"]:
                return resp_json["prihlaska"]["guid"]

        # 2) guidPrihlasky
        if "guidPrihlasky" in resp_json:
            return resp_json["guidPrihlasky"]

    return None


# =============================================
# MAIN TEST
# =============================================
def main():

    print("\n============================================================")
    print("CREATE-PRIHLASKA")
    print("============================================================\n")

    first, last = generate_random_name()
    print(f"➡️ Vytváram prihlášku pre: {first} {last}")

    payload = build_base_prihlaska_payload()

    # PREZENTÁCIA PAYLOADU
    print("\n📦 PAYLOAD:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    resp = send_post_raw(
        "CREATE-PRIHLASKA",
        "/api/prihlaska/zapis",
        payload
    )

    print(f"[CREATE-PRIHLASKA] → {resp.status_code}")

    # response text
    try:
        resp_json = resp.json()
    except:
        resp_json = None

    print("\n📥 RESPONSE:")
    print(resp.text)

    # VALIDÁCIA
    guid = extract_prihlaska_guid(resp_json) if resp_json else None

    if resp.status_code != 200:
        print("\n❌ CREATE FAILED — status != 200")
        return

    if not guid:
        print("\n❌ CREATE FAILED — GUID prihlášky nenájdený")
        return

    print(f"\n✔️ CREATE PASSED — získané GUID prihlášky: {guid}\n")


if __name__ == "__main__":
    main()
