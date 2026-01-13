# tests/locust/utils/flow_common.py

from config.random_names import generate_random_name
from tests.child.payloads.child import build_base_child_payload

def create_child(login, datum):
    first, last = generate_random_name()
    child = build_base_child_payload(first, last)

    child["subjektGUID"] = login.subj_guid
    child["datumNarodenia"] = datum
    
    return first, last, child
