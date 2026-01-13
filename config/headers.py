# config/headers.py

from config.settings import HOST, CSRF, IAM_TOKEN, COOKIE_BUNDLE

# ---------------------------------------------------------
# COMMON HEADERS
# ---------------------------------------------------------

COMMON_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "RequestVerificationToken": CSRF,
    "X-Token-Descriptor": IAM_TOKEN,
    "Cookie": COOKIE_BUNDLE,
}

# ---------------------------------------------------------
# EXTENDED HEADERS
# ---------------------------------------------------------

EXTENDED_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json; charset=UTF-8",
    "Cookie": COOKIE_BUNDLE,
    "Host": "test-eprihlasky.iedu.sk",
    "Origin": HOST,
    "Referer": f"{HOST}/Prihlaska",
    "RequestVerificationToken": CSRF,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors", 
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "x-correlation-id": "",
    "x-token-descriptor": IAM_TOKEN,
}

VYHLEDAVACIE_HEADERS = {
    "x-requested-with": "XMLHttpRequest",
    "origin": HOST,
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "referer": ""
}