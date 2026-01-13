from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

from tests.locust.common.client import post
from tests.locust.common.logging import flow_start, flow_end
from tests.locust.common.utils import safe_json
from tests.locust.common.failures import fail_request

from tests.locust.common.guards import expect_json_dict

def run_child_flow(user):
    first, last = generate_random_name()
    flow_start("CHILD", f"{first} {last}")

    payload = build_base_child_payload(first, last)
    payload["subjektGUID"] = user.login.subj_guid

    r = post(user, "/api/zapisAModifikaciaDietata", payload, "CHILD / Create child")
    data = expect_json_dict(user, r, "CHILD / Create child", "CHILD – FAILED")
    if not data:
        return

    dieta = data.get("dieta")
    guid = dieta.get("guid") if isinstance(dieta, dict) else None
    if not guid:
        fail_request(
            user, "POST",
            "CHILD / Create child – missing guid",
            r,
            f"dieta.guid missing, response={data}",
        )
        flow_end("CHILD – FAILED")
        return

    payload["dietaGUID"] = guid
    payload["pohlavieKod"] = "2"

    post(user, "/api/zapisAModifikaciaDietata", payload, "CHILD / Update child")
    post(user, "/api/vymazDietata", {"guid": guid}, "CHILD / Delete child")

    flow_end("CHILD")

