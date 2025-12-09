# config/settings.py
# ===================

# -----------------------------
# Základné URL a časy čakania
# -----------------------------
HOST = "https://test-eprihlasky.iedu.sk"

WAIT_TIME_MIN = 1
WAIT_TIME_MAX = 3

# -----------------------------
# Tokeny, cookies, autentifikácia
# -----------------------------
CSRF = "CfDJ8JJLSCh_emVEns9vaN-xR0AXTa77jdB9izRDpAm6huE_VKCt-AQqlHx7tcHVVuvaSY6t3tgTM73baKGUCTjeP95xbkby25Si5MjCr_qsyW32turVOv55D0KZOAKSNyZH4WUxSHDRpjaXCrysl5B1mUHah2xetolMQg2Xdlm48DuZZNY7sr_XpZyx3fNlN4zI9Q"
IAM_TOKEN = "ffcfe09e-b128-404e-a50e-0afb8bbcbb2a:d05cf2f2eb17a7620e80a867c9125e276d83f4dca36000d19d9855cbd391f079"
COOKIE_BUNDLE = "_DC=c%3Dsk-SK%7Cuic%3Dsk-SK; Balanced_and_Offloaded=378929418.20480.0000; cookies-warning=true; _DS=CfDJ8JJLSCh%2FemVEns9vaN%2BxR0DwjdvcXerLh%2FICpkCdsYWbJPIk%2Bg7m8BROFYnx14m5vq%2Fm1OUJ4f1eCG9R43zbMfX0m8K5DJMiW7U5m4CuZ3Y5gCt04wKjZ1SFB%2Bbyz5NS59i0u755blsIZjHo5aC9YU9GljtlELfivUju%2FBCbDRKc; .AspNetCore.Antiforgery.UaYXyBoyr8Q=CfDJ8JJLSCh_emVEns9vaN-xR0AtTNnI9yqMgaiGS4jqMYRkcJN29axuxMnz9-NLTrN0d1tNIWR85uFuN_m7b-9IMQyuYKxPRskbsmtGdtrTKddy6zh_8kB3C_Z2uRJaxCCn7rGLTRx5E8XTKFU7Pnq6mKw; _DSA=CfDJ8JJLSCh_emVEns9vaN-xR0CTQPxlHkItD9JnVnuygru_J40g7MIu7--c5W8DsAhN52Tqa3r2HRs5y85TV6h8z9uBtz6bah10IPmxWYlfUYvBKywvBVS0UZh-0HRwe2Bom8Gri2Ea5_rm6XdsuFXDceX-BvgOMLdUBkQOr7BCnfCBKmpQkRGiODeKyuxAb5d1phbOzVqxs6t5KVJlQKrxR965YUJOrdsZ-p3LdJr0q9rDCaPbe5GQ927H0Cx4-yEz3WtVIjbwqfTP_5CnFSlNOaQml1mULQm-QkniI5YRp_e9BsYnmzaXYOukXmeR8KJt0Q; last_non_error_path=%2FPrihlaska"

# -----------------------------
# GUIDy subjektu / prihlásenej osoby
# -----------------------------
SUBJEKT_GUID = "5028de57-b609-4363-8db6-5dd31387e63a"
PRIHLASENA_OSOBA_GUID = "5e1b6f1f-9e38-4546-80ab-6f1ff18f7032"

# -----------------------------
# Školský rok (ZŠ)
# -----------------------------
SKOLSKY_ROK_KOD_2026 = "2026/2027"

SZ_LOGIN_EMAIL = "martin.milacek@professional-test-automation.com"
SZ_LOGIN_PASSWORD = "Initial0!"
