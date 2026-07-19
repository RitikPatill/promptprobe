from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from pathlib import Path

from .runner import RunResult


def write_report(
    suite_name: str,
    results: list[RunResult],
    output_dir: str = "results",
    model: str = "",
) -> str:
    """Writes results/run_<timestamp>.json. Returns the file path."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow()
    filename = f"run_{now.strftime('%Y%m%d_%H%M%S')}.json"
    filepath = out / filename

    pass_count = sum(r.passed for r in results)
    total = len(results)
    score_pct = round(pass_count / total * 100, 1) if total else 0.0

    report = {
        "suite": suite_name,
        "timestamp": now.isoformat(),
        "model": model,
        "pass_count": pass_count,
        "total": total,
        "score_pct": score_pct,
        "cases": [dataclasses.asdict(r) for r in results],
    }

    filepath.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(filepath)
