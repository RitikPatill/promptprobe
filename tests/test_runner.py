from unittest.mock import MagicMock, patch

import pytest

from promptprobe.schema import Suite, Case
from promptprobe.runner import LLMRunner, RunResult


def _make_suite(model: str, scorer: str = "exact") -> Suite:
    return Suite(
        name="test-suite",
        system_prompt="You are helpful.",
        model=model,
        scorer=scorer,
        cases=[Case(user="Hello", expected="hello", id="case_0")],
        temperature=0.0,
    )


# --- dispatch tests ---

def test_dispatch_anthropic():
    suite = _make_suite("claude-haiku-4-5-20251001")
    runner = LLMRunner(suite)
    with patch.object(runner, "_call_anthropic", return_value="hello") as mock_a, \
         patch.object(runner, "_call_openai", return_value="hello") as mock_b:
        runner._call_llm("Hello")
    mock_a.assert_called_once_with("Hello")
    mock_b.assert_not_called()


def test_dispatch_openai():
    suite = _make_suite("gpt-4o-mini")
    runner = LLMRunner(suite)
    with patch.object(runner, "_call_anthropic", return_value="hello") as mock_a, \
         patch.object(runner, "_call_openai", return_value="hello") as mock_b:
        runner._call_llm("Hello")
    mock_b.assert_called_once_with("Hello")
    mock_a.assert_not_called()


def test_dispatch_unknown():
    suite = _make_suite("gemini-pro")
    runner = LLMRunner(suite)
    with pytest.raises(ValueError, match="Unknown model prefix"):
        runner._call_llm("Hello")


# --- run() integration ---

def test_run_returns_runresults():
    suite = _make_suite("claude-haiku-4-5-20251001", scorer="exact")
    runner = LLMRunner(suite)
    with patch.object(runner, "_call_llm", return_value="hello"):
        results = runner.run()
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, RunResult)
    assert result.case_id == "case_0"
    assert result.user == "Hello"
    assert result.expected == "hello"
    assert result.response == "hello"
    assert result.passed is True
