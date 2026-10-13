import csv
import json

from rcri_lee import FACTORS, calculate_metrics, main, process_batch


def test_all_six_rcri_factors():
    for selected in FACTORS:
        values = {factor: factor == selected for factor in FACTORS}
        result = calculate_metrics(**values)
        assert result["score"] == 1
        assert result["classification"] == "Class II"
        assert result["validation_event_rate_percent"] == 0.9


def test_cli_single(capsys):
    main(["single", "--high-risk-surgery", "--heart-failure"])
    result = json.loads(capsys.readouterr().out)
    assert result["score"] == 2
    assert result["risk_category"] == "Elevated"


def test_batch_csv(tmp_path):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    rows = [
        {"case": "case-1", **{key: "0" for key in FACTORS}},
        {"case": "case-2", **{key: "YES" for key in FACTORS}},
    ]
    with input_path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=["case", *FACTORS])
        writer.writeheader()
        writer.writerows(rows)
    process_batch(str(input_path), str(output_path))
    with output_path.open(encoding="utf-8", newline="") as inp:
        output = list(csv.DictReader(inp))
    assert [row["score"] for row in output] == ["0", "6"]
    assert [row["classification"] for row in output] == ["Class I", "Class IV"]
