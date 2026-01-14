# End-to-End Test Automation & Load Testing Framework

This repository contains a **professional-grade test automation and performance testing framework** for the *ePrihlášky* ecosystem. It covers:

- **Functional API flows** (Child, ZŠ application, SŠ application, Search)
- **End-to-end application flows** with real SAML authentication
- **Load & stress testing** using Locust (simple and behavior-driven)
- **Automated reporting** (HTML, CSV, PDF)
- **CI/CD execution** via GitHub Actions with GitHub Pages publishing

The framework is designed to be **deterministic, environment-agnostic, and production-like**, simulating real user behavior.

---

## 1. Requirements

### Local machine

- **Python**: 3.11+
- **pip**: latest version
- **Git**

Recommended:
- macOS / Linux (Windows via WSL also works)

---

## 2. Installation

### 2.1 Clone repository

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_NAME>
```

### 2.2 Create virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` is not present:

```bash
pip install locust requests beautifulsoup4 pandas matplotlib reportlab
```

---

## 3. Runtime Configuration

The framework **does not hard-code environments or credentials**.

Runtime values are resolved in the following priority:

1. **Environment variables**
2. **GitHub Secrets** (CI)
3. **Defaults in `config/env.py` and `config/runtime.py`**

### Key variables

| Variable | Description | Example |
|--------|------------|--------|
| `BASE_URL` | Application base URL | https://test-eprihlasky.iedu.sk |
| `IDP_URL` | TIAM Identity Provider URL | https://tiamidsk.iedu.sk |
| `LOGIN_USERNAME` | Login username | user@example.com |
| `LOGIN_PASSWORD` | Login password | *(secret)* |
| `LOAD_PROFILE_NAME` | Locust load profile | light_mixed |

---

## 4. Authentication – SAML

All flows use **real SAML authentication** implemented in:

```
login/saml_login.py
```

Process:
1. Redirect to application login
2. Redirect to TIAM IdP
3. Submit credentials
4. Process SAML response
5. Extract CSRF token and session cookies

Authentication is:
- Executed once per run
- Reused for Locust users
- Never logged with sensitive data

---

## 5. Functional Test Execution (Local)

### 5.1 Child – CRUD

```bash
python3 tests/child/full_flow.py --show-data
```

### 5.2 ZŠ application

```bash
python3 tests/prihlaska/ZS_full_flow.py --show-data
```

### 5.3 SŠ application

```bash
python3 tests/prihlaska/SS_full_flow.py --show-data
```

### 5.4 Search (Vyhľadávanie)

```bash
python3 tests/vyhladavanie/full_flow.py --show-data
```

---

## 6. Load & Stress Testing (Locust)

### 6.1 Simple load test (users / ramp-up / duration)

Local run:

```bash
python3 -m locust   -f tests/locust/full_flow_locust_all.py   --headless   -u 50   -r 5   -t 2m   --html report.html   --csv results
```

Used mainly for:
- quick smoke load
- sanity performance checks

---

### 6.2 Behaviour load test (profile-driven)

Profiles are defined in:

```
tests/locust/load_profiles/
```

Each profile represents a **realistic load pattern** used in enterprise performance testing.

#### Available load profiles

| Profile | Description |
|-------|------------|
| `baseline` | Very low, stable traffic. Used for environment sanity and monitoring validation. |
| `light_baseline` | Light steady load simulating normal off-peak usage. |
| `light_mixed` | Mixed functional usage under light load (default profile). |
| `light_peak` | Short light peak on top of baseline traffic. |
| `light_spike` | Sudden short spike followed by recovery. |
| `capacity` | Gradual ramp-up to identify system capacity limits. |
| `peak` | High peak load representing worst expected production traffic. |
| `spike` | Aggressive spike to test auto-scaling and error handling. |
| `soak` | Long-running steady load to detect memory leaks and degradation. |
| `regression` | Reproducible load pattern used for performance regression comparison. |
| `warmup` | Short warm-up run to stabilize caches and JVM/application state. |
| `stress` | Load beyond expected limits to observe failure behavior and recovery. |

Example profile file:

```json
[
  {"after": 0, "users": 50, "rate": 5},
  {"after": 300, "users": 200, "rate": 10},
  {"after": 600, "users": 0, "rate": 20}
]
```

Run locally:

```bash
export LOAD_PROFILE_NAME=light_mixed

python3 -m locust   -f tests/locust/full_flow_spawn.py   --headless   --csv tests/locust/temp/results   --html tests/locust/temp/report.html   --only-summary
```

---

## 7. Reporting

### Generated artifacts

- **Locust HTML report**
- **CSV statistics**
- **Failures CSV**
- **PDF executive report**
- **ZIP logs archive**

### PDF generation

```bash
python3 tests/locust/utils/generate_pdf_report.py
```

Includes:
- Test context (profile, URLs, user)
- Load overview
- Response times
- Error analysis
- Recommendations

---

## 8. GitHub Actions – How to Run Tests

### 8.1 Configure secrets (once)

In **Repository → Settings → Secrets and variables → Actions**, define:

- `LOGIN_USERNAME`
- `LOGIN_PASSWORD`

These are used by default if workflow inputs are not provided.

---

### 8.2 Running Behaviour Load Test

1. Go to **GitHub → Actions**
2. Select **Behaviour Load Test (Locust)**
3. Click **Run workflow**
4. Fill inputs:
   - **profile** – load profile (dropdown)
   - **base_url** – optional (default is test environment)
   - **idp_url** – optional
   - **username / password** – optional (override secrets)

5. Click **Run workflow**

---

### 8.3 Running Simple Load Test

1. Go to **GitHub → Actions**
2. Select **Simple Load Test**
3. Click **Run workflow**
4. Fill inputs:
   - users
   - ramp-up
   - duration
   - base_url (optional)
   - credentials (optional)

---

### 8.4 Where to find results

#### Behaviour / profile-driven load tests

Published automatically to **GitHub Pages**:

```
https://milacekmartin.github.io/mssr-testing/loadtest/
```

Contains:
- Dashboard (`index.html`)
- PDF report
- Locust HTML
- CSV results
- Logs ZIP

#### Simple load tests

```
https://milacekmartin.github.io/mssr-testing/simple-loadtest/report.html
```

---

## 9. Project Philosophy

- No hard-coded credentials
- No hard-coded environments
- Real authentication
- Real workflows
- Production-grade reporting

Designed for:
- CI quality gates
- Performance benchmarking
- Capacity planning
- Regression load testing

---

## Author & Ownership

**Ing. Martin Miláček**  
Professional Test Automation s.r.o.

📧 martin.milacek@professional-test-automation.com  
📱 +421 911 239 661  
🌐 https://professional-test-automation.com
