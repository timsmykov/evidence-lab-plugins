#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path


MODULE = Path(__file__).with_name("rank_tasks.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("rank_tasks", MODULE)
assert SPEC and SPEC.loader
rank_tasks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rank_tasks)


def task(title: str, **overrides):
    base = {
        "title": title,
        "owner": "Tim",
        "executors": ["Tim"],
        "reviewer": "Misha",
        "project": "Evidence Lab",
        "product_contour": ["Skill Pack"],
        "project_active": True,
        "result": "Verified artifact",
        "acceptance_criteria": "Artifact is linked and reviewed",
        "source": "request://example",
        "priority": "P1",
        "impact": 3,
        "urgency": 2,
        "size": "M",
        "status": "To Do",
        "open_dependencies": 0,
    }
    base.update(overrides)
    return base


def main() -> int:
    today = date(2026, 8, 27)
    rows = rank_tasks.rank(
        [
            task("Strategic", priority="P0", impact=5, urgency=3, p0_failure_sentence="Without it, the release cannot ship."),
            task("Quick", priority="P2", impact=2, urgency=1, size="XS"),
            task("Blocked", pilot_gate=True, open_dependencies=1),
            task("No executor", executors=[]),
            task("Other owner", owner="Misha", reviewer="Tim", impact=4),
        ],
        today,
    )
    by_title = {row["title"]: row for row in rows}
    assert by_title["Strategic"]["owner_rank"] == 10
    assert by_title["Quick"]["owner_rank"] == 20
    assert by_title["Blocked"]["owner_rank"] is None
    assert not by_title["Blocked"]["ready"]
    assert by_title["No executor"]["owner_rank"] is None
    assert "missing executor" in by_title["No executor"]["gate_failures"]
    assert by_title["Other owner"]["owner_rank"] == 10
    assert by_title["Strategic"]["priority_score"] > by_title["Quick"]["priority_score"]
    print("PASS: Evidence Lab task gates, scoring, and per-owner ranking")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
