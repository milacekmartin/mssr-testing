# config/credentials.py
import os

def _get(name: str, default=None):
    val = os.getenv(name)
    if val:
        return val
    return default

# ==========================================================
# LOGIN CREDENTIALS RESOLUTION
# ==========================================================

USERNAME = _get("LOGIN_USERNAME")
PASSWORD = _get("LOGIN_PASSWORD")

# ----------------------------------------------------------
# LOCAL FALLBACK
# ----------------------------------------------------------
if not USERNAME or not PASSWORD:
    try:
        from config.local_credentials import USERNAME, PASSWORD
    except ImportError:
        raise RuntimeError(
            "Missing credentials. "
            "Set LOGIN_USERNAME / LOGIN_PASSWORD env vars "
            "or create config/local_credentials.py"
        )
