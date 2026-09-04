#!/usr/bin/env python3
"""Create a deterministic, non-mutating Codex companion-plugin plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parent.parent
PACK_ROOT = HERE.parents[3] if HERE.parent.name == "scripts" and HERE.parent.parent.name == "evidence-lab-onboarding" else REPO_ROOT
DEFAULT_REGISTRY = PACK_ROOT / "catalog" / "external-plugin-candidates.json"
FIELDS = ("domains", "workflows", "materials", "stages", "methods")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def matches(profile: dict, selection: dict) -> bool:
    """Match reviewed profile signals with explicit all/any semantics."""
    signals = selection["signals"]
    if not signals:
        return True
    results = [bool(set(profile.get(field, [])) & set(values)) for field, values in signals.items()]
    return any(results) if selection.get("match") == "any" else all(results)


def installed_index(inventory: dict | None) -> tuple[set[str], set[str], set[str], set[str]]:
    plugins, disabled_plugins, skills, local_apps = set(), set(), set(), set()
    for row in (inventory or {}).get("plugins", []):
        target = plugins if row.get("enabled", True) else disabled_plugins
        for value in (row.get("plugin_id"), row.get("name"), row.get("selector")):
            if value:
                target.add(str(value).casefold())
    for row in (inventory or {}).get("skills", []):
        if row.get("name"):
            skills.add(str(row["name"]).casefold())
    for name in (inventory or {}).get("local_apps", []):
        local_apps.add(str(name).casefold())
    return plugins, disabled_plugins, skills, local_apps


def select(
    profile: dict,
    registry: dict,
    host: str = "codex",
    requested_plugins: tuple[str, ...] = (),
    inventory: dict | None = None,
) -> dict:
    if host != "codex":
        return {"schema_version": 1, "host": host, "actions": [], "reason": "Codex directory plugins are not portable to this host."}
    requested = {value.casefold() for value in requested_plugins}
    installed_plugins, disabled_plugins, installed_skills, local_apps = installed_index(inventory)
    actions = []
    for plugin in registry["plugins"]:
        if host not in plugin["hosts"] or not matches(profile, plugin["selection"]):
            continue
        identities = {
            plugin["id"].casefold(), plugin["display_name"].casefold(),
            plugin.get("plugin_name", "").casefold(),
            *(value.casefold() for value in plugin.get("aliases", [])),
        }
        identities.discard("")
        explicitly_requested = bool(identities & requested)
        if plugin["policy"] == "explicit-opt-in" and not explicitly_requested:
            continue
        present = bool(identities & installed_plugins)
        present_but_disabled = bool(identities & disabled_plugins)
        prerequisite = plugin.get("requires_local_app")
        prerequisite_ready = not prerequisite or prerequisite.casefold() in local_apps
        if present:
            action = "retain-installed"
        elif present_but_disabled:
            action = (
                "activate-after-confirmation"
                if plugin["policy"] in {"approved-baseline", "required-when-selected", "explicit-opt-in"}
                else "offer-activation"
            )
        elif prerequisite and not prerequisite_ready:
            action = "withhold-missing-prerequisite"
        elif plugin["install_mode"] == "marketplace" and plugin["policy"] in {
            "approved-baseline", "required-when-selected", "recommended-when-selected", "explicit-opt-in",
        }:
            action = "install-after-confirmation"
        elif plugin["install_mode"] == "plugins-ui" and plugin["policy"] == "required-when-selected":
            action = "activate-after-confirmation"
        elif plugin["install_mode"] == "plugins-ui" and plugin["policy"] == "recommended-when-selected":
            action = "offer-activation"
        elif plugin["component_type"] in {"directory-app", "hybrid"}:
            action = "offer-connection" if plugin["policy"] == "candidate" else "withhold-pending-benchmark"
        elif plugin["policy"] == "candidate":
            action = "recommend-after-validation"
        else:
            action = "offer-opt-in" if plugin["policy"] == "explicit-opt-in" else "withhold-pending-benchmark"
        selector = None
        if plugin.get("marketplace") and plugin.get("plugin_name"):
            selector = f"{plugin['plugin_name']}@{plugin['marketplace']}"
        actions.append({
            "plugin_id": plugin["id"],
            "display_name": plugin["display_name"],
            "action": action,
            "install_mode": plugin["install_mode"],
            "credential_mode": plugin["credential_mode"],
            "selector": selector,
            "required": plugin["policy"] in {"approved-baseline", "required-when-selected"},
            "installed_version": next((
                str(row.get("version") or "unknown") for row in (inventory or {}).get("plugins", [])
                if identities & {str(row.get(key) or "").casefold() for key in ("plugin_id", "name", "selector")}
            ), None),
            "overlapping_skills": sorted(installed_skills & {value.casefold() for value in plugin.get("capabilities", [])}),
            "share_url": plugin.get("share_url"),
            "reason": plugin["rationale"],
        })
    return {"schema_version": 1, "host": host, "inventory_digest": (inventory or {}).get("digest"), "actions": actions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--host", choices=("codex", "claude-code"), default="codex")
    parser.add_argument("--request", action="append", default=[], help="Explicit plugin ID or display name; may be repeated")
    parser.add_argument("--inventory", type=Path, help="Current host inventory produced by inventory_host.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inventory = load(args.inventory) if args.inventory else None
    rendered = json.dumps(select(load(args.profile), load(args.registry), args.host, tuple(args.request), inventory), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
