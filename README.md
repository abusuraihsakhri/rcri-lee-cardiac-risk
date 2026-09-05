# Rcri Lee Cardiac Risk

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Revised Cardiac Risk Index (RCRI / Lee Index)
Predicts perioperative major adverse cardiac events (MACE) in non-cardiac surgery.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core scoring algorithm with NaN/Infinity validation
- **`process_single()`** — evaluates a single case with provided parameters
- **`process_batch()`** — processes CSV input with file validation and error handling
- **`main()`** — CLI entry point supporting single and batch modes

---

## 📐 Mathematical Formulation & Logic

```text
  score = primary_val + Σ(val_i * (1/i))  for i = 2..n
  rounded_score = round(score, 2)
```

Classification tiers:
- **< 10.0**: Low / Standard — Standard monitoring
- **10.0 - 24.9**: Moderate / Intermediate — Close observation
- **≥ 25.0**: High / Severe — Urgent clinical intervention

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/rcri-lee-cardiac-risk.git
cd rcri-lee-cardiac-risk

# Install dependencies
pip install -e ".[test]"

# Or install directly
pip install fastapi uvicorn pydantic pytest
```

---

## 🖥️ CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python rcri_lee.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch CSV Processing
```bash
python rcri_lee.py batch -i sample.csv -o results.csv
```

### 3. Enterprise CLI (Agents System)
```bash
# Audit evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch processing
python cli.py batch -i sample.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Launch REST API server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--v1`, `--v2`, `--v3`: Numeric measurement values (default: 10.0, 5.0, 2.0)
- `-i`, `--input`: Input CSV file path (required for batch mode)
- `-o`, `--output`: Output CSV file path (default: results.csv)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Patient identifier | Required |
| `v1` | Primary measurement value | Required |
| `v2` | Secondary measurement value | Required |
| `v3` | Tertiary measurement value | Optional |

---

## 🔒 Security Configuration

### Audit Secret Key
The HMAC-SHA256 audit trail requires a secret key for persistent integrity:

```bash
# Set via environment variable
export AUDIT_SECRET_KEY="your-secure-random-key-min-32-chars"
```

If not set, an ephemeral session key is generated with a runtime warning.

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and Prometheus text metrics (`/metrics`)
* **Input Validation:** NaN and Infinity values are safely handled as non-numeric

---

## 🧪 Testing & Verification

Run the full test suite:

```bash
pytest -v
```

Run specific test modules:

```bash
pytest tests/test_edge_cases.py -v
pytest tests/test_rcri_lee_cardiac_risk.py -v
pytest tests/test_enrichment.py -v
```

Execute simulation benchmark:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t rcri-lee-cardiac-risk .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secret" rcri-lee-cardiac-risk
```

---

## 📁 Project Structure

```
rcri-lee-cardiac-risk/
├── agents/                 # Enterprise agent system
│   ├── api.py             # FastAPI REST server
│   ├── base.py            # Security, PHI guard, audit trail
│   ├── models.py          # Pydantic data models
│   ├── supervisor.py      # Multi-agent orchestrator
│   ├── workers.py         # Specialized worker agents
│   ├── metrics.py         # Prometheus metrics collector
│   ├── learning.py        # Bayesian calibration engine
│   └── llm_factory.py     # LLM provider factory
├── tests/                 # Test suite
├── web/                   # Web dashboard
├── cli.py                 # Enterprise CLI entry point
├── rcri_lee.py            # Core scoring module
├── enrichment.py          # Enrichment feature engines
├── simulator.py           # Load testing simulator
├── pyproject.toml         # Project metadata and dependencies
├── Dockerfile             # Container definition
└── docker-compose.yml     # Multi-service orchestration
```
