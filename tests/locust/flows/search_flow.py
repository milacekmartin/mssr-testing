from tests.vyhladavanie.payloads.ms import build_search_payload
from tests.vyhladavanie.payloads.zs import build_search_payload_zs
from tests.vyhladavanie.payloads.ss import build_search_payload_ss

from tests.vyhladavanie.search_cases.ms import MS_SEARCH_CASES
from tests.vyhladavanie.search_cases.zs import ZS_SEARCH_CASES
from tests.vyhladavanie.search_cases.ss import SS_SEARCH_CASES

from tests.locust.common.client import post
from tests.locust.common.logging import flow_start, flow_end
from tests.locust.common.guards import expect_json_dict
from tests.locust.common.failures import fail_request


def run_search_flow(user):
    flow_start("VYHĽADÁVANIE", "MS / ZŠ / SŠ")

    # ============================================================
    # MS SEARCH
    # ============================================================
    for name, cfg in MS_SEARCH_CASES:
        r = post(
            user,
            "/api/vyhladanieMSaZS",
            build_search_payload(**cfg),
            f"SEARCH / MS – {name}",
        )
        data = expect_json_dict(user, r, f"SEARCH / MS – {name}", "SEARCH FAILED")
        if not data:
            return

    # ============================================================
    # ZŠ SEARCH
    # ============================================================
    for name, cfg in ZS_SEARCH_CASES:
        r = post(
            user,
            "/api/vyhladanieMSaZS",
            build_search_payload_zs(**cfg),
            f"SEARCH / ZS – {name}",
        )
        data = expect_json_dict(user, r, f"SEARCH / ZS – {name}", "SEARCH FAILED")
        if not data:
            return

    # ============================================================
    # SŠ SEARCH
    # ============================================================
    for name, cfg in SS_SEARCH_CASES:
        r = post(
            user,
            "/api/vyhladanieSaSZSS",
            build_search_payload_ss(**cfg),
            f"SEARCH / SS – {name}",
        )
        data = expect_json_dict(user, r, f"SEARCH / SS – {name}", "SEARCH FAILED")
        if not data:
            return

    flow_end("VYHĽADÁVANIE")
