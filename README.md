# 🧪 API Test Automation Framework

> An enterprise-grade API automation testing framework built on **Pytest + Allure**, designed for multi-tenant SaaS platforms with scenario-driven regression coverage across multiple core business modules.

---

## 📌 Overview

This project is a portfolio piece demonstrating end-to-end engineering practices for API test automation in an enterprise SaaS environment. Key capabilities include:

- **Multi-environment & multi-tenant** configuration management — one codebase adapts to any client environment
- **Scenario-driven test design** organized by business module, with full BVT regression coverage
- **Data-driven approach** — request data is fully decoupled from test logic for easy maintenance
- **One-click execution** — integrates multi-threading, logging, Allure report generation, and instant messaging notifications

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    local_run.py                      │
│   ( Entry Point · Multi-thread · Report · Notify )   │
└────────────────────────┬─────────────────────────────┘
                         │
           ┌─────────────▼──────────────┐
           │       testcase_scene/      │
           │   ( Scenario Test Layer )  │
           │   test_bvt_*.py  Regression│
           └───────┬───────────┬────────┘
                   │           │
      ┌────────────▼───┐  ┌────▼──────────────────┐
      │  *_base.py     │  │       data/            │
      │ Request Layer  │  │  Decoupled Input Data  │
      └────────┬───────┘  └────────────────────────┘
               │
      ┌────────▼──────────────────────────┐
      │          common_tools/            │
      │  env_config · mysql · file_upload │
      └────────┬──────────────────────────┘
               │
      ┌────────▼──────────────────────────┐
      │              conf/                │
      │   Multi-tenant YAML Configs       │
      └───────────────────────────────────┘
```

---
# Results
## Test Report
<img width="1896" height="865" alt="image" src="https://github.com/user-attachments/assets/916f71c3-e6dd-43c3-9348-d66f76b52f02" />

## Test Case Analysis

<img width="1878" height="909" alt="image" src="https://github.com/user-attachments/assets/151461bb-b907-4208-974e-caf0d58ca0f8" />

## 🗂️ Project Structure

```
.
├── common_tools/                   # Shared utility layer
│   ├── env_config.py               # Reads YAML environment configs from conf/
│   ├── mysql_operate.py            # Database query wrapper for data validation
│   └── file_upload.py              # Chunked file upload base implementation
│
├── conf/                           # Multi-tenant environment configs
│   ├── conf1/                      # Client group 1
│   │   ├── env1.yaml               # Client 1 environment
│   │   └── env2.yaml               # Client 2 environment
│   └── conf2/                      # Client group 2
│       └── env3.yaml               # Client 3 environment
│
├── testcase_scene/                 # Test cases organized by business scenario
│   ├── module1/                    # Business module 1
│   │   ├── feature1/               # Feature 1
│   │   │   ├── data/               # API request payloads
│   │   │   ├── feature1_base.py    # Atomic API request encapsulation
│   │   │   └── test_bvt_feature1.py  # BVT regression test cases
│   │   ├── feature2/               # Feature 2 (same structure as feature1)
│   │   └── module1_tools/          # One-off scripts (excluded from regression)
│   │       ├── test_data_consistency_parametrize.py  # Upstream/downstream data consistency check
│   │       └── test_file_upload.py                   # Business-scenario file upload validation
│   ├── module2/                    # Business module 2 (same structure as module1)
│
├── allure/                         # Allure historical report storage
├── conftest.py                     # Global Pytest fixtures
├── local_run.py                    # One-click execution entry point
└── pytest.ini                      # Pytest configuration
```

---

## ⚙️ Module Breakdown

### `local_run.py` — Execution Entry Point

The central control script. All runtime configuration is managed here — no other files need to be modified to switch environments or adjust execution scope.

| Feature | Description |
|---------|-------------|
| Environment switching | Specify the target YAML config file |
| Test filtering | Filter by module or marker (e.g. `bvt`) |
| Multi-threaded execution | Concurrent runs via `threading` for faster feedback |
| Logging | Unified formatted output with level-based archiving |
| Allure report | Auto-generated and archived after each run |
| Notification | Pushes report summary to team chat tool on completion |

### `common_tools/` — Shared Utilities

| File | Responsibility |
|------|----------------|
| `env_config.py` | Parses YAML configs and injects environment variables (host, token, DB credentials, etc.) |
| `mysql_operate.py` | Wraps DB query methods for response-vs-database consistency assertions |
| `file_upload.py` | Encapsulates chunked file upload logic, reusable across all modules |

### `testcase_scene/` — Test Case Convention

Every business module follows a consistent three-layer structure:

```
module/
├── feature/
│   ├── data/                  # API input data (JSON/YAML), decoupled from logic
│   ├── feature_base.py        # Atomic API call encapsulation for this feature
│   └── test_bvt_feature.py    # Scenario-level tests with assertions & DB validation
└── module_tools/              # Ad-hoc / exploratory scripts, excluded from CI regression
```

> **BVT Marker**: Files prefixed with `test_bvt_` form the regression suite and are triggered automatically after each iteration.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Primary language |
| Pytest | Test framework |
| Allure | Test reporting |
| PyYAML | Environment config parsing |
| PyMySQL | Database validation |
| threading | Concurrent test execution |
| Requests | HTTP API requests |

---

## 📐 Design Principles

1. **Layered decoupling** — Data layer → Request layer → Scenario layer. Each layer has a single responsibility and does not bleed into others.
2. **Multi-tenant support** — Client environments are fully isolated under `conf/`. Switching targets requires zero code changes.
3. **Regression vs. exploration** — `test_bvt_*.py` files serve CI regression; `*_tools/` scripts serve ad-hoc validation. They never interfere with each other.
4. **DB-level assertions** — Validations go beyond status codes, verifying upstream/downstream data consistency directly against the database.

---

## 📄 License

This is a personal portfolio project intended for reference and demonstration purposes only.
