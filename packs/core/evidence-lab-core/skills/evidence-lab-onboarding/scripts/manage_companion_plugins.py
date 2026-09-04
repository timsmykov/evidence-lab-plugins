#!/usr/bin/env python3
"""Apply and verify one confirmed Codex companion-plugin plan."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from inventory_host import collect_inventory


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def identities(inventory: dict) -> set[str]:
    result = set()
    for row in inventory.get("plugins", []):
        if not row.get("enabled", True):
            continue
        for key in ("plugin_id", "name", "selector"):
            if row.get(key):
                result.add(str(row[key]).casefold())
    return result


def expected_identity(action: dict) -> set[str]:
    values = {str(action["plugin_id"]).casefold()}
    if action.get("selector"):
        selector = str(action["selector"]).casefold()
        values.update((selector, selector.split("@", 1)[0]))
    return values


def apply_plan(plan: dict, inventory_before: dict, runner=run, inventory_reader=collect_inventory) -> dict:
    if plan.get("inventory_digest") != inventory_before.get("digest"):
        return {"status": "stale", "installed": [], "retained": [], "pending_activation": [], "error": "host inventory changed"}
    installed, retained, added_selectors = [], [], []
    for action in plan.get("actions", []):
        if action["action"] == "retain-installed":
            retained.append(action["display_name"])
            continue
        if action["action"] != "install-after-confirmation":
            continue
        selector = action.get("selector")
        if not selector:
            return {"status": "failed", "installed": installed, "retained": retained, "pending_activation": [], "error": f"missing selector for {action['display_name']}"}
        result = runner(["codex", "plugin", "add", selector, "--json"])
        if result.returncode:
            for added in reversed(added_selectors):
                runner(["codex", "plugin", "remove", added, "--json"])
            return {"status": "failed", "installed": installed, "retained": retained, "pending_activation": [], "error": f"Codex could not install {action['display_name']}"}
        added_selectors.append(selector)
        installed.append(action["display_name"])

    inventory_after = inventory_reader()
    actual = identities(inventory_after)
    missing = [
        action["display_name"] for action in plan.get("actions", [])
        if action["action"] in {"retain-installed", "install-after-confirmation"}
        and action.get("required") and not (expected_identity(action) & actual)
    ]
    if missing:
        for added in reversed(added_selectors):
            runner(["codex", "plugin", "remove", added, "--json"])
        return {"status": "failed", "installed": installed, "retained": retained, "pending_activation": [], "missing": missing, "error": "required plugin readback failed"}
    pending = [
        action["display_name"] for action in plan.get("actions", [])
        if action["action"] == "activate-after-confirmation" and not (expected_identity(action) & actual)
    ]
    return {
        "status": "awaiting-activation" if pending else "ready",
        "installed": installed,
        "retained": retained,
        "pending_activation": pending,
        "inventory_after": inventory_after,
        "error": None,
    }


def verify_plan(plan: dict, inventory: dict) -> dict:
    actual = identities(inventory)
    missing = [
        action["display_name"] for action in plan.get("actions", [])
        if (action.get("required") or action["action"] == "activate-after-confirmation")
        and action["action"] not in {"withhold-missing-prerequisite", "withhold-pending-benchmark"}
        and not (expected_identity(action) & actual)
    ]
    return {"status": "ready" if not missing else "awaiting-activation", "missing": missing, "inventory_after": inventory}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("apply", "verify"))
    parser.add_argument("plan", type=Path)
    parser.add_argument("inventory", type=Path, nargs="?")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    inventory = json.loads(args.inventory.read_text(encoding="utf-8")) if args.inventory else collect_inventory()
    result = apply_plan(plan, inventory) if args.command == "apply" else verify_plan(plan, inventory)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["status"] in {"ready", "awaiting-activation"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
