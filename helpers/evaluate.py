# helpers/evaluate.py
# ===================
#
# Evaluate funkcie pre Locust requesty.
# Nerobia logging — to zabezpečuje HTTPHelper.
# Len správne hlásia success/failure Locustu.

def evaluate(resp, name):
    """
    Evaluate pre bežné POST/GET volania.
    Resp.success() pri 200, inak resp.failure().
    """
    status = resp.status_code

    if status == 200:
        resp.success()
    else:
        # zobrazi sa v Locust UI → Failures tab
        resp.failure(f"{name} FAILED → {status} | {resp.text[:300]}")


def evaluate_scenario(resp, name):
    """
    Evaluate pre scenárové POST/GET volania.
    Zobrazuje chyby v Locust UI.
    """
    status = resp.status_code

    if status == 200:
        resp.success()
    else:
        resp.failure(f"{name} FAILED → {status} | {resp.text[:400]}")
