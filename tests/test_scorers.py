from unittest.mock import MagicMock, patch

from promptprobe.scorers import score_exact, score_contains, score_llm_judge


# --- score_exact ---

def test_exact_pass():
    passed, detail = score_exact("Hello World", "hello world")
    assert passed is True
    assert "exact match" in detail


def test_exact_fail():
    passed, detail = score_exact("Hello World", "Goodbye")
    assert passed is False


# --- score_contains ---

def test_contains_all_present():
    passed, detail = score_contains("The sky is blue and clear", "blue, clear")
    assert passed is True


def test_contains_partial():
    passed, detail = score_contains("The sky is blue", "blue, clear")
    assert passed is False
    assert "clear" in detail


def test_contains_multi_keyword():
    passed, detail = score_contains("bonjour le monde", "bonjour, monde")
    assert passed is True


# --- score_llm_judge ---

def _make_anthropic_mock(text: str):
    """Return a mock anthropic.Anthropic() whose messages.create returns the given text."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=text)]
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_llm_judge_pass():
    mock_client = _make_anthropic_mock('{"score": 4, "reason": "good"}')
    with patch("anthropic.Anthropic", return_value=mock_client):
        passed, detail = score_llm_judge("Great response", "Be helpful")
    assert passed is True
    assert "4/5" in detail


def test_llm_judge_fail():
    mock_client = _make_anthropic_mock('{"score": 2, "reason": "bad"}')
    with patch("anthropic.Anthropic", return_value=mock_client):
        passed, detail = score_llm_judge("Poor response", "Be helpful")
    assert passed is False
    assert "2/5" in detail


def test_llm_judge_parse_error():
    mock_client = _make_anthropic_mock("I cannot evaluate this.")
    with patch("anthropic.Anthropic", return_value=mock_client):
        passed, detail = score_llm_judge("Some response", "Some rubric")
    assert passed is False
    assert detail == "judge parse error"
