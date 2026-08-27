#!/usr/bin/env python3
"""Audit every listed, available entry in a Codex remote plugin catalog snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = ROOT / "docs" / "openai-plugin-audit.md"
DEFAULT_DATA = ROOT / "catalog" / "openai-plugin-audit.json"
RESEARCH_CANDIDATES = {
    "Life Science Research", "Life Sciences NGS Analysis", "Zotero",
    "Build Web Data Visualization", "Data Analytics", "Wolfram", "Consensus",
    "Scite", "Elicit", "SciSpace", "Undermind", "Sider Scholar", "BioRender",
    "PaperDock", "Strive PDF Generator",
}


def component_type(release: dict) -> str:
    has_skills = bool(release.get("skills"))
    has_apps = bool(release.get("app_ids"))
    if has_skills and has_apps:
        return "hybrid"
    if has_skills:
        return "skills-only"
    return "app-only"


def active(plugin: dict) -> bool:
    return (
        plugin.get("scope") == "GLOBAL"
        and plugin.get("discoverability") == "LISTED"
        and plugin.get("status") == "AVAILABLE"
        and plugin.get("installation_policy") in {"AVAILABLE", "INSTALLED_BY_DEFAULT"}
        and bool(plugin.get("release"))
    )


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    source = json.loads(raw)
    all_plugins = source["plugins"]
    current = [plugin for plugin in all_plugins if active(plugin)]
    types = Counter(component_type(plugin["release"]) for plugin in current)
    categories = Counter((plugin["release"].get("interface") or {}).get("category") or "Uncategorized" for plugin in current)
    developers = Counter((plugin["release"].get("interface") or {}).get("developer_name") or "Unknown" for plugin in current)
    policies = Counter(plugin.get("installation_policy") or "UNKNOWN" for plugin in all_plugins)
    statuses = Counter(plugin.get("status") or "UNKNOWN" for plugin in all_plugins)
    discoverability = Counter(plugin.get("discoverability") or "UNKNOWN" for plugin in all_plugins)
    names = [(plugin["release"].get("display_name") or "") for plugin in current]
    candidate_rows = []
    for plugin in current:
        release = plugin["release"]
        name = release.get("display_name")
        if name not in RESEARCH_CANDIDATES:
            continue
        interface = release.get("interface") or {}
        candidate_rows.append({
            "id": plugin["id"],
            "display_name": name,
            "developer": interface.get("developer_name") or "Unknown",
            "category": interface.get("category") or "Uncategorized",
            "version": release.get("version"),
            "component_type": component_type(release),
            "skill_count": len(release.get("skills") or []),
            "app_count": len(release.get("app_ids") or []),
            "authentication_policy": plugin.get("authentication_policy"),
        })
    return {
        "schema_version": 1,
        "fetched_at": source["fetched_at"],
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "all_global_entries": len(all_plugins),
        "active_listed_entries": len(current),
        "all_entry_statuses": dict(sorted(statuses.items())),
        "all_entry_discoverability": dict(sorted(discoverability.items())),
        "all_entry_installation_policies": dict(sorted(policies.items())),
        "active_component_types": dict(sorted(types.items())),
        "active_categories": dict(categories.most_common()),
        "top_active_developers": dict(developers.most_common(20)),
        "exact_tectonic_matches": sum(name.casefold() == "tectonic" for name in names),
        "latex_name_matches": sorted(name for name in names if "latex" in name.casefold()),
        "reviewed_candidates": sorted(candidate_rows, key=lambda row: row["display_name"].casefold()),
    }


def render(data: dict) -> str:
    types = data["active_component_types"]
    lines = [
        "# OpenAI Codex plugin directory audit",
        "",
        f"Snapshot fetched at `{data['fetched_at']}`; SHA-256 `{data['snapshot_sha256']}`.",
        "The audit script examines every entry in the snapshot and then narrows the product review to globally listed, available entries.",
        "",
        "## Whole-catalog result",
        "",
        f"- All global directory entries: **{data['all_global_entries']}**.",
        f"- Active, listed, installable entries: **{data['active_listed_entries']}**.",
        f"- App-only: **{types.get('app-only', 0)}**; hybrid app + skills: **{types.get('hybrid', 0)}**; skills-only: **{types.get('skills-only', 0)}**.",
        f"- Exact plugin-name matches for `Tectonic`: **{data['exact_tectonic_matches']}**.",
        f"- Plugin names containing `LaTeX`: {', '.join(data['latex_name_matches']) or 'none'}.",
        "",
        "A directory entry is not automatically a downloadable skill bundle. App-only and hybrid entries can require an account connection, an installation interstitial, or an external service. Evidence Lab must never silently treat those as zero-dependency skills.",
        "",
        "## Active categories",
        "",
        "| Category | Entries |",
        "|---|---:|",
    ]
    lines.extend(f"| {category} | {count} |" for category, count in data["active_categories"].items())
    lines.extend([
        "",
        "## Research shortlist",
        "",
        "| Plugin | Developer | Type | Skills | Apps | Authentication | Review decision |",
        "|---|---|---|---:|---:|---|---|",
    ])
    decisions = {
        "Life Science Research": "Strong skill-bundle candidate; representative behavior tests required before default selection.",
        "Life Sciences NGS Analysis": "Explicit opt-in only; heavy local scientific toolchain and mixed maturity.",
        "Zotero": "Recommend only when Zotero Desktop is used or detected; local application dependency.",
        "Build Web Data Visualization": "Optional interactive/web visualization; not a replacement for publication figures.",
        "Data Analytics": "Hybrid with external apps; benchmark and connection flow required.",
        "Wolfram": "Useful quantitative companion app; separate user connection required.",
        "BioRender": "Useful life-science image companion app; separate user connection required.",
    }
    for row in data["reviewed_candidates"]:
        decision = decisions.get(row["display_name"], "External research app; benchmark before recommending a default.")
        lines.append(
            f"| {row['display_name']} | {row['developer']} | `{row['component_type']}` | "
            f"{row['skill_count']} | {row['app_count']} | `{row['authentication_policy']}` | {decision} |"
        )
    lines.extend([
        "",
        "## Product boundary",
        "",
        "1. Evidence Lab packs remain the portable Codex + Claude layer.",
        "2. Codex runtime plugins already present on the host may be used as baseline capabilities after readback verification.",
        "3. Reviewed skills-only plugins may enter deterministic selection only after structural and representative behavior tests.",
        "4. Directory apps are recommendations, not silent bootstrap operations. The user confirms the connection in Codex and Evidence Lab verifies availability afterward.",
        "5. External plugin contents are referenced by stable directory ID and observed version; they are not copied into this MIT repository.",
        "",
        "Official references: https://learn.chatgpt.com/docs/plugins and https://learn.chatgpt.com/docs/build-plugins.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, nargs="?")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not args.data.exists():
            print(f"FAIL: missing audit data: {args.data.relative_to(ROOT)}", file=sys.stderr)
            return 1
        rendered = render(json.loads(args.data.read_text(encoding="utf-8")))
        if not args.report.exists() or args.report.read_text(encoding="utf-8") != rendered:
            print(f"FAIL: generated report is stale: {args.report.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"verified {args.report.relative_to(ROOT)}")
        return 0
    if args.snapshot is None:
        parser.error("snapshot is required unless --check is used")
    data = audit(args.snapshot)
    args.data.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.report.write_text(render(data), encoding="utf-8")
    print(f"audited {data['all_global_entries']} entries; {data['active_listed_entries']} active/listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
