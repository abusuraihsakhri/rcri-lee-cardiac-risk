"""Clinically consequential edge cases for RCRI scoring."""
import csv
import itertools

import pytest

from rcri_lee import FACTORS, calculate_metrics, process_batch


def factors_with(n):
    return {factor: i < n for i, factor in enumerate(FACTORS)}


@pytest.mark.parametrize("score,risk_class,rate", [
    (0, "Class I", 0.4),
    (1, "Class II", 0.9),
    (2, "Class III", 7.0),
    (3, "Class IV", 11.0),
    (4, "Class IV", 11.0),
    (5, "Class IV", 11.0),
    (6, "Class IV", 11.0),
])
def test_rcri_levels(score, risk_class, rate):
    result = calculate_metrics(**factors_with(score))
    assert result["score"] == score
    assert result["classification"] == risk_class
    assert result["validation_event_rate_percent"] == rate
    assert result["risk_category"] == ("Elevated" if score >= 2 else "Low")


def test_all_64_combinations():
    for combination in itertools.product([False, True], repeat=6):
        result = calculate_metrics(**dict(zip(FACTORS, combination)))
        assert result["score"] == sum(combination)


@pytest.mark.parametrize("invalid", [None, "", "false", "0", 0, 1, -1, 2, float("nan"), float("inf")])
def test_non_boolean_rejected(invalid):
    data = factors_with(0)
    data["heart_failure"] = invalid
    with pytest.raises(ValueError, match="Boolean"):
        calculate_metrics(**data)


def test_missing_and_unexpected_rejected():
    with pytest.raises(ValueError, match="missing"):
        calculate_metrics()
    with pytest.raises(ValueError, match="unknown"):
        calculate_metrics(**factors_with(0), patient_name="private")


def test_batch_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_batch(str(tmp_path / "no-file.csv"), str(tmp_path / "out.csv"))


def test_batch_rejects_invalid_values_without_output(tmp_path):
    src, dst = tmp_path / "input.csv", tmp_path / "output.csv"
    src.write_text(",".join(FACTORS) + "\n" + ",".join([""] * 6) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="row 2"):
        process_batch(str(src), str(dst))
    assert not dst.exists()


def test_batch_rejects_missing_header(tmp_path):
    src, dst = tmp_path / "input.csv", tmp_path / "output.csv"
    src.write_text("high_risk_surgery\ntrue\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required"):
        process_batch(str(src), str(dst))


def test_batch_rejects_input_overwrite(tmp_path):
    src = tmp_path / "input.csv"
    src.write_text(",".join(FACTORS) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="overwrite"):
        process_batch(str(src), str(src))
