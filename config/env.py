# config/env.py

# ============================================
# BASE URL PRE TEST EPRIHLAŠKY
# ============================================

BASE_URL = "https://test-eprihlasky.iedu.sk"

# komplet host
HOST = BASE_URL.rstrip("/")

# ============================================
# TIAM / SAML KONŠTANTY
# ============================================

# Base TIAM Identity Provider
TIAM_BASE = "https://tiamidsk.iedu.sk"

# login stránka
LOGIN_OSOBA_URL = f"{HOST}/loginosoba?returnurl=%2F"

# Assertion Consumer Service
ACS_URL = f"{HOST}/assertionconsumerservice"

# ============================================
# Cookies, ktoré chceme prenášať
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
