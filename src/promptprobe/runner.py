from __future__ import annotations

from dataclasses import dataclass

from .schema import Suite
from .scorers import score_exact, score_contains, score_llm_judge


@dataclass
class RunResult:
    case_id: str
    user: str
    expected: str
    response: str
    passed: bool
    score_detail: str


_SCORER_MAP = {
    "exact": score_exact,
    "contains": score_contains,
    "llm_judge": score_llm_judge,
}


class LLMRunner:
    def __init__(self, suite: Suite) -> None:
        self.suite = suite

    def run(self) -> list[RunResult]:
        results: list[RunResult] = []
        scorer_fn = _SCORER_MAP[self.suite.scorer]
        for case in self.suite.cases:
            response = self._call_llm(case.user)
            if self.suite.scorer == "llm_judge":
                passed, detail = scorer_fn(response, case.expected, model=self.suite.model)
            else:
                passed, detail = scorer_fn(response, case.expected)
            results.append(
                RunResult(
                    case_id=case.id,
                    user=case.user,
                    expected=case.expected,
                    response=response,
                    passed=passed,
                    score_detail=detail,
                )
            )
        return results

    def _call_llm(self, user_message: str) -> str:
        model = self.suite.model
        if model.startswith("claude"):
            return self._call_anthropic(user_message)
        elif model.startswith("gpt"):
            return self._call_openai(user_message)
        else:
            raise ValueError(f"Unknown model prefix for '{model}'. Supported: claude*, gpt*")

    def _call_anthropic(self, user_message: str) -> str:
        import anthropic

        client = anthropic.Anthropic()
        message = client.messages.create(
            model=self.suite.model,
            max_tokens=1024,
            system=self.suite.system_prompt,
            temperature=self.suite.temperature,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text

    def _call_openai(self, user_message: str) -> str:
        import openai

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=self.suite.model,
            max_tokens=1024,
            temperature=self.suite.temperature,
            messages=[
                {"role": "system", "content": self.suite.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
