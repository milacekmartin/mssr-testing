# End‑to‑End Test Automation & Load Testing Framework

This repository contains a **professional‑grade test automation and performance testing framework** for the *ePrihlášky* ecosystem. It covers:

- **Functional API flows** (Child, ZŠ application, SŠ application, Search)
- **End‑to‑end application flows** with real SAML authentication
- **Load & stress testing** using Locust with dynamic user profiles
- **Automated reporting** (HTML, CSV, PDF)
- **CI/CD execution** via GitHub Actions

The framework is designed to be **deterministic, environment‑agnostic, and production‑like**, simulating real user behavior.

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

If `requirements.txt` is not present, install manually:

```bash
pip install locust requests beautifulsoup4 pandas matplotlib reportlab
```

---

## 3. Runtime Configuration

The framework **does not hard‑code environments**.

All runtime‑specific values are resolved dynamically from:

1. **Environment variables** (highest priority)
2. **GitHub Secrets** (in CI)
3. **Defaults defined in `config/env.py` and `config/runtime.py`**

### Key runtime variables

| Variable | Description | Example |
|--------|------------|--------|
| `HOST` | Base application URL | `https://test-eprihlasky.iedu.sk` |
| `TIAM_BASE` | Identity Provider (TIAM) URL | `https://tiamidsk.iedu.sk` |
| `LOGIN_USERNAME` | Login username | `user@example.com` |
| `LOGIN_PASSWORD` | Login password | *(secret)* |
| `LOAD_PROFILE_NAME` | Locust load profile | `baseline`, `light_mixed`, `stress` |

Example:

```bash
export HOST=https://test-eprihlasky.iedu.sk
export LOGIN_USERNAME=user@example.com
export LOGIN_PASSWORD=******
```

---

## 4. Authentication – SAML

All flows use **real SAML authentication** implemented in:

```
login/saml_login.py
```

The login process:
1. Redirect to application login
2. Redirect to TIAM IdP
3. Submit credentials
4. Process SAML response
5. Extract CSRF token, session cookies, subject GUIDs

Login is:
- **Executed once per test run** in Locust
- **Shared across users** for performance realism

---

## 5. Functional Test Execution (Local)

### 5.1 Child – CRUD tests

```bash
python3 tests/child/full_flow.py --show-data
```

Covers:
- Create child
- Update child
- Verify data
- Delete child

---

### 5.2 ZŠ application – full flow

```bash
python3 tests/prihlaska/ZS_full_flow.py --show-data
```

Steps:
1. Create child
2. Create application
3. Complementary data
4. School search
5. School selection
6. Finalization
7. Submit application

---

### 5.3 SŠ application – full flow (capability‑driven)

```bash
python3 tests/prihlaska/SS_full_flow.py --show-data
```

Includes:
- Dynamic school capability detection
- Adaptive steps (talent exams, grades, competitions)

---

### 5.4 Search (Vyhľadávanie)

```bash
python3 tests/vyhladavanie/full_flow.py --show-data
```

Covers:
- MS search
- ZŠ search
- SŠ search
- Pagination, filters, combinations

---

## 6. Load & Stress Testing (Locust)

### 6.1 Available scenarios

- **Child CRUD**
- **ZŠ application**
- **SŠ application**
- **Search (MS / ZŠ / SŠ)**
- **Random cleanup**

All combined in:

```
tests/locust/full_flow_locust_all.py
```

---

### 6.2 Load profiles

Load profiles are defined as JSON files:

```
tests/locust/load_profiles/
```

Example:

```json
[
  {"after": 0, "users": 10, "rate": 2},
  {"after": 60, "users": 50, "rate": 5},
  {"after": 120, "users": 0, "rate": 1}
]
```

Select profile via environment variable:

```bash
export LOAD_PROFILE_NAME=light_mixed
```

---

### 6.3 Run Locust (headless)

```bash
LOAD_PROFILE_NAME=light_mixed \
python3 -m locust \
  -f tests/locust/full_flow_spawn.py \
  --headless \
  --csv tests/locust/temp/results \
  --html tests/locust/temp/report.html \
  --only-summary
```

What happens:
- Load profile controls user ramp‑up
- Full mixed scenario is executed
- CSV + HTML reports are generated

---

## 7. Automatic Reports

### 7.1 Archive results

```bash
python3 tests/locust/utils/archive_results.py
```

Creates ZIP archive with:
- HTML report
- CSV statistics
- Failures

---

### 7.2 Generate PDF report

```bash
python3 tests/locust/utils/generate_pdf_report.py
```

The PDF includes:
- Test context (URL, profile, methodology)
- Load charts (users, RPS)
- Response times (avg, p95)
- Endpoint overview
- Error analysis
- Recommendations

---

## 8. GitHub Actions (CI/CD)

The repository contains **professional reusable pipelines** for:

- Child tests
- ZŠ application tests
- SŠ application tests
- Search tests
- Full behavior / load testing

All pipelines:
- Can be **triggered manually** (`workflow_dispatch`)
- Allow **runtime configuration** (URLs, credentials, profiles)
- Use **GitHub Secrets by default**
- Publish **artifacts and reports** automatically

---

## 9. Project Philosophy

- ❌ No hard‑coded credentials
- ❌ No hard‑coded environments
- ✅ Real authentication
- ✅ Real workflows
- ✅ Deterministic test data
- ✅ Production‑grade reporting

This framework is suitable for:
- Performance benchmarking
- Regression testing
- CI quality gates
- Capacity planning

---

## 10. Support & Extension

The architecture is modular:

- Add new flows easily
- Extend payload builders safely
- Add new load profiles without code changes

If you need:
- SLA validation
- Threshold‑based pipeline failures
- Trend comparison across runs

The framework is already prepared for it.

---

## Author & Ownership

**Ing. Martin Miláček**  
Professional Test Automation s.r.o.

📧 Email: martin.milacek@professional-test-automation.com  
📱 Phone: +421 911 239 661  
🌐 Website: https://professional-test-automation.com

This project and its automation framework were designed and implemented by Professional Test Automation s.r.o.  
All scripts, pipelines, and testing methodologies reflect real-world enterprise QA and performance testing practices.
