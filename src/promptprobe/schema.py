from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


VALID_SCORERS = {"exact", "contains", "llm_judge"}


class SuiteValidationError(ValueError):
    pass


@dataclass
class Case:
    user: str
    expected: str
    id: str = ""


@dataclass
class Suite:
    name: str
    system_prompt: str
    model: str
    scorer: str
    cases: list[Case]
    temperature: float = 0.0


def load_suite(path: str | Path) -> Suite:
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise SuiteValidationError(f"Invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise SuiteValidationError("Invalid YAML: expected a mapping at the top level")

    for key in ("name", "system_prompt", "model", "scorer", "cases"):
        if key not in data:
            raise SuiteValidationError(f"Missing required field: {key}")

    scorer = data["scorer"]
    if scorer not in VALID_SCORERS:
        raise SuiteValidationError(
            f"Unknown scorer '{scorer}'. Valid: exact, contains, llm_judge"
        )

    cases_raw = data["cases"]
    if not isinstance(cases_raw, list) or len(cases_raw) == 0:
        raise SuiteValidationError("'cases' must be a non-empty list")

    cases: list[Case] = []
    for i, case_dict in enumerate(cases_raw):
        if not isinstance(case_dict, dict):
            raise SuiteValidationError(f"cases[{i}]: expected a mapping")
        for key in ("user", "expected"):
            if key not in case_dict:
                raise SuiteValidationError(f"cases[{i}]: missing field '{key}'")
        case_id = case_dict.get("id", "") or f"case_{i}"
        cases.append(Case(user=case_dict["user"], expected=case_dict["expected"], id=case_id))

    return Suite(
        name=data["name"],
        system_prompt=data["system_prompt"],
        model=data["model"],
        scorer=scorer,
        cases=cases,
        temperature=float(data.get("temperature", 0.0)),
    )
