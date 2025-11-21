import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.common import send_post, safe_extract
from config.random_names import generate_random_name
from payloads.dieta import create_dieta_payload


def main():
    context = "CREATE+DELETE"

    first, last = generate_random_name()
    print(f"\n🧒 [CREATE+DELETE] Generujem dieťa: {first} {last}")

    # 1. vytvorenie dieťaťa
    resp = send_post(
        context,
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last)
    )

    data = resp.json()
    dieta_guid = safe_extract(resp, data, ["dieta", "guid"], "GUID dieťaťa")

    # 2. mazanie dieťaťa
    send_post(
        context,
        "/api/vymazDietata",
        {"guid": dieta_guid}
    )

    print("\n✔️ TEST PASSED – dieťa vytvorené aj vymazané.\n")


if __name__ == "__main__":
    main()
