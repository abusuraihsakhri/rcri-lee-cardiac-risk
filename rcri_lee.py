#!/usr/bin/env python3
"""Revised Cardiac Risk Index (Lee Index) for noncardiac surgery.

Six binary predictors, one point each. Validation-cohort rates are descriptive,
not patient-specific probabilities; see Lee et al., Circulation 1999.
"""
import argparse
import csv
import json
from pathlib import Path

FACTORS = (
    "high_risk_surgery",
    "ischemic_heart_disease",
    "heart_failure",
    "cerebrovascular_disease",
    "insulin_treatment",
    "creatinine_ge_2",
)
LABELS = {
    "high_risk_surgery": "High-risk noncardiac surgery",
    "ischemic_heart_disease": "History of ischemic heart disease",
    "heart_failure": "History of congestive heart failure",
    "cerebrovascular_disease": "History of cerebrovascular disease",
    "insulin_treatment": "Preoperative insulin treatment",
    "creatinine_ge_2": "Serum creatinine >= 2.0 mg/dL",
}
# Observed major cardiac complication rates in the original VALIDATION cohort;
# 3, 4, 5 and 6 predictors share the >=3 category.
VALIDATION_RATES = (0.4, 0.9, 7.0, 11.0)


def calculate_metrics(**kwargs):
    """Calculate an integer RCRI (0–6) from exactly the six Boolean predictors.

    Missing factors are errors; unknown factors and coercion of strings or
    numeric values are prohibited to avoid silently misclassifying patients.
    """
    missing = [factor for factor in FACTORS if factor not in kwargs]
    unknown = [key for key in kwargs if key not in FACTORS]
    if missing or unknown:
        raise ValueError(f"Invalid RCRI inputs; missing={missing}, unknown={unknown}")
    for factor in FACTORS:
        if type(kwargs[factor]) is not bool:
            raise ValueError(f"{factor} must be a Boolean (True or False)")
    score = sum(kwargs[factor] for factor in FACTORS)
    category = min(score, 3)
    return {
        "tool": "rcri-lee-cardiac-risk",
        "score": score,
        "classification": ("Class I", "Class II", "Class III", "Class IV")[category],
        "risk_category": "Elevated" if score >= 2 else "Low",
        "validation_event_rate_percent": VALIDATION_RATES[category],
        "event_rate_context": "Original Lee 1999 validation cohort; not an individualized prediction.",
        "positive_predictors": [LABELS[factor] for factor in FACTORS if kwargs[factor]],
        "inputs_evaluated": len(FACTORS),
    }


def _parse_bool(value, field, row_number):
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"CSV row {row_number}: {field} must be true/false, yes/no or 1/0")


def process_single(args):
    data = {key: getattr(args, key) for key in FACTORS}
    print(json.dumps(calculate_metrics(**data), indent=2))


def process_batch(input_csv, output_csv):
    """Evaluate CSV records; reject incomplete rows before writing output."""
    source = Path(input_csv)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")
    if source.resolve() == Path(output_csv).resolve():
        raise ValueError("Output CSV must not overwrite the input CSV")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError("Duplicate CSV column names are not supported")
        missing = [factor for factor in FACTORS if factor not in fields]
        if missing:
            raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")
        out_fields = ("score", "classification", "risk_category", "validation_event_rate_percent")
        collisions = [field for field in out_fields if field in fields]
        if collisions:
            raise ValueError(f"Output fields already exist: {', '.join(collisions)}")
        rows = []
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {row_number} has more fields than the header")
            values = {factor: _parse_bool(row[factor], factor, row_number) for factor in FACTORS}
            result = calculate_metrics(**values)
            rows.append({**row, **{field: result[field] for field in out_fields}})
    with open(output_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*fields, *out_fields])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Processed {len(rows)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Revised Cardiac Risk Index (RCRI)")
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("single", help="Score one case (omitted flags are False)")
    for factor in FACTORS:
        single.add_argument("--" + factor.replace("_", "-"), action="store_true", help=LABELS[factor])
    batch = commands.add_parser("batch", help="Score a CSV with six Boolean columns")
    batch.add_argument("-i", "--input", required=True, help="Input CSV file")
    batch.add_argument("-o", "--output", default="results.csv", help="Output CSV file")
    args = parser.parse_args(argv)
    if args.command == "single":
        process_single(args)
    else:
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
