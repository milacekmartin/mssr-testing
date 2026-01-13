import random

from tests.locust.common.client import post
from tests.locust.common.utils import safe_json
from tests.locust.common.logging import flow_start, flow_end
from tests.locust.common.failures import fail_request

from tests.locust.common.guards import expect_json_dict

def run_random_cleanup_flow(user):
    flow_start("RANDOM CLEANUP", "ZS + SS")

    r = post(
        user,
        "/api/vratenieZoznamuPrihlasokSubjektu",
        {"SubjektGUID": user.login.subj_guid},
        "CLEANUP / Load applications",
    )

    data = expect_json_dict(
        user, r,
        "CLEANUP / Load applications",
        "RANDOM CLEANUP – FAILED",
    )
    if not data:
        return

    prihlasky = data.get("prihlaska")
    if not isinstance(prihlasky, list):
        fail_request(
            user, "POST",
            "CLEANUP / Load applications – invalid payload",
            r,
            f"Expected prihlaska list, got {type(prihlasky).__name__}",
        )
        flow_end("RANDOM CLEANUP – FAILED")
        return

    eligible = []
    for p in prihlasky:
        if not isinstance(p, dict):
            continue

        typ = p.get("typPrihlaskyKod")
        stav = p.get("stavKod")

        if typ == "SŠ" and stav == "5":
            eligible.append(p)
        elif typ == "ZŠ" and stav == "2":
            eligible.append(p)

    if not eligible:
        flow_end("RANDOM CLEANUP – NOTHING TO DELETE")
        return

    target = random.choice(eligible)
    prihlaska_guid = target.get("prihlaskaGUID")
    dieta_guid = target.get("dietaGUID")

    if not prihlaska_guid or not dieta_guid:
        fail_request(
            user, "POST",
            "CLEANUP / Invalid application object",
            r,
            f"Invalid target object: {target}",
        )
        flow_end("RANDOM CLEANUP – FAILED")
        return

    post(
        user,
        "/api/vymazPrihlasky",
        {"PrihlaskaGUID": prihlaska_guid},
        f"CLEANUP / Delete {target.get('typPrihlaskyKod')} application",
    )

    post(
        user,
        "/api/vymazDietata",
        {"guid": dieta_guid},
        "CLEANUP / Delete child",
    )

    flow_end("RANDOM CLEANUP – OK")

