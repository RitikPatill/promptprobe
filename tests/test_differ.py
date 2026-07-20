import json
import pytest

from promptprobe.differ import load_report, compare_reports


def _report(*cases):
    """Build a minimal report dict from (case_id, passed) tuples."""
    return {
        "suite": "test",
        "cases": [
            {
                "case_id": cid,
                "user": f"user {cid}",
                "expected": "expected",
                "response": "response",
                "passed": passed,
                "score_detail": "",
            }
            for cid, passed in cases
        ],
    }


def test_no_flips():
    a = _report(("c1", True), ("c2", False))
    b = _report(("c1", True), ("c2", False))
    result = compare_reports(a, b)
    assert result["regressions"] == []
    assert result["fixes"] == []
    assert len(result["unchanged"]) == 2


def test_regression():
    a = _report(("c1", True))
    b = _report(("c1", False))
    result = compare_reports(a, b)
    assert len(result["regressions"]) == 1
    assert result["regressions"][0]["case_id"] == "c1"
    assert result["fixes"] == []


def test_fix():
    a = _report(("c1", False))
    b = _report(("c1", True))
    result = compare_reports(a, b)
    assert len(result["fixes"]) == 1
    assert result["fixes"][0]["case_id"] == "c1"
    assert result["regressions"] == []


def test_mixed():
    a = _report(("c1", True), ("c2", False), ("c3", True))
    b = _report(("c1", False), ("c2", True), ("c3", True))
    result = compare_reports(a, b)
    assert len(result["regressions"]) == 1
    assert result["regressions"][0]["case_id"] == "c1"
    assert len(result["fixes"]) == 1
    assert result["fixes"][0]["case_id"] == "c2"
    assert len(result["unchanged"]) == 1
    assert result["unchanged"][0]["case_id"] == "c3"


def test_only_in_a():
    a = _report(("c1", True), ("c2", True))
    b = _report(("c1", True))
    result = compare_reports(a, b)
    assert len(result["only_in_a"]) == 1
    assert result["only_in_a"][0]["case_id"] == "c2"
    assert result["regressions"] == []
    assert result["fixes"] == []


def test_only_in_b():
    a = _report(("c1", True))
    b = _report(("c1", True), ("c2", False))
    result = compare_reports(a, b)
    assert len(result["only_in_b"]) == 1
    assert result["only_in_b"][0]["case_id"] == "c2"


def test_load_report_missing_file():
    with pytest.raises(FileNotFoundError):
        load_report("/nonexistent/path/does_not_exist.json")


def test_load_report_reads_json(tmp_path):
    data = {"suite": "s", "cases": []}
    p = tmp_path / "run.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    result = load_report(str(p))
    assert result["suite"] == "s"
