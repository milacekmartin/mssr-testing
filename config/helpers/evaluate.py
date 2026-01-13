# helpers/evaluate.py

def evaluate(resp, name):
    status = resp.status_code

    if status == 200:
        resp.success()
    else:
        resp.failure(f"{name} FAILED → {status} | {resp.text[:300]}")


def evaluate_scenario(resp, name):
    status = resp.status_code

    if status == 200:
        resp.success()
    else:
        resp.failure(f"{name} FAILED → {status} | {resp.text[:400]}")
