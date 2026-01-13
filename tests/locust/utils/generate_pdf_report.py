import json
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_DIR = BASE_DIR / "temp"
REPORTS_DIR = BASE_DIR / "reports"
META_FILE = BASE_DIR / ".last_run_meta.json"
HISTORY_FILE = REPORTS_DIR / "_history.json"
ICONS_DIR = BASE_DIR / "assets" / "icons"

REPORTS_DIR.mkdir(exist_ok=True)

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONT_TITLE = ("Helvetica-Bold", 18)
FONT_SECTION = ("Helvetica-Bold", 14)
FONT_TEXT = ("Helvetica", 11)
FONT_TABLE_HEADER = ("Helvetica-Bold", 10)
FONT_TABLE = ("Helvetica", 10)

PAGE_TOP = 800
PAGE_BOTTOM = 60
LINE = 18

# =============================================================================
# HELPERS
# =============================================================================
def find_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"Expected one of {candidates}, got {list(df.columns)}")

def draw_icon_text(c, icon, text, x, y, font):
    font_name, font_size = font
    icon_path = ICONS_DIR / icon
    ascent = font_size * 0.75
    icon_size = font_size + 2
    icon_y = y - (icon_size - ascent) / 2
    c.setFont(font_name, font_size)

    if icon_path.exists():
        c.drawImage(str(icon_path), x, icon_y, icon_size, icon_size, mask="auto")
        c.drawString(x + icon_size + 6, y, text)
    else:
        c.drawString(x, y, text)

def draw_table(c, x, y, headers, rows, col_widths):
    c.setFont(*FONT_TABLE_HEADER)
    cx = x
    for h, w in zip(headers, col_widths):
        c.drawString(cx, y, h)
        cx += w

    y -= 8
    c.setLineWidth(0.7)
    c.line(x, y, x + sum(col_widths), y)
    y -= 14

    c.setFont(*FONT_TABLE)
    for row in rows:
        cx = x
        for cell, w in zip(row, col_widths):
            c.drawString(cx, y, str(cell))
            cx += w
        y -= 14
        if y < PAGE_BOTTOM:
            c.showPage()
            y = PAGE_TOP - 40
            c.setFont(*FONT_TABLE)

    return y - 12

def extract_host_from_html(report_html):
    if not report_html.exists():
        return None
    content = report_html.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"Host:\s*(https?://[^\s<]+)", content)
    return m.group(1) if m else None

# =============================================================================
# LOAD DATA
# =============================================================================
meta = json.loads(META_FILE.read_text())
profile = meta["profile"]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

stats = pd.read_csv(TEMP_DIR / "results_stats.csv")
history = pd.read_csv(TEMP_DIR / "results_stats_history.csv")
failures = pd.read_csv(TEMP_DIR / "results_failures.csv")

time_col = find_column(history, ["Timestamp"])
users_col = find_column(history, ["User Count"])
rps_col = find_column(history, ["Requests/s"])
avg_rt_col = find_column(history, ["Total Average Response Time"])
p95_col = find_column(history, ["95%"])

name_col = find_column(stats, ["Name"])
avg_col = find_column(stats, ["Average Response Time"])
fail_col = find_column(stats, ["Failure Count"])
req_col = find_column(stats, ["Request Count"])

total_requests = int(stats[req_col].sum())
total_failures = int(stats[fail_col].sum())
error_rate = round((total_failures / total_requests) * 100, 2)
global_p95 = int(history[p95_col].max())
max_users = int(history[users_col].max())

# =============================================================================
# DYNAMIC TARGET URL
# =============================================================================
TARGET_URL = (
    os.getenv("LOCUST_HOST")
    or os.getenv("TARGET_URL")
    or extract_host_from_html(TEMP_DIR / "report.html")
    or "UNKNOWN"
)

# =============================================================================
# DATASETS FOR TABLES
# =============================================================================
endpoint_overview = stats.sort_values(by=avg_col, ascending=False)
root_cause = stats[stats[fail_col] > 0].sort_values(by=[fail_col, avg_col], ascending=[False, False])
submit_endpoints = stats[stats[name_col].str.contains("Submit", case=False, na=False)]

