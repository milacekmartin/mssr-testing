# tests/locust/full_flow_spawn.py

import json
import os
from pathlib import Path
from locust import LoadTestShape
from tests.locust.users.full_flow_user import FullFlowUser

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "load_profiles"
META_FILE = BASE_DIR / ".last_run_meta.json"


def load_profile():
    name = os.getenv("LOAD_PROFILE_NAME", "baseline")
    path = PROFILE_DIR / f"{name}.json"

    if not path.exists():
        raise FileNotFoundError(f"Load profile not found: {path}")

    with path.open() as f:
        profile = json.load(f)

    if profile[-1]["users"] != 0:
        raise ValueError("Load profile MUST end with users = 0")

    META_FILE.write_text(json.dumps({
        "profile": name
    }))

    return sorted(profile, key=lambda x: x["after"])


class FullFlowDynamicLoadShape(LoadTestShape):
    stages = load_profile()

    def tick(self):
        run_time = int(self.get_run_time())

        for i, stage in enumerate(self.stages):
            next_stage = self.stages[i + 1] if i + 1 < len(self.stages) else None

            if next_stage and run_time < next_stage["after"]:
                return stage["users"], stage["rate"]

            if not next_stage and run_time >= stage["after"]:
                return None

        return None
