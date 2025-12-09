import datetime

def generate_index(output="pages/index.html"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
<html>
<head>
    <meta charset="utf-8" />
    <title>Test Reports</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1 {{ color: #1d3557; }}
        ul {{ line-height: 1.8; }}
        a {{ font-size: 18px; }}
    </style>
</head>
<body>
    <h1>📊 Test Reports</h1>
    <p>Generated: {now}</p>

    <h2>Child Tests</h2>
    <ul>
        <li><a href="child/create_tests_report.html">Child Create Tests Report</a></li>
        <li><a href="child/full_flow_report.html">Child Full Flow Report</a></li>
    </ul>
</body>
</html>
"""
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    generate_index()
