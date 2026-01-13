# tests/locust/common/failures.py

def fail_request(user, request_type, name, response, message):
    try:
        response.failure(message)
    except Exception:
        pass

    try:
        user.environment.events.request_failure.fire(
            request_type=request_type,
            name=name,
            response_time=0,
            exception=Exception(message),
            response=response,
        )
    except Exception:
        pass
