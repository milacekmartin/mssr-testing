# tests/locust/common/utils.py

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}
