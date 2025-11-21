import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests

from config.settings import HOST, CSRF, COOKIE_BUNDLE


# EXTENDED HEADERS — tieto endpoint potrebuje
HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": HOST,
    "Referer": f"{HOST}/",
    "RequestVerificationToken": CSRF,
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": COOKIE_BUNDLE
}


def main():
    context = "SESSION-HEALTH"

    print("\n🔍 Kontrola platnosti session/tokenov…")
    print(f"[{context}] GET /api/vratKonfiguracneUdajePrihlasok")

    url = f"{HOST}/api/vratKonfiguracneUdajePrihlasok"

    resp = requests.get(url, headers=HEADERS)

    print(f"[{context}] → Status: {resp.status_code}\n")

    # SUCCESS
    if resp.status_code == 200:
        print("✔️ SESSION OK — tokeny sú platné.")
        try:
            parsed = resp.json()
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print(resp.text)
        print()
        sys.exit(0)

    # FAILURE
    print("❌ SESSION INVALID — tokeny alebo cookies sú neplatné.\n")
    print("Response body:")
    print(resp.text)
    print("\nNajčastejšie dôvody:")
    print("  • expirovaný XSRF token")
    print("  • expirované _DS, _DSA alebo antiforgery cookies")
    print("  • nesprávne RequestVerificationToken vs antiforgery cookie")
    print("  • session nevznikla po SAML logine\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
