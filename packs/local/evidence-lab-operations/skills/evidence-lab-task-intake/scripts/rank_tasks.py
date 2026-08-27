#!/usr/bin/env python3
"""Deterministically score and rank executable Evidence Lab tasks.

Input is a JSON array of task objects. The script does not write to Notion.
It returns gate failures, a score breakdown, and a per-owner execution rank.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


PRIORITY_POINTS = {"P0": 60, "P1": 30, "P2": 0}
SIZE_POINTS = {"XS": 12, "S": 9, "M": 4, "L": 0}
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3}


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise ValueError(f"invalid ISO date: {value}") from exc


def due_points(due: date | None, today: date) -> tuple[int, str]:
    if due is None:
        return 0, "no due date"
    days = (due - today).days
    if days < 0:
        return 20, f"overdue {-days}d"
    if days <= 1:
        return 20, f"due in {days}d"
    if days <= 3:
        return 15, f"due in {days}d"
    if days <= 7:
        return 10, f"due in {days}d"
    if days <= 14:
        return 5, f"due in {days}d"
    return 0, f"due in {days}d"


def gate_failures(task: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {
        "title": "title",
        "owner": "owner",
        "executors": "executor",
        "reviewer": "reviewer",
        "product_contour": "product contour",
        "result": "result",
        "acceptance_criteria": "acceptance criteria",
        "source": "source",
        "priority": "priority",
        "impact": "impact",
        "urgency": "urgency",
        "size": "size",
    }
    for key, label in required.items():
        if task.get(key) in (None, "", []):
            failures.append(f"missing {label}")
    if task.get("project") in (None, "", []) and task.get("initiative") in (None, "", []):
        failures.append("missing active project or initiative")
    if task.get("status") == "Done":
        failures.append("already done")
    if task.get("blocked") or task.get("board_column") == "Blocked" or int(task.get("open_dependencies", 0) or 0) > 0:
        failures.append("blocked")
    if task.get("is_container"):
        failures.append("container is not executable")
    if task.get("project_active") is False:
        failures.append("project or initiative is not active")
    if task.get("priority") == "P0" and not task.get("p0_failure_sentence"):
        failures.append("P0 has no failure sentence")
    return failures


def evaluate(task: dict[str, Any], today: date) -> dict[str, Any]:
    failures = gate_failures(task)
    priority = str(task.get("priority", ""))
    size = str(task.get("size", ""))
    impact = int(task.get("impact", 0) or 0)
    urgency = int(task.get("urgency", 0) or 0)
    if priority and priority not in PRIORITY_POINTS:
        failures.append(f"unsupported priority {priority}")
    if size and size not in SIZE_POINTS:
        failures.append(f"unsupported size {size}")
    if impact and not 1 <= impact <= 5:
        failures.append("impact must be 1..5")
    if urgency and not 1 <= urgency <= 5:
        failures.append("urgency must be 1..5")

    due, due_note = due_points(parse_date(task.get("due")), today)
    breakdown = {
        "pilot": 100 if task.get("pilot_gate") else 0,
        "priority": PRIORITY_POINTS.get(priority, 0),
        "impact": impact * 10,
        "urgency": urgency * 6,
        "unblocks": min(int(task.get("active_dependents", 0) or 0), 3) * 8,
        "due": due,
        "size": SIZE_POINTS.get(size, 0),
        "in_progress": 25 if task.get("status") == "In progress" else 0,
    }
    return {
        **task,
        "ready": not failures,
        "gate_failures": failures,
        "priority_score": sum(breakdown.values()),
        "score_breakdown": breakdown,
        "due_note": due_note,
        "owner_rank": None,
    }


def rank(tasks: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    rows = [evaluate(task, today) for task in tasks]
    owners = sorted({str(row.get("owner")) for row in rows if row.get("owner")})
    for owner in owners:
        ready = [row for row in rows if row.get("owner") == owner and row["ready"]]
        ready.sort(
            key=lambda row: (
                -row["priority_score"],
                parse_date(row.get("due")) or date.max,
                SIZE_ORDER.get(str(row.get("size")), 99),
                str(row.get("created_at", "")),
                str(row.get("title", "")),
            )
        )
        for index, row in enumerate(ready, start=1):
            row["owner_rank"] = index * 10
    rows.sort(
        key=lambda row: (
            str(row.get("owner", "")),
            row["owner_rank"] is None,
            row["owner_rank"] or 10**9,
            str(row.get("title", "")),
        )
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON array of task objects")
    parser.add_argument("--today", help="ISO date used for deterministic due-date scoring")
    parser.add_argument("--out", default="-", help="output path or '-' for stdout")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("input must be a JSON array")
    today = parse_date(args.today) if args.today else date.today()
    result = rank(payload, today or date.today())
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out == "-":
        print(rendered, end="")
    else:
        Path(args.out).write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
