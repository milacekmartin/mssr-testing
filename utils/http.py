# utils/http.py

import json
import sys
from config.env import HOST
from config.http import build_headers


def post_strict(login, endpoint, payload, ctx, show=False):
    url = f"{HOST}{endpoint}"

    if show:
        print(f"\n🌍 URL: {url}")
        print(f"➡️ {ctx}")
        print("📤 REQUEST:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    r = login.session.post(
        url,
        json=payload,
        headers=build_headers(login),
    )

    try:
        data = r.json()
    except Exception:
        data = {}

    if show:
        print(f"✅ RESPONSE [{r.status_code}]")
        print(json.dumps(data, indent=2, ensure_ascii=False))

    if r.status_code >= 400:
        print(f"\n❌ {ctx} FAILED [{r.status_code}]")
        sys.exit(1)

    return data


def post_raw(login, endpoint, payload):
    return login.session.post(
        f"{HOST}{endpoint}",
        json=payload,
        headers=build_headers(login),
    )
