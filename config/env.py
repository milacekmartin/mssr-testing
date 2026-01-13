# config/env.py

# ============================================
# BASE URL
# ============================================

BASE_URL = "https://test-eprihlasky.iedu.sk"
HOST = BASE_URL.rstrip("/")

# ============================================
# TIAM / SAML CONSTS
# ============================================

TIAM_BASE = "https://tiamidsk.iedu.sk"
LOGIN_OSOBA_URL = f"{HOST}/loginosoba?returnurl=%2F"

ACS_URL = f"{HOST}/assertionconsumerservice"

# ============================================
# Cookies
# ============================================

IMPORTANT_COOKIES = [
    "IamTokenDescriptor",
    "_DS",
    "_DSA",
    "_DC",
    ".AspNetCore.Antiforgery.UaYXyBoyr8Q",
    ".AspNetCore.Antiforgery.fAr6xnvBhu0",
    "IamWeb",
    "culture",
    "Balanced_and_Offloaded",
    "cookies-warning",
    "last_non_error_path",
]
