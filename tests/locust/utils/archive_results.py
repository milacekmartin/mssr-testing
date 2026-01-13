import json
import zipfile
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
LOGS_DIR = BASE / "logs"
META_FILE = BASE / ".last_run_meta.json"

RESULT_FILES = [
    "report.html",
    "results_stats.csv",
    "results_requests.csv",
    "results_failures.csv",
]

LOGS_DIR.mkdir(exist_ok=True)

meta = json.loads(META_FILE.read_text())
profile = meta["profile"]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_path = LOGS_DIR / f"{profile}_{timestamp}.zip"

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for name in RESULT_FILES:
        p = Path(name)
        if p.exists():
            z.write(p, arcname=p.name)

print(f"✔ ZIP created: {zip_path}")
print(zip_path)
