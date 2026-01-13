import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"

LOCUST_FILE = BASE_DIR / "full_flow_spawn.py"
ARCHIVE_SCRIPT = BASE_DIR / "utils" / "archive_results.py"
PDF_SCRIPT = BASE_DIR / "utils" / "generate_pdf_report.py"

PYTHON = sys.executable


def run(cmd, desc, allow_fail=False):
    print(f"\n▶ {desc}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0 and not allow_fail:
        print(f"❌ Failed: {desc}")
        sys.exit(result.returncode)
    return result.returncode


# ------------------------------------------------------------------
# PREPARE TEMP DIR
# ------------------------------------------------------------------
TEMP_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------
# RUN LOCUST (ALLOW FAIL)
# ------------------------------------------------------------------
locust_exit_code = run(
    f"""
    {PYTHON} -m locust \
      -f "{LOCUST_FILE}" \
      --headless \
      --csv "{TEMP_DIR / 'results'}" \
      --html "{TEMP_DIR / 'report.html'}" \
      --only-summary \
      --host "{os.getenv('LOCUST_HOST', 'http://localhost')}"
    """,
    "Running Locust load test",
    allow_fail=True   # ⬅️ kľúčová zmena
)

# ------------------------------------------------------------------
# ARCHIVE RAW RESULTS (ALWAYS)
# ------------------------------------------------------------------
run(
    f'{PYTHON} "{ARCHIVE_SCRIPT}"',
    "Archiving raw results (ZIP)",
    allow_fail=False
)

# ------------------------------------------------------------------
# GENERATE PDF REPORT (ALWAYS)
# ------------------------------------------------------------------
run(
    f'{PYTHON} "{PDF_SCRIPT}"',
    "Generating professional PDF report",
    allow_fail=False
)

print("\n📄 PDF report generated successfully")

# ------------------------------------------------------------------
# FINAL EXIT CODE (PROPAGATE LOCUST RESULT)
# ------------------------------------------------------------------
if locust_exit_code != 0:
    print("\n⚠️ Load test finished with FAILURES (exit code 1)")
    sys.exit(locust_exit_code)

print("\n✅ Load test finished successfully")
sys.exit(0)
