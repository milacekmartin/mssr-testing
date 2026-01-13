# tests/locust/common/auth.py

from login.saml_login import saml_login

def login_user():
    return saml_login()
