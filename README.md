# Revised Cardiac Risk Index (RCRI / Lee Index)

A six-factor perioperative cardiac risk score for **noncardiac surgery**. The repository provides an offline browser calculator, a Python CLI, CSV batch scoring, and a FastAPI endpoint.

## Clinical basis

One point is assigned for each present factor:

1. High-risk surgery (intraperitoneal, intrathoracic, or suprainguinal vascular)
2. History of ischemic heart disease
3. History of congestive heart failure
4. History of cerebrovascular disease
5. Preoperative insulin treatment
6. Serum creatinine ≥ 2.0 mg/dL (threshold in the 2024 AHA/ACC guideline)

**RCRI = sum of these six Boolean predictors (0–6).** In the original 1999 *validation cohort*, the observed rates of major cardiac complications for scores 0, 1, 2, and ≥3 were **0.4%, 0.9%, 7%, and 11%**, respectively. The score categories are Class I (0), Class II (1), Class III (2), and Class IV (≥3). An RCRI of ≥2 is traditionally considered an elevated-risk score.

These are historical cohort observations, **not individualized or contemporary event probabilities**. The RCRI does not replace clinical assessment, procedure-specific risk tools, or current perioperative guidance.

References: [Lee et al., *Circulation*, 1999](https://pubmed.ncbi.nlm.nih.gov/10477528/) · [2024 AHA/ACC perioperative guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.06.013).

## Browser calculator

Open the configured GitHub Pages deployment, or serve the `web/` directory from a local HTTP server. Select the six predictors to calculate a score immediately. The static interface runs entirely in browser JavaScript, uses no external libraries, does not make requests to a clinical backend, and does not store selections. No Python-in-browser runtime is needed for this small deterministic calculation.

The browser calculator does **not** accept patient names, identifiers, or uploaded files.

For local browser use, run `python -m http.server 8000 -d web` and visit `http://localhost:8000/`. Opening the HTML directly via `file://` may be blocked by browsers' ES-module security restrictions.

## Python CLI and batch processing

Python 3.10 or newer:

~~~bash
python -m pip install -e ".[test]"
rcri-lee single --high-risk-surgery --heart-failure
rcri-lee batch -i sample.csv -o results.csv
python -m pytest -q
~~~

The single-case command treats omitted flags as absent. All **six** named columns must be supplied in batch CSV; accepted values are `true/false`, `yes/no`, or `1/0` (case-insensitive). Missing or invalid data is rejected rather than silently scored as zero. Scores, risk classes, category, and the original validation-cohort observed rate are appended to the CSV. Additional columns are carried through verbatim; do not upload or share CSV files containing identifiable patient information.

The primary Python API is `rcri_lee.calculate_metrics(**six_boolean_factors)`.

## Optional REST API and existing audit components

~~~bash
python cli.py serve --host 127.0.0.1 --port 8000
~~~

`POST /api/rcri` accepts JSON with all six Boolean fields, with extra fields rejected. OpenAPI documentation is available at `/docs` on the running server. These server endpoints are **not deployed to GitHub Pages**.

The pre-existing generic audit, worker, simulated chat, and enrichment interfaces are still available through `python cli.py` and `rcri-lee-audit`. They are **demonstration utilities, not RCRI prediction models or independently validated clinical decision systems**. In particular, the generic workers' thresholds are unrelated to the Lee Index. Do not interpret their alert tiers as perioperative risk advice.

The in-memory HMAC audit trail requires `AUDIT_SECRET_KEY` for a stable key; it does not provide persistent storage. The administrative `/api/audit/logs` endpoint additionally requires `AUDIT_ADMIN_KEY`, sent as the `X-Audit-Access-Key` header. The existing pattern-based identifier guard is not a comprehensive PHI-deidentification or HIPAA compliance mechanism. Avoid passing patient identifiers to any demonstration or audit endpoint. Keep server-side keys private.

## Local verification and container

~~~bash
python -m pytest -q
node --test web/app.test.mjs  # Node.js 22+
docker compose up --build    # Requires AUDIT_SECRET_KEY in the environment
~~~

CI runs Python tests on Python 3.10–3.12 and JavaScript unit tests on Node.js 22, then publishes the `web/` directory to GitHub Pages on successful `master` pushes when GitHub Pages is configured for GitHub Actions.

## Technology and compatibility

Python 3.10+, FastAPI, Pydantic v2, pytest, and vanilla HTML/CSS/JavaScript (ES modules). The static calculator works in current browsers with module support, including Chrome, Firefox, Safari, and Edge. Browser calculations and Python scoring require no network access. The static app does not persist data.

## License

MIT — see [LICENSE](LICENSE).
