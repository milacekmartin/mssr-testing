# tests/locust/utils/report.py

from datetime import datetime
from config.runtime import DATE_FORMAT
from .cli import section, bullet

def report_child(first, last, dieta):
    section("🧒 CHILD")
    bullet(f"meno: {first} {last}")
    bullet(f"GUID: {dieta.get('guid')}")
    if dieta.get("eduid"):
        bullet(f"EDU ID: {dieta.get('eduid')}")
    bullet(f"dátum narodenia: {dieta.get('datumNarodenia')}")

def report_school_zs(school):
    section("📘 STEP 3 – school")
    bullet(f"škola: {school.get('nazovOficialny', school.get('nazov'))}")
    bullet(f"typ: {school.get('typSaSZNazov')} ({school.get('formaVlastnictvaNazov')})")
    bullet(f"obec: {school.get('obec')}")
    bullet(f"EDUID: {school.get('eduid')}")

def report_school_ss(school, odbor):
    section("📘 STEP 3 – school + field")
    bullet(f"škola: {school['nazov']}")
    bullet(f"EDUID: {school['eduid']}")
    bullet(f"odbor: {odbor['saUONazov']} ({odbor['saUOKod']})")

def report_finalize(detail):
    p = detail.get("prihlaska", {})
    section("📘 STEP 10 – finalize")
    bullet(f"stav prihlášky: {p.get('prihlaskaStavNazov')}")
    bullet(f"krok: {p.get('krokZadavania')}")
    if p.get("datumVytvorenia"):
        bullet(f"vytvorená: {p['datumVytvorenia'][:16].replace('T',' ')}")

def report_submit(ident, guid, school_name, submit, zz=None, odbor=None):
    section("📤 SUBMIT PRIHLÁŠKY")
    bullet(f"identifikátor: {ident}")
    bullet(f"prihlaska GUID: {guid}")
    bullet(f"škola: {school_name}")

    if odbor:
        bullet(f"odbor: {odbor}")
    if zz:
        bullet(f"zákonný zástupca: {zz}")

    bullet("doručenie poštou: nie")
    bullet(f"dátum odoslania: {datetime.now().strftime(DATE_FORMAT)}")

    if submit.get("response", {}).get("pristupovyKod"):
        bullet(f"prístupový kód: {submit['response']['pristupovyKod']}")
