from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from promptprobe.cli import app
from promptprobe.runner import RunResult
from promptprobe.schema import Suite, Case

runner = CliRunner()


def _make_suite():
    return Suite(
        name="my-suite",
        system_prompt="You are helpful.",
        model="claude-haiku-4-5-20251001",
        scorer="exact",
        cases=[Case(user="Hello", expected="hello", id="case_0")],
        temperature=0.0,
    )


def _make_result(passed: bool) -> RunResult:
    return RunResult(
        case_id="case_0",
        user="Hello",
        expected="hello",
        response="hello" if passed else "nope",
        passed=passed,
        score_detail="exact match" if passed else "no match",
    )


@patch("promptprobe.cli.write_report", return_value="results/run_x.json")
@patch("promptprobe.cli.LLMRunner")
@patch("promptprobe.cli.load_suite")
def test_eval_all_pass(mock_load, mock_runner_cls, mock_write):
    mock_load.return_value = _make_suite()
    mock_runner_cls.return_value.run.return_value = [_make_result(True)]

    result = runner.invoke(app, ["eval", "suite.yaml"])

    assert result.exit_code == 0
    assert "PASS" in result.output


@patch("promptprobe.cli.write_report", return_value="results/run_x.json")
@patch("promptprobe.cli.LLMRunner")
@patch("promptprobe.cli.load_suite")
def test_eval_any_fail(mock_load, mock_runner_cls, mock_write):
    mock_load.return_value = _make_suite()
    mock_runner_cls.return_value.run.return_value = [_make_result(False)]

    result = runner.invoke(app, ["eval", "suite.yaml"])

    assert result.exit_code == 1
    assert "FAIL" in result.output


@patch("promptprobe.cli.write_report", return_value="results/run_x.json")
@patch("promptprobe.cli.LLMRunner")
@patch("promptprobe.cli.load_suite")
def test_eval_summary_present(mock_load, mock_runner_cls, mock_write):
    mock_load.return_value = _make_suite()
    mock_runner_cls.return_value.run.return_value = [_make_result(True)]

    result = runner.invoke(app, ["eval", "suite.yaml"])

    assert "passed" in result.output
    assert "%" in result.output


@patch("promptprobe.cli.write_report", return_value="results/run_x.json")
@patch("promptprobe.cli.LLMRunner")
@patch("promptprobe.cli.load_suite")
def test_eval_writes_report(mock_load, mock_runner_cls, mock_write):
    mock_load.return_value = _make_suite()
    mock_runner_cls.return_value.run.return_value = [_make_result(True)]

    runner.invoke(app, ["eval", "suite.yaml"])

    mock_write.assert_called_once()


def test_list_missing_dir():
    result = runner.invoke(app, ["list", "/nonexistent/path/xyz"])
    assert result.exit_code == 1
    assert "No results directory" in result.output


def test_list_shows_filenames(tmp_path):
    (tmp_path / "run_001.json").write_text("{}")
    (tmp_path / "run_002.json").write_text("{}")

    result = runner.invoke(app, ["list", str(tmp_path)])

    assert result.exit_code == 0
    assert "run_001.json" in result.output
    assert "run_002.json" in result.output


import json as _json


def _write_report(path, cases):
    """Write a minimal JSON report to path. cases: list of (case_id, passed)."""
    data = {
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
    path.write_text(_json.dumps(data), encoding="utf-8")
    return path


def test_diff_no_regressions_exits_zero(tmp_path):
    a = _write_report(tmp_path / "a.json", [("c1", True), ("c2", False)])
    b = _write_report(tmp_path / "b.json", [("c1", True), ("c2", True)])

    result = runner.invoke(app, ["diff", str(a), str(b)])

    assert result.exit_code == 0
    assert "regression(s)" in result.output


def test_diff_regressions_exits_one(tmp_path):
    a = _write_report(tmp_path / "a.json", [("c1", True)])
    b = _write_report(tmp_path / "b.json", [("c1", False)])

    result = runner.invoke(app, ["diff", str(a), str(b)])

    assert result.exit_code == 1
    assert "PASS→FAIL" in result.output


def test_diff_missing_file_exits_nonzero(tmp_path):
    real = _write_report(tmp_path / "a.json", [("c1", True)])

    result = runner.invoke(app, ["diff", str(real), str(tmp_path / "missing.json")])

    assert result.exit_code == 1
