"""
Edge case and input validation tests for rcri-lee-cardiac-risk.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import math
from rcri_lee import calculate_metrics, process_batch


def test_calculate_metrics_with_nan():
    """NaN values should be treated as non-numeric and not affect score."""
    res = calculate_metrics(v1=float('nan'), v2=5.0)
    assert "score" in res
    assert math.isfinite(res["score"])


def test_calculate_metrics_with_inf():
    """Infinity values should be treated as non-numeric."""
    res = calculate_metrics(v1=float('inf'), v2=5.0)
    assert "score" in res
    assert math.isfinite(res["score"])


def test_calculate_metrics_with_negative_inf():
    """Negative infinity values should be treated as non-numeric."""
    res = calculate_metrics(v1=float('-inf'), v2=5.0)
    assert "score" in res
    assert math.isfinite(res["score"])


def test_calculate_metrics_with_no_numeric():
    """When no numeric values provided, should use default 1.0."""
    res = calculate_metrics(a="hello", b="world")
    assert res["score"] == 1.0
    assert res["classification"] == "Low / Standard"


def test_calculate_metrics_with_none_values():
    """None values should be ignored."""
    res = calculate_metrics(v1=None, v2=5.0)
    assert res["score"] == 5.0


def test_calculate_metrics_empty():
    """Empty call should return default score."""
    res = calculate_metrics()
    assert res["score"] == 1.0
    assert res["inputs_evaluated"] == 0


def test_process_batch_file_not_found():
    """Should raise FileNotFoundError for missing input file."""
    with pytest.raises(FileNotFoundError):
        process_batch("nonexistent_file.csv", "output.csv")


def test_process_batch_with_nan_in_csv(tmp_path):
    """CSV with NaN values should handle gracefully."""
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,nan,3.0\nPat_002,5.0,inf\n", encoding="utf-8")

    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content


def test_calculate_metrics_classification_tiers():
    """Test all three classification tiers."""
    low = calculate_metrics(v1=5.0)
    assert low["classification"] == "Low / Standard"

    mid = calculate_metrics(v1=15.0)
    assert mid["classification"] == "Moderate / Intermediate"

    high = calculate_metrics(v1=30.0)
    assert high["classification"] == "High / Severe"


def test_calculate_metrics_with_string_numeric():
    """String representations of numbers should be parsed."""
    res = calculate_metrics(v1="12.5", v2="3.5")
    assert res["score"] > 0
    assert math.isfinite(res["score"])
