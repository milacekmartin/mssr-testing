import subprocess
import os
import sys

PROFILE = os.getenv("LOAD_PROFILE_NAME", "light_mixed")

def run(cmd, name):
    print(f"\n▶ {name}")
    r = subprocess.run(cmd, shell=True)
    print(f"▶ {name} finished with code {r.returncode}")
    return r.returncode

code = run(
    f"""
    LOAD_PROFILE_NAME={PROFILE} python3 -m locust \
      -f tests/locust/full_flow_spawn.py \
      --headless \
      --csv tests/locust/temp/results \
      --html tests/locust/temp/report.html \
      --only-summary \
      --loglevel WARNING
    """,
    "LOCUST LOAD TEST"
)

print("\n▶ Generating PDF report")
subprocess.run("python3 tests/locust/utils/generate_pdf_report.py", shell=True)

print("\n▶ Archiving results")
subprocess.run("python3 tests/locust/utils/archive_results.py", shell=True)

sys.exit(code)