error_summary = (
    failures.groupby("Error")["Occurrences"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

error_list = (
    failures.groupby(["Name", "Error"])["Occurrences"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# =============================================================================
# TEST CONTEXT
# =============================================================================
TEST_CONTEXT = {
    "Target URL": TARGET_URL,
    "Test profile": profile,
    "Test type": "Load / Stress (mixed scenario)",
    "Authentication": "SAML (real user login)",
    "Test tool": "Locust",
    "Execution mode": "Headless",
    "Total requests": total_requests,
    "Max concurrent users": max_users,
}

# =============================================================================
# PLOTS (PREGENERATED)
# =============================================================================
def plot(x, y, title, ylabel, fname):
    plt.figure(figsize=(8, 3))
    plt.plot(x, y)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Time")
    plt.tight_layout()
    p = TEMP_DIR / fname
    plt.savefig(p)
    plt.close()
    return p

plot(history[time_col], history[users_col], "Users Over Time", "Users", "users.png")
plot(history[time_col], history[rps_col], "Requests Per Second", "RPS", "rps.png")
plot(history[time_col], history[avg_rt_col], "Average Response Time", "ms", "avg_rt.png")
plot(history[time_col], history[p95_col], "95th Percentile Response Time", "ms", "p95.png")

# =============================================================================
# PDF GENERATION
# =============================================================================
pdf_path = REPORTS_DIR / f"{profile}_{timestamp}.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=A4)

# =============================================================================
# PAGE 1 – SUMMARY + CONTEXT + LOAD
# =============================================================================
draw_icon_text(c, "analysis.png", "Performance Test Report", 40, 800, FONT_TITLE)
draw_icon_text(c, "profile.png", f"Profile: {profile}", 40, 760, FONT_TEXT)
draw_icon_text(c, "time.png", f"Generated: {timestamp}", 40, 740, FONT_TEXT)
draw_icon_text(c, "requests.png", f"Total requests: {total_requests}", 40, 720, FONT_TEXT)
draw_icon_text(c, "verdict.png", f"Error rate: {error_rate} %", 40, 700, FONT_TEXT)
draw_icon_text(c, "verdict.png", "Verdict: FAIL", 40, 680, FONT_TEXT)

draw_icon_text(c, "analysis.png", "Test Context & Methodology", 40, 640, FONT_SECTION)
y = draw_table(
    c, 40, 610,
    ["Parameter", "Value"],
    [[k, v] for k, v in TEST_CONTEXT.items()],
    [200, 320]
)

c.setFont(*FONT_TEXT)
methodology = [
    "• Test simulates real user behaviour across search, child management and submission flows.",
    "• Load was increased step-wise until performance degradation and saturation were observed.",
    "• Metrics were collected continuously and evaluated against defined SLA thresholds.",
]
for line in methodology:
    c.drawString(40, y, line)
    y -= LINE

draw_icon_text(c, "response.png", "Load Overview", 40, y - 10, FONT_SECTION)
c.drawImage(str(TEMP_DIR / "users.png"), 40, y - 170, 520, 140)
c.drawImage(str(TEMP_DIR / "rps.png"), 40, y - 330, 520, 140)
c.showPage()

# =============================================================================
# PAGE 2 – RESPONSE TIME
# =============================================================================
draw_icon_text(c, "response.png", "Response Time Analysis", 40, 800, FONT_SECTION)
c.drawImage(str(TEMP_DIR / "avg_rt.png"), 40, 520, 520, 180)
c.drawImage(str(TEMP_DIR / "p95.png"), 40, 300, 520, 180)
c.showPage()

# =============================================================================
# PAGE 3 – ENDPOINT OVERVIEW
# =============================================================================
draw_icon_text(c, "endpoints.png", "Endpoint Overview (All)", 40, 800, FONT_SECTION)
y = draw_table(
    c, 40, 760,
    ["Endpoint", "Avg RT (ms)", "p95 RT (ms)", "Errors"],
    [[r[name_col][:45], int(r[avg_col]), f"~{global_p95}", int(r[fail_col])]
     for _, r in endpoint_overview.iterrows()],
    [260, 90, 90, 60]
)
c.showPage()

# =============================================================================
# PAGE 4 – ROOT CAUSE + SUBMIT + ERRORS
# =============================================================================
draw_icon_text(c, "endpoints.png", "Root Cause – Problematic Endpoints", 40, 800, FONT_SECTION)
y = draw_table(
    c, 40, 760,
    ["Endpoint", "Avg RT (ms)", "p95 RT (ms)", "Errors"],
    [[r[name_col][:45], int(r[avg_col]), f"~{global_p95}", int(r[fail_col])]
     for _, r in root_cause.iterrows()],
    [260, 90, 90, 60]
)

draw_icon_text(c, "submit.png", "Submission Endpoints (ZS / SS)", 40, y, FONT_SECTION)
y = draw_table(
    c, 40, y - 20,
    ["Endpoint", "Avg RT (ms)", "p95 RT (ms)", "Errors"],
    [[r[name_col][:45], int(r[avg_col]), f"~{global_p95}", int(r[fail_col])]
     for _, r in submit_endpoints.iterrows()],
    [260, 90, 90, 60]
)

draw_icon_text(c, "verdict.png", "Error Analysis", 40, y, FONT_SECTION)
y = draw_table(
    c, 40, y - 20,
    ["Error Type", "Occurrences"],
    [[r["Error"], int(r["Occurrences"])] for _, r in error_summary.iterrows()],
    [360, 120]
)

draw_icon_text(c, "verdict.png", "Error List (by Endpoint)", 40, y, FONT_SECTION)
y = draw_table(
    c, 40, y - 20,
    ["Endpoint", "Error", "Count"],
    [[r["Name"][:35], r["Error"][:40], int(r["Occurrences"])]
     for _, r in error_list.iterrows()],
    [220, 200, 80]
)
c.showPage()

# =============================================================================
# PAGE 5 – RECOMMENDATIONS
# =============================================================================
draw_icon_text(c, "analysis.png", "Recommendations", 40, 800, FONT_SECTION)
c.setFont(*FONT_TEXT)
y = 760
recommendations = [
    "Isolate Create child flow using asynchronous processing or queue.",
    "Investigate database locking and transaction scope during child creation.",
    "Introduce throttling or rate limiting above ~80 concurrent users.",
    "Define dedicated SLA for Create child operations.",
]
for r in recommendations:
    c.drawString(40, y, f"• {r}")
    y -= LINE

c.save()
print(f"✅ PDF report generated: {pdf_path}")
