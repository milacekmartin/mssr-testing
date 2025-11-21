import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.common import send_post, safe_extract
from config.random_names import generate_random_name
from payloads.dieta import create_dieta_payload
from payloads.prihlaska import koncept_krok_1


def main():
    context = "CREATE-APP+DELETE"

    first, last = generate_random_name()
    print(f"\n📄 [CREATE-APP+DELETE] Generujem dieťa: {first} {last}")

    # 1. Vytvorenie dieťaťa
    resp_d = send_post(
        context,
        "/api/zapisAModifikaciaDietata",
        create_dieta_payload(first, last)
    )

    dieta_guid = safe_extract(resp_d, resp_d.json(), ["dieta", "guid"], "GUID dieťaťa")

    # 2. Vytvorenie prihlášky
    resp_k1 = send_post(
        context,
        "/api/zapisAModifikaciaKonceptuPrihlasky",
        koncept_krok_1(dieta_guid)
    )

    prihlaska_guid = safe_extract(
        resp_k1, resp_k1.json(), ["prihlaska", "prihlaskaGUID"], "GUID prihlášky"
    )

    # 3. Mazanie prihlášky
    send_post(
        context,
        "/api/vymazPrihlasky",
        {"PrihlaskaGUID": prihlaska_guid}
    )

    # 4. Mazanie dieťaťa
    send_post(
        context,
        "/api/vymazDietata",
        {"guid": dieta_guid}
    )

    print("\n✔️ TEST PASSED – dieťa + prihláška vytvorené a vymazané.\n")


if __name__ == "__main__":
    main()
