# tests/locust/common/client.py

import json
from config.env import HOST


def post(user, endpoint, payload, label, allow_400=False):
    """
    Central POST wrapper:
    - unified headers
    - Locust UI naming
    - console output
    - clear error reporting for Locust UI
    """

    locust_name = f"{label} (POST {endpoint})"

    print(f"➡️ {label}")
    print(f"   URL: {endpoint}")

    with user.client.post(
        endpoint,
        json=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": HOST,
            "Referer": f"{HOST}/Moj-profil2",
            "RequestVerificationToken": user.login.csrf,
            "x-token-descriptor": user.login.token_desc,
            "Cookie": user.login.cookie_bundle,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0",
        },
        name=locust_name,
        catch_response=True,
    ) as resp:

        # --------------------------------------------------------------
        # SUCCESS
        # --------------------------------------------------------------
        if resp.status_code == 200:
            print("   ✅ 200 OK")
            resp.success()
            return resp

        # --------------------------------------------------------------
        # EXPECTED 400 (NEGATIVE / SKIPPED FLOW)
        # --------------------------------------------------------------
        if resp.status_code == 400 and allow_400:
            print("   ↪ 🟡 SKIPPED (expected 400)")

            try:
                data = resp.json()
                print("   📥 RESPONSE:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception:
                print("   📥 RESPONSE (raw):")
                print(resp.text)

            resp.success()
            return resp

        # --------------------------------------------------------------
        # UNEXPECTED ERROR (VISIBLE IN LOCUST UI)
        # --------------------------------------------------------------
        print(f"   ❌ ERROR [{resp.status_code}]")

        body = ""
        try:
            body = resp.text.strip()
            if body:
                print("   📥 RESPONSE:")
                print(body)
        except Exception:
            body = "no response body"

        resp.failure(
            f"HTTP {resp.status_code} – {body or 'no response body'}"
        )

        return resp
