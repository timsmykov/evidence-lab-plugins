#!/usr/bin/env python3
"""Audit the Codex plugin directory and classify its researcher-facing surface."""
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
TARGET_CATEGORIES = {"Education & Research", "Data & Analytics", "Scientific Research"}
RESEARCH_CANDIDATES = {
    "Academic Writing Toolkit", "Ace Knowledge Graph", "Acumen by Talarion",
    "alphaXiv", "Amass", "Article Galaxy", "BioRender", "Boltz",
    "Build Web Data Visualization", "Consensus", "CourtListener", "Data Analytics",
    "Deep Research", "Dewey Data", "Elicit", "GoVeda Patent",
    "Life Science Research", "Life Sciences NGS Analysis", "Midpage Legal Research",
    "Mixpanel Headless", "PaperDock", "Patent Connector", "Precise Special Functions",
    "Readwise", "Scholar Gateway", "Scholar Sidekick", "SciSpace", "Scite",
    "Sider Scholar", "Strive PDF Generator", "Transkriptor", "Undermind", "Wolfram",
    "Zotero",
}
RESEARCH_TERMS = {
    "academic", "analysis", "article", "citation", "clinical", "computation",
    "data", "dataset", "evidence", "formula", "journal", "knowledge graph",
    "laboratory", "literature", "mathemat", "paper", "patent", "pdf", "protein",
    "research", "science", "scientific", "scholar", "statistics", "transcri",
}
SKILL_BUNDLE_OVERRIDES = {
    "Life Science Research": {
        "dependency_model": "public-endpoints-and-local-runtime",
        "provider_access": "no-provider-account-observed",
        "bootstrap_decision": "candidate-after-behavior-benchmark",
        "reason": "Broad OpenAI-authored life-science retrieval bundle; useful by profile, but not a universal researcher baseline.",
    },
    "Life Sciences NGS Analysis": {
        "dependency_model": "heavy-local-bioinformatics-toolchain",
        "provider_access": "no-provider-account-observed",
        "bootstrap_decision": "explicit-domain-opt-in",
        "reason": "Useful only for sequencing and omics workflows; dependency preflight is mandatory.",
    },
    "Zotero": {
        "dependency_model": "local-zotero-desktop",
        "provider_access": "local-application-required",
        "bootstrap_decision": "explicit-tool-opt-in",
        "reason": "Install only when the researcher uses Zotero and the local application is detected.",
    },
    "Mixpanel Headless": {
        "dependency_model": "python-sdk-and-mixpanel-account",
        "provider_access": "external-account-required",
        "bootstrap_decision": "exclude-from-researcher-default",
        "reason": "A skill bundle, but its purpose is product analytics and it requires Mixpanel authentication.",
    },
    "Boltz": {
        "dependency_model": "boltz-cli-auth-and-paid-jobs",
        "provider_access": "external-account-and-spend-confirmation-required",
        "bootstrap_decision": "explicit-domain-opt-in-after-benchmark",
        "reason": "Specialized biomolecular modeling; its own prompts require cost estimation and spend confirmation.",
    },
    "Build Web Data Visualization": {
        "dependency_model": "local-web-development-toolchain",
        "provider_access": "no-provider-account-observed",
        "bootstrap_decision": "optional-output-format-opt-in",
        "reason": "Useful for interactive research outputs, but outside the three research catalog categories and not a publication-figure baseline.",
    },
}
OFFICIAL_ACCESS_EVIDENCE = {
    "Consensus": {
        "access_summary": "Free account tier includes limited MCP/ChatGPT calls; paid tiers raise limits and can enable metered overage.",
        "evidence_url": "https://help.consensus.app/en/articles/10059020-consensus-in-chatgpt",
    },
    "Elicit": {
        "access_summary": "Free Basic plan exists with limited agent/report usage; paid plans add capacity and exports.",
        "evidence_url": "https://elicit.com/pricing",
    },
    "Scite": {
        "access_summary": "MCP access is included in paid individual plans; the public pricing page offers a time-limited trial, not a perpetual free MCP tier.",
        "evidence_url": "https://scite.ai/pricing",
    },
    "SciSpace": {
        "access_summary": "Free Basic tier is credit-limited; paid subscriptions increase monthly agent credits.",
        "evidence_url": "https://scispace.com/resources/credits-pricing-guide/",
    },
    "Readwise": {
        "access_summary": "Thirty-day free trial, then a paid subscription; no permanent free plan is advertised.",
        "evidence_url": "https://readwise.io/pricing/reader",
    },
    "Zotero": {
        "access_summary": "The local open-source application is free; optional hosted file storage has a free allowance and paid larger tiers.",
        "evidence_url": "https://www.zotero.org/storage",
    },
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


def catalog_row(plugin: dict) -> dict:
    release = plugin["release"]
    interface = release.get("interface") or {}
    name = release.get("display_name") or plugin["id"]
    kind = component_type(release)
    text = " ".join(str(value or "") for value in (
        name, release.get("description"), interface.get("short_description"), interface.get("long_description")
    )).casefold()
    research_signal = name in RESEARCH_CANDIDATES or any(term in text for term in RESEARCH_TERMS)
    if kind == "skills-only":
        override = SKILL_BUNDLE_OVERRIDES.get(name, {})
        dependency_model = override.get("dependency_model", "skill-bundle-dependencies-unreviewed")
        provider_access = override.get("provider_access", "requires-bundle-review")
        decision = override.get("bootstrap_decision", "manual-bundle-review")
        reason = override.get("reason", "Pure skill bundle; inspect its skills and runtime dependencies before selection.")
    else:
        dependency_model = "connected-service-with-skills" if kind == "hybrid" else "connected-service"
        provider_access = "external-service-terms-unverified"
        decision = "connection-candidate-after-benchmark" if name in RESEARCH_CANDIDATES else (
            "manual-review-if-profile-matches" if research_signal else "not-bootstrap-priority"
        )
        reason = (
            "Potential research companion, but it is a connected service and its account, limits, and pricing require official review."
            if name in RESEARCH_CANDIDATES
            else "Catalog-screened; no evidence yet that it should enter the Evidence Lab bootstrap shortlist."
        )
    access_evidence = OFFICIAL_ACCESS_EVIDENCE.get(name)
    return {
        "id": plugin["id"],
        "display_name": name,
        "developer": interface.get("developer_name") or "Unknown",
        "category": interface.get("category") or "Uncategorized",
        "version": release.get("version"),
        "component_type": kind,
        "skill_count": len(release.get("skills") or []),
        "app_count": len(release.get("app_ids") or []),
        "authentication_policy": plugin.get("authentication_policy"),
        "installation_policy": plugin.get("installation_policy"),
        "website_url": interface.get("website_url"),
        "short_description": interface.get("short_description") or release.get("description"),
        "research_signal": research_signal,
        "dependency_model": dependency_model,
        "provider_access": provider_access,
        "bootstrap_decision": decision,
        "reason": reason,
        "official_access_evidence": access_evidence,
    }


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    source = json.loads(raw)
    all_plugins = source["plugins"]
    current = [plugin for plugin in all_plugins if active(plugin)]
    rows = [catalog_row(plugin) for plugin in current]
    target = sorted((row for row in rows if row["category"] in TARGET_CATEGORIES), key=lambda row: (row["category"], row["display_name"].casefold()))
    skills_only = sorted((row for row in rows if row["component_type"] == "skills-only"), key=lambda row: (row["category"], row["display_name"].casefold()))
    reviewed = sorted((row for row in rows if row["display_name"] in RESEARCH_CANDIDATES), key=lambda row: row["display_name"].casefold())
    names = [row["display_name"] for row in rows]
    return {
        "schema_version": 2,
        "fetched_at": source["fetched_at"],
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "all_global_entries": len(all_plugins),
        "active_listed_entries": len(current),
        "active_component_types": dict(sorted(Counter(row["component_type"] for row in rows).items())),
        "active_categories": dict(Counter(row["category"] for row in rows).most_common()),
        "target_categories": sorted(TARGET_CATEGORIES),
        "target_category_entries": len(target),
        "target_component_types": dict(sorted(Counter(row["component_type"] for row in target).items())),
        "exact_tectonic_matches": sum(name.casefold() == "tectonic" for name in names),
        "latex_name_matches": sorted(name for name in names if "latex" in name.casefold()),
        "target_inventory": target,
        "all_skills_only_plugins": skills_only,
        "reviewed_candidates": reviewed,
    }


def render(data: dict) -> str:
    types = data["active_component_types"]
    target_types = data["target_component_types"]
    lines = [
        "# Codex researcher plugin marketplace audit", "",
        f"Snapshot fetched at `{data['fetched_at']}`; SHA-256 `{data['snapshot_sha256']}`.",
        "This is a complete catalog screen, not a claim that every external service has been behavior-tested.", "",
        "## What was audited", "",
        f"- All directory records: **{data['all_global_entries']}**; active, listed, installable records: **{data['active_listed_entries']}**.",
        f"- Whole active catalog: **{types.get('app-only', 0)} app-only**, **{types.get('hybrid', 0)} hybrid**, **{types.get('skills-only', 0)} skills-only**.",
        f"- Complete researcher-facing category inventory: **{data['target_category_entries']}** entries across Education & Research, Data & Analytics, and Scientific Research.",
        f"- In those categories: **{target_types.get('app-only', 0)} app-only**, **{target_types.get('hybrid', 0)} hybrid**, **{target_types.get('skills-only', 0)} skills-only**.",
        f"- Exact `Tectonic` matches: **{data['exact_tectonic_matches']}**; names containing `LaTeX`: **{len(data['latex_name_matches'])}**.", "",
        "The Install button is not evidence of zero cost or zero setup. App-only and hybrid entries connect an external service. A skills-only entry can still require an account, local software, a heavy toolchain, or paid jobs.", "",
        "## Pure skill bundles in the three target categories", "",
        "| Plugin | Category | Skills | Provider/runtime dependency | Bootstrap decision |", "|---|---|---:|---|---|",
    ]
    for row in (row for row in data["target_inventory"] if row["component_type"] == "skills-only"):
        lines.append(f"| {row['display_name']} | {row['category']} | {row['skill_count']} | `{row['provider_access']}` / `{row['dependency_model']}` | `{row['bootstrap_decision']}` |")
    lines.extend(["", "## Bootstrap policy", "",
        "1. Evidence Lab-owned packs remain the portable Codex + Claude layer.",
        "2. A reviewed pure skill bundle may be proposed only when its profile signals match and its dependency preflight passes.",
        "3. App-only and hybrid plugins are connection offers. They are never silently installed or described as free without current official evidence.",
        "4. Account, subscription, API, data-sharing, and paid-compute terms are independent fields. Unknown means unknown, not free.",
        "5. User confirmation is required before every external connection and before any workflow that can incur spend.", "",
        "## Product-review shortlist", "", "| Plugin | Category | Type | Access evidence | Decision |", "|---|---|---|---|---|",
    ])
    for row in data["reviewed_candidates"]:
        lines.append(f"| {row['display_name']} | {row['category']} | `{row['component_type']}` | `{row['provider_access']}` | `{row['bootstrap_decision']}` |")
    lines.extend(["", "## Official access review for high-priority services", "",
        "These facts are intentionally separate from the catalog manifest and must be refreshed when provider terms change.", "",
        "| Plugin | Current access evidence | Official source |", "|---|---|---|",
    ])
    for row in data["reviewed_candidates"]:
        evidence = row.get("official_access_evidence")
        if evidence:
            lines.append(f"| {row['display_name']} | {evidence['access_summary']} | {evidence['evidence_url']} |")
    lines.extend(["", "## Complete category inventory", "",
        "Every active entry in the three target categories appears below. `catalog-screened` means identity and component shape were checked from the Codex directory; it does not mean pricing or behavior was independently verified.", "",
        "| Category | Plugin | Developer | Type | Skills | Apps | Screen decision |", "|---|---|---|---|---:|---:|---|",
    ])
    for row in data["target_inventory"]:
        lines.append(f"| {row['category']} | {row['display_name']} | {row['developer']} | `{row['component_type']}` | {row['skill_count']} | {row['app_count']} | `{row['bootstrap_decision']}` |")
    lines.extend(["", "## Sources and reproducibility", "",
        "- The committed JSON preserves the complete target-category inventory and every active skills-only bundle.",
        "- Re-run `python3 scripts/audit_openai_plugins.py <catalog-snapshot>` when the Codex directory changes.",
        "- Official plugin model: https://learn.chatgpt.com/docs/plugins and https://learn.chatgpt.com/docs/build-plugins.", "",
    ])
    return "\n".join(lines)


def validate_data(data: dict) -> list[str]:
    failures = []
    target = data.get("target_inventory", [])
    if len(target) != data.get("target_category_entries"):
        failures.append("target inventory count mismatch")
    ids = [row.get("id") for row in target]
    if len(ids) != len(set(ids)):
        failures.append("target inventory contains duplicate plugin IDs")
    if set(row.get("category") for row in target) - set(data.get("target_categories", [])):
        failures.append("target inventory contains an out-of-scope category")
    bundles = data.get("all_skills_only_plugins", [])
    if len(bundles) != data.get("active_component_types", {}).get("skills-only"):
        failures.append("skills-only inventory count mismatch")
    return failures


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
        data = json.loads(args.data.read_text(encoding="utf-8"))
        failures = validate_data(data)
        if failures:
            print("FAIL: " + "; ".join(failures), file=sys.stderr)
            return 1
        if not args.report.exists() or args.report.read_text(encoding="utf-8") != render(data):
            print(f"FAIL: generated report is stale: {args.report.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"verified {args.report.relative_to(ROOT)} ({len(data['target_inventory'])} target entries)")
        return 0
    if args.snapshot is None:
        parser.error("snapshot is required unless --check is used")
    data = audit(args.snapshot)
    failures = validate_data(data)
    if failures:
        print("FAIL: " + "; ".join(failures), file=sys.stderr)
        return 1
    args.data.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.report.write_text(render(data), encoding="utf-8")
    print(f"audited {data['active_listed_entries']} active entries; preserved {data['target_category_entries']} target entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
