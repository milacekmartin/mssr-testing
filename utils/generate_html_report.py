import sys, datetime, html, os

def generate_html_report(title, log_text, output_file):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
<html>
<head>
    <meta charset="utf-8" />
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><strong>Generated:</strong> {now}</p>
    <h2>Raw Output</h2>
    <pre>{html.escape(log_text)}</pre>
</body>
</html>
"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_index(output_path="pages/index.html"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_index = f"""
<html>
<head>
    <meta charset="utf-8" />
    <title>Test Reports Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #1d3557; }}
        ul {{ line-height: 1.8; }}
        a {{ font-size: 18px; }}
    </style>
</head>
<body>
    <h1>📊 Test Reports Dashboard</h1>
    <p>Generated: {now}</p>

    <h2>Load Tests</h2>
    <ul>
        <li><a href="loadtest/report.html">Locust HTML Report</a></li>
        <li><a href="loadtest/results_stats.csv">Stats CSV</a></li>
        <li><a href="loadtest/results_failures.csv">Failures CSV</a></li>
    </ul>

</body>
</html>
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_index)

