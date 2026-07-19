from __future__ import annotations

import json
import re


def score_exact(response: str, expected: str) -> tuple[bool, str]:
    """Case-insensitive full-string match."""
    passed = response.strip().lower() == expected.strip().lower()
    return passed, "exact match" if passed else "no exact match"


def score_contains(response: str, expected: str) -> tuple[bool, str]:
    """All comma-separated keywords in expected must appear (case-insensitive) in response."""
    keywords = [kw.strip() for kw in expected.split(",")]
    missing = [kw for kw in keywords if kw.lower() not in response.lower()]
    if missing:
        return False, f"missing: {missing}"
    return True, "all keywords present"


def score_llm_judge(
    response: str, expected: str, model: str = "claude-haiku-4-5-20251001"
) -> tuple[bool, str]:
    """Secondary Claude call. Rates response 1-5 against rubric. Pass if >= 3."""
    import anthropic

    system = (
        "You are an evaluator. Rate the following response on a scale of 1-5 against the rubric. "
        'Respond with ONLY a JSON object: {"score": <int>, "reason": "<one sentence>"}'
    )
    user = f"Rubric: {expected}\nResponse to evaluate: {response}"

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = message.content[0].text

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return False, "judge parse error"
    try:
        data = json.loads(match.group())
        score = int(data["score"])
        reason = data.get("reason", "")
        passed = score >= 3
        return passed, f"llm_judge: {score}/5 — {reason}"
    except (json.JSONDecodeError, KeyError, ValueError):
        return False, "judge parse error"
