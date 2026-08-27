#!/usr/bin/env python3
"""Generate the current Evidence Lab pack and skill readiness inventory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
DEFAULT_OUTPUT = ROOT / "docs" / "skill-pack-readiness.md"
FOUNDATION = ROOT / "catalog" / "foundation-skills.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory() -> dict:
    rows = []
    for pack_path in sorted(PACKS.glob("*/*/pack.json")):
        pack_dir = pack_path.parent
        pack = load(pack_path)
        meta = load(pack_dir / "meta.json")
        reference_only = pack["id"] == "example-domain"
        declared = {item["name"]: item for item in meta["skills"]}
        skills = []
        for skill_path in sorted((pack_dir / "skills").glob("*/SKILL.md")):
            skill_dir = skill_path.parent
            line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
            role = "research"
            if skill_dir.name == "evidence-lab-onboarding":
                role = "onboarding"
            elif skill_dir.name == "personal-skill-authoring":
                role = "skill-authoring"
            elif skill_dir.name.endswith("-router"):
                role = "compatibility-router"
            scripts = sum(path.is_file() for path in (skill_dir / "scripts").glob("*")) if (skill_dir / "scripts").exists() else 0
            references = sum(path.is_file() for path in (skill_dir / "references").glob("*")) if (skill_dir / "references").exists() else 0
            skills.append({
                "name": skill_dir.name,
                "role": role,
                "lines": line_count,
                "scripts": scripts,
                "references": references,
                "has_eval": (skill_dir / "evals" / "trigger_eval.json").is_file(),
                "quality_status": declared[skill_dir.name]["quality_status"],
                "development_notes": declared[skill_dir.name].get("development_notes", []),
            })
        rows.append({
            "id": pack["id"],
            "display_name": pack["display_name"],
            "layer": pack["layer"],
            "version": pack["version"],
            "status": meta["status"],
            "capabilities": pack["capabilities"],
            "runtimes": pack["runtimes"],
            "selection_rules": [rule["id"] for rule in pack["selection"]["rules"]],
            "always": pack["selection"]["always"],
            "dependencies": pack["dependencies"],
            "skills": skills,
            "reference_only": reference_only,
        })
    return {"schema_version": 1, "packs": rows}


def cell(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "—"


def render(data: dict) -> str:
    working = [row for row in data["packs"] if not row["reference_only"]]
    reference = [row for row in data["packs"] if row["reference_only"]]
    skills = [skill for row in working for skill in row["skills"]]
    roles = {role: sum(skill["role"] == role for skill in skills) for role in ("research", "onboarding", "skill-authoring", "compatibility-router")}
    quality = {
        state: sum(skill["quality_status"] == state for skill in skills)
        for state in ("needs-substantive-work", "needs-representative-testing", "review-ready", "production", "support-only")
    }
    foundation = load(FOUNDATION)
    foundation_states = {
        state: sum(row["state"] == state for row in foundation["skills"])
        for state in ("planned", "implemented-needs-substantive-work", "implemented-needs-representative-testing", "implemented-review-ready", "implemented-production")
    }
    lines = [
        "# Skill-pack readiness inventory",
        "",
        "Generated deterministically by `python3 scripts/audit_skill_packs.py`.",
        "",
        "## Summary",
        "",
        f"- Working packs: **{len(working)}**; reference-only packs: **{len(reference)}**.",
        f"- Working skills: **{len(skills)}** — {roles['research']} research skills, {roles['onboarding']} onboarding skill, {roles['skill-authoring']} personal skill-authoring skill, and {roles['compatibility-router']} compatibility routers.",
        f"- Lifecycle: **{sum(row['status'] == 'draft' for row in working)} of {len(working)} working packs are `draft`**.",
        f"- Trigger eval files present: **{sum(skill['has_eval'] for skill in skills)} of {len(skills)}**.",
        f"- Explicit quality states: **{quality['needs-substantive-work']} need substantive work**, **{quality['needs-representative-testing']} need representative testing**, **{quality['review-ready']} review-ready**, **{quality['production']} production**, and **{quality['support-only']} support-only**.",
        "",
        "`draft` does not mean that the package is un-installable. It means scientific/content acceptance is incomplete even when repository, selection, release, and bootstrap checks pass.",
        "",
        "## Foundation target",
        "",
        f"The bounded cross-disciplinary target contains **{foundation['target_size']} skills**: **{foundation_states['planned']} planned**, **{foundation_states['implemented-needs-substantive-work']} implemented but needing substantive work**, and **{foundation_states['implemented-needs-representative-testing']} implemented but needing representative testing**.",
        "",
        "This is the capability library from which deterministic onboarding selects a researcher's setup; it is not a requirement to install all 27 skills for every user. Personal skill authoring is mandatory through Core, while domain and workflow add-ons remain conditional.",
        "",
        "| Priority | Foundation capability | Group | Current implementation | State |",
        "|---|---|---|---|---|",
    ]
    for row in foundation["skills"]:
        current = f"`{row['current_skill']}`" if row.get("current_skill") else "—"
        lines.append(f"| {row['priority']} | `{row['id']}` | `{row['group']}` | {current} | `{row['state']}` |")
    lines.extend([
        "",
        "## Packs, boundaries, and current status",
        "",
        "| Pack | Layer | Version | Skills | Capabilities | Selection | Status |",
        "|---|---|---:|---:|---|---|---|",
    ])
    for row in working:
        selection = "always" if row["always"] else cell(row["selection_rules"])
        lines.append(
            f"| `{row['id']}` | `{row['layer']}` | `{row['version']}` | {len(row['skills'])} | "
            f"{cell(row['capabilities'])} | {selection} | `{row['status']}` |"
        )
    lines.extend([
        "",
        "## Skills",
        "",
        "| Pack | Skill | Role | SKILL.md lines | Scripts | References | Trigger eval | Quality status |",
        "|---|---|---|---:|---:|---:|---|---|",
    ])
    for row in working:
        for skill in row["skills"]:
            lines.append(
                f"| `{row['id']}` | `{skill['name']}` | `{skill['role']}` | {skill['lines']} | "
                f"{skill['scripts']} | {skill['references']} | {'yes' if skill['has_eval'] else 'no'} | `{skill['quality_status']}` |"
            )
    lines.extend([
        "",
        "## Readiness interpretation",
        "",
        "- **Mechanically ready:** both hosts can receive immutable pack versions; schemas, trigger evals, deterministic scenario selection, installation planning, and host readback are covered by repository tests.",
        "- **Not yet production-accepted:** all working packs remain `draft`; representative real research runs and independent domain review are still required.",
        "- **Highest content-development priority:** skills explicitly marked `needs-substantive-work`, currently life-science protocols, publication monitoring, qualitative analysis, research-image analysis, and systematic review. Their exact work items live in `meta.json`.",
        "- **Host-independent skill creation:** `personal-skill-authoring` is part of mandatory Core. Native Codex or Claude authoring tools may accelerate it, but bootstrap does not assume that an optional host plugin is installed.",
        "- **Compatibility only:** `data-and-pdf-router` and `full-research-cycle-router` carry no independent research method; their packs compose focused dependencies.",
        "",
        "## Deterministic installation path",
        "",
        "1. Chat answers are normalized to controlled profile values. Free text can propose values, but it cannot name install targets.",
        "2. Stable rules in each `pack.json` select packs; Core is mandatory.",
        "3. Dependencies are resolved and ordered by layer, then pack ID.",
        "4. Bootstrap locks exact versions from the release snapshot and renders a plain-language plan.",
        "5. Nothing is applied until confirmation; the host is read back afterward and state becomes `ready` only when exact versions match.",
        "6. External Codex plugins use a separate reviewed registry because Claude cannot install Codex directory plugins and Codex apps may require an account connection.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(inventory())
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
