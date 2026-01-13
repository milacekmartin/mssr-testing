# tests/locust/common/guards.py

from tests.locust.common.failures import fail_request
from tests.locust.common.logging import flow_end


def expect_json_dict(user, response, step_name, end_flow_label):
    try:
        data = response.json()
        
    except Exception:
        fail_request(
            user,
            response.request.method,
            f"{step_name} – invalid JSON",
            response,
            f"Non-JSON response, status={response.status_code}, body={response.text[:300]}",
        )
        flow_end(end_flow_label)
        return None

    if not isinstance(data, dict):
        fail_request(
            user,
            response.request.method,
            f"{step_name} – invalid response type",
            response,
            f"Expected JSON object, got {type(data).__name__}",
        )
        flow_end(end_flow_label)
        return None

    return data
