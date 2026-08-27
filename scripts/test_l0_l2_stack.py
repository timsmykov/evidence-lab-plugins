#!/usr/bin/env python3
"""Validate the canonical L0-L2 stack registry and its decision boundaries."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "catalog" / "l0-l2-stack.json"
SCHEMA = ROOT / "schemas" / "l0-l2-stack.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    registry = load(REGISTRY)
    schema = load(SCHEMA)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(registry),
        key=lambda error: list(error.path),
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise AssertionError(f"{location}: {first.message}")

    components = registry["components"]
    by_id = {item["id"]: item for item in components}
    if len(by_id) != len(components):
        raise AssertionError("component IDs must be unique")

    profile_ids = [profile["id"] for profile in registry["profiles"]]
    if profile_ids != ["base", "documents", "data"]:
        raise AssertionError("profiles must remain ordered base, documents, data")
    for profile in registry["profiles"]:
        unknown = set(profile["component_ids"]) - set(by_id)
        if unknown:
            raise AssertionError(f"{profile['id']}: unknown component IDs {sorted(unknown)}")

    base = {item["id"] for item in components if item["inclusion"] in {"required", "route-required"}}
    listed_base = set(registry["profiles"][0]["component_ids"])
    if base != listed_base:
        raise AssertionError(f"base profile drift: missing={sorted(base - listed_base)}, extra={sorted(listed_base - base)}")

    for item in components:
        lifecycle = item["lifecycle"]
        if any(not lifecycle[action].strip() for action in ("install", "verify", "update", "remove")):
            raise AssertionError(f"{item['id']}: incomplete lifecycle")
        if item["access_cost"]["class"] == "provider-access-required" and item["category"] != "access":
            raise AssertionError(f"{item['id']}: provider access cost belongs only to an access component")
        if item["verification"]["status"] == "live-cross-host":
            evidence = " ".join(item["verification"]["evidence_refs"])
            if "codex" not in evidence.casefold() or "claude" not in evidence.casefold():
                raise AssertionError(f"{item['id']}: live cross-host status lacks both host evidence")

    print(f"OK: L0-L2 registry verified ({len(components)} components, 3 profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
