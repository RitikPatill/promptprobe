from __future__ import annotations

import json


def load_report(path: str) -> dict:
    """Load a JSON report file. Raises FileNotFoundError or json.JSONDecodeError."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compare_reports(report_a: dict, report_b: dict) -> dict:
    """Compare two reports by case_id and classify each case.

    Returns a dict with keys:
        regressions  — cases that flipped True→False
        fixes        — cases that flipped False→True
        unchanged    — cases with the same pass/fail value in both reports
        only_in_a    — cases present only in report_a
        only_in_b    — cases present only in report_b
    """
    cases_a = {c["case_id"]: c for c in report_a.get("cases", [])}
    cases_b = {c["case_id"]: c for c in report_b.get("cases", [])}

    all_ids = set(cases_a) | set(cases_b)

    regressions: list[dict] = []
    fixes: list[dict] = []
    unchanged: list[dict] = []
    only_in_a: list[dict] = []
    only_in_b: list[dict] = []

    for cid in sorted(all_ids):
        in_a = cid in cases_a
        in_b = cid in cases_b

        if in_a and not in_b:
            only_in_a.append({"case_id": cid, **cases_a[cid]})
            continue
        if in_b and not in_a:
            only_in_b.append({"case_id": cid, **cases_b[cid]})
            continue

        ca = cases_a[cid]
        cb = cases_b[cid]
        passed_a = ca.get("passed", False)
        passed_b = cb.get("passed", False)

        entry = {
            "case_id": cid,
            "user": ca.get("user", ""),
            "expected": ca.get("expected", ""),
            "response_a": ca.get("response", ""),
            "response_b": cb.get("response", ""),
        }

        if passed_a and not passed_b:
            regressions.append(entry)
        elif not passed_a and passed_b:
            fixes.append(entry)
        else:
            unchanged.append({"case_id": cid, "passed": passed_a})

    return {
        "regressions": regressions,
        "fixes": fixes,
        "unchanged": unchanged,
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
    }
