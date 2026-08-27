#!/usr/bin/env python3
"""Build the deterministic scenario-to-pack capability boundary report."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "catalog" / "scenarios.json"
DECISIONS = ROOT / "catalog" / "pack-boundary-decisions.json"
CATALOG = ROOT / "packs" / "core" / "evidence-lab-core" / "catalog" / "packs.json"
POLICY = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding" / "selection-policy.json"
SELECTOR = ROOT / "packs" / "core" / "evidence-lab-core" / "skills" / "evidence-lab-onboarding" / "scripts" / "select_packs.py"
DEFAULT_OUTPUT = ROOT / "docs" / "pack-boundary-report.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_selector():
    spec = importlib.util.spec_from_file_location("evidence_lab_selector", SELECTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SELECTOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def analyze(matrix: dict, catalog: dict, policy: dict) -> dict:
    selector = load_selector()
    packs = {pack["id"]: pack for pack in catalog["packs"]}
    baseline = matrix["baseline_pack"]
    baseline_capabilities = set(packs[baseline]["capabilities"])
    rows = []
    usage = {pack_id: {"selected_by": [], "excluded_by": []} for pack_id in packs}
    for scenario in matrix["scenarios"]:
        plan = selector.select(scenario["profile"], catalog, policy)
        installed = [pack["id"] for pack in plan["packs"]]
        selected = [
            pack["id"]
            for pack in plan["packs"]
            if pack["id"] == baseline or any(rule_id != "required-foundation" for rule_id in pack["rule_ids"])
        ]
        provided = set().union(*(set(packs[pack_id]["capabilities"]) for pack_id in selected))
        required = set(scenario["required_capabilities"])
        optional = set(scenario["optional_capabilities"])
        missing = sorted(required - provided)
        extra = sorted(
            capability for capability in provided - required - optional - baseline_capabilities
            if not capability.endswith("-compatibility")
        )
        for pack_id in packs:
            usage[pack_id]["selected_by" if pack_id in selected else "excluded_by"].append(scenario["id"])
        rows.append({
            "id": scenario["id"],
            "segment": scenario["segment"],
            "installed_packs": installed,
            "selected_packs": selected,
            "missing_capabilities": missing,
            "overinstalled_capabilities": extra,
        })
    return {
        "schema_version": 1,
        "scenario_count": len(rows),
        "missing_occurrences": sum(len(row["missing_capabilities"]) for row in rows),
        "overinstalled_occurrences": sum(len(row["overinstalled_capabilities"]) for row in rows),
        "scenarios": rows,
        "pack_usage": usage,
    }


def cell(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "—"


def render(report: dict, decisions: dict) -> str:
    lines = [
        "# Pack-boundary evidence report",
        "",
        "Generated deterministically by `python3 scripts/analyze_pack_boundaries.py`.",
        f"It measures the current catalog with R3 boundary status `{decisions['status']}`.",
        "Bootstrap installs the frozen foundation for every profile. The scenario matrix shows profile-relevant pack activation rules, so the boundary evidence remains useful after physical installation is broadened.",
        "Core capabilities are treated as the mandatory baseline and are not counted as over-installation.",
        "",
        "## Summary",
        "",
        f"- Scenarios: **{report['scenario_count']}**",
        f"- Missing required capability occurrences: **{report['missing_occurrences']}**",
        f"- Over-installed optional-pack capability occurrences: **{report['overinstalled_occurrences']}**",
        "",
        "## Scenario matrix",
        "",
        "| Scenario | Selected packs | Missing required capabilities | Over-installed capabilities |",
        "|---|---|---|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| `{row['id']}` | {cell(row['selected_packs'])} | "
            f"{cell(row['missing_capabilities'])} | {cell(row['overinstalled_capabilities'])} |"
        )

    lines.extend(["", "## Current pack coverage", ""])
    for pack_id, usage in report["pack_usage"].items():
        if usage["excluded_by"]:
            negative = f"negative scenarios include `{usage['excluded_by'][0]}`"
        else:
            negative = "mandatory baseline; exclusion is intentionally not applicable"
        lines.append(f"- `{pack_id}`: selected by {len(usage['selected_by'])} scenario(s); {negative}.")

    lines.extend(["", "## Split or keep decisions", ""])
    for decision in decisions["current_pack_decisions"]:
        lines.extend([
            f"### `{decision['pack_id']}` — {decision['decision'].upper()}",
            "",
            decision["rationale"],
            "",
            f"Target boundary: {decision['target_boundary']}",
            "",
            f"Evidence: {cell(decision['scenario_evidence'])}.",
            "",
        ])

    lines.extend([
        "## Prioritized additions",
        "",
        "| Priority | Pack | Target capabilities | Lifecycle | Scenario evidence |",
        "|---|---|---|---|---|",
    ])
    for addition in decisions["prioritized_additions"]:
        lines.append(
            f"| {addition['priority']} | `{addition['pack_id']}` | {cell(addition['capabilities'])} | "
            f"`{addition['lifecycle_status']}` | "
            f"{cell(addition['trigger_scenarios'])} |"
        )
    lines.extend([
        "",
        "Each pack is tied to a repeatable workflow or material boundary across the listed scenarios, not merely to a discipline label.",
        "Draft additions have passed repository behavior checks but still require representative research runs and independent review before `production`.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(analyze(load(SCENARIOS), load(CATALOG), load(POLICY)), load(DECISIONS))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"FAIL: generated report is stale: {args.output.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"verified {args.output.relative_to(ROOT)}")
        return 0
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
