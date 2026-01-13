# tests/locust/common/shared_login.py

import threading
from tests.locust.common.auth import login_user

_shared_login = None
_login_lock = threading.Lock()


def get_shared_login():
    global _shared_login

    if _shared_login is not None:
        return _shared_login

    with _login_lock:
        if _shared_login is None:
            print("\n🔐 Performing ONE-TIME SAML login for all users...")
            _shared_login = login_user()
            
            print("🔐 SHARED LOGIN OK")
            print(f"   • Subjekt GUID: {_shared_login.subj_guid}")
            print(f"   • User GUID:    {_shared_login.logged_guid}")

    return _shared_login
