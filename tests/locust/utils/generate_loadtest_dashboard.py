#!/usr/bin/env python3
import os
import shutil
import zipfile
import datetime

PAGES_DIR = "pages/loadtest"
LOGS_DIR = "tests/locust/logs"
REPORTS_DIR = "tests/locust/reports"
TEMP_DIR = "tests/locust/temp"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def zip_logs(output_zip):
    if not os.path.isdir(LOGS_DIR):
        return False

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(LOGS_DIR):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, LOGS_DIR)
                z.write(full, rel)
    return True


def find_latest_pdf():
    if not os.path.isdir(REPORTS_DIR):
        return None

    pdfs = [
        os.path.join(REPORTS_DIR, f)
        for f in os.listdir(REPORTS_DIR)
        if f.lower().endswith(".pdf")
    ]
    return max(pdfs, key=os.path.getmtime) if pdfs else None


def copy_if_exists(src, dst):
    if os.path.exists(src):
        shutil.copy2(src, dst)
        return True
    return False


def generate_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Load Test Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    h1 {{ color: #1d3557; }}
    ul {{ line-height: 1.8; }}
    a {{ font-size: 18px; }}
    .ok {{ color: green; }}
    .missing {{ color: red; }}
  </style>
</head>
<body>

<h1>📊 Behaviour Load Test – Report Dashboard</h1>
<p><strong>Generated:</strong> {now}</p>

<h2>📄 Reports</h2>
<ul>
  <li><a href="report.pdf">📕 PDF Executive Report</a></li>
  <li><a href="locust.html">📈 Locust HTML Report</a></li>
</ul>

<h2>📦 Artifacts</h2>
<ul>
  <li><a href="logs.zip">🗜️ Logs archive (ZIP)</a></li>
  <li><a href="results_stats.csv">📊 Stats CSV</a></li>
  <li><a href="results_failures.csv">❌ Failures CSV</a></li>
</ul>

</body>
</html>
"""
    with open(os.path.join(PAGES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ensure_dir(PAGES_DIR)

    # ZIP logs
    zip_logs(os.path.join(PAGES_DIR, "logs.zip"))

    # Copy latest PDF
    pdf = find_latest_pdf()
    if pdf:
        shutil.copy2(pdf, os.path.join(PAGES_DIR, "report.pdf"))

    # Copy locust outputs
    copy_if_exists(
        os.path.join(TEMP_DIR, "report.html"),
        os.path.join(PAGES_DIR, "locust.html"),
    )

    copy_if_exists(
        os.path.join(TEMP_DIR, "results_stats.csv"),
        os.path.join(PAGES_DIR, "results_stats.csv"),
    )

    copy_if_exists(
        os.path.join(TEMP_DIR, "results_failures.csv"),
        os.path.join(PAGES_DIR, "results_failures.csv"),
    )

    generate_html()
    print(f"✅ Load test dashboard generated: {PAGES_DIR}/index.html")


if __name__ == "__main__":
    main()
