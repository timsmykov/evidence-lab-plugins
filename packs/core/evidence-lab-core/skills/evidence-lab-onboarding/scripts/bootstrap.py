#!/usr/bin/env python3
"""Plan, apply, and verify an Evidence Lab installation for Codex or Claude Code."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
from select_packs import load_object, select


HERE = Path(__file__).resolve()
PACK_ROOT = HERE.parents[3]
DEFAULT_CATALOG = PACK_ROOT / "catalog" / "packs.json"
DEFAULT_SOURCE = "timsmykov/evidence-lab-plugins"
DEFAULT_MARKETPLACE = "evidence-lab-plugins"


class BootstrapError(RuntimeError):
    pass


SAFE_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_REF = re.compile(r"^[A-Za-z0-9._/-]+$")


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def plan_id_for(host: str, source: str, ref: str, selection_plan: dict) -> str:
    identity = json.dumps(
        {"host": host, "source": source, "ref": ref, "selection_plan": selection_plan},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(identity).hexdigest()[:16]


def make_plan(profile: dict, catalog: dict, host: str, source: str, ref: str, marketplace: str) -> dict:
    selection_plan = select(profile, catalog)
    plan_id = plan_id_for(host, source, ref, selection_plan)
    operations = [{"action": "ensure-marketplace", "target": marketplace}]
    operations.extend(
        {"action": "install-pack", "target": pack["id"], "version": pack["version"]}
        for pack in selection_plan["packs"]
    )
    return {
        "schema_version": 1,
        "plan_id": plan_id,
        "host": host,
        "marketplace": {"name": marketplace, "source": source, "ref": ref},
        "selection_plan": selection_plan,
        "operations": operations,
    }


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise BootstrapError(f"host executable not found: {command[0]}") from exc


def run_checked(command: list[str], label: str) -> str:
    result = run(command)
    if result.returncode:
        raise BootstrapError(f"{label} failed with exit code {result.returncode}")
    return result.stdout


def run_json(command: list[str], label: str):
    output = run_checked(command, label)
    try:
        return json.loads(output or "null")
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"{label} returned invalid JSON") from exc


def marketplace_list_command(host: str) -> list[str]:
    if host == "codex":
        return ["codex", "plugin", "marketplace", "list", "--json"]
    return ["claude", "plugin", "marketplace", "list", "--json"]


def installed_list_command(host: str) -> list[str]:
    if host == "codex":
        return ["codex", "plugin", "list", "--json"]
    return ["claude", "plugin", "list", "--json"]


def marketplace_add_command(host: str, source: str, ref: str) -> list[str]:
    if host == "codex":
        command = ["codex", "plugin", "marketplace", "add", source]
        if not source.startswith(("/", ".")):
            command.extend(("--ref", ref))
        return [*command, "--json"]
    if source.startswith(("/", ".", "https://", "git@")):
        pinned = f"{source}#{ref}" if not source.startswith(("/", ".")) else source
    else:
        pinned = f"https://github.com/{source}.git#{ref}"
    return ["claude", "plugin", "marketplace", "add", pinned, "--scope", "user"]


def marketplace_update_command(host: str, name: str) -> list[str]:
    if host == "codex":
        return ["codex", "plugin", "marketplace", "upgrade", name, "--json"]
    return ["claude", "plugin", "marketplace", "update", name]


def is_local_source(source: str) -> bool:
    return source.startswith(("/", "."))


def install_command(host: str, pack_id: str, marketplace: str) -> list[str]:
    selector = f"{pack_id}@{marketplace}"
    if host == "codex":
        return ["codex", "plugin", "add", selector, "--json"]
    return ["claude", "plugin", "install", selector, "--scope", "user"]


def remove_command(host: str, pack_id: str, marketplace: str) -> list[str]:
    selector = f"{pack_id}@{marketplace}"
    if host == "codex":
        return ["codex", "plugin", "remove", selector, "--json"]
    return ["claude", "plugin", "uninstall", selector, "--scope", "user"]


def marketplace_rows(host: str) -> list[dict]:
    payload = run_json(marketplace_list_command(host), "marketplace readback")
    rows = payload.get("marketplaces", []) if isinstance(payload, dict) else payload
    return [row for row in (rows or []) if isinstance(row, dict)]


def installed_rows(host: str, marketplace: str) -> list[dict]:
    payload = run_json(installed_list_command(host), "plugin readback")
    rows = payload.get("installed", []) if isinstance(payload, dict) else payload
    normalized = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        raw_id = row.get("pluginId") or row.get("id") or row.get("name") or ""
        name = row.get("name") or str(raw_id).split("@", 1)[0]
        row_marketplace = row.get("marketplaceName") or row.get("marketplace")
        if row_marketplace is None and "@" in str(raw_id):
            row_marketplace = str(raw_id).split("@", 1)[1]
        if row_marketplace and row_marketplace != marketplace:
            continue
        version = str(row.get("version") or "unknown")
        normalized.append({"id": str(name), "version": version})
    return sorted(normalized, key=lambda item: item["id"])


def canonical_source(source: str) -> str:
    value = source.strip().split("#", 1)[0].rstrip("/")
    if is_local_source(value):
        return str(Path(value).resolve())
    github_ssh_prefix = "git@" + "github.com:"
    if value.startswith(github_ssh_prefix):
        value = value.removeprefix(github_ssh_prefix)
    value = value.removeprefix("https://github.com/").removeprefix("http://github.com/")
    return value.removesuffix(".git").casefold()


def source_matches(row: dict, source: str) -> bool:
    candidates = [row.get("repo"), row.get("source"), row.get("path"), row.get("installLocation")]
    nested = row.get("marketplaceSource")
    if isinstance(nested, dict):
        candidates.append(nested.get("source"))
    expected = canonical_source(source)
    return any(
        isinstance(candidate, str)
        and canonical_source(candidate) == expected
        for candidate in candidates
    )


def desired_from_plan(plan: dict) -> list[dict]:
    return [{"id": pack["id"], "version": pack["version"]} for pack in plan["selection_plan"]["packs"]]


def initial_state(plan: dict) -> dict:
    return {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "host": plan["host"],
        "status": "planned",
        "desired": desired_from_plan(plan),
        "installed_before": [],
        "installed_after": [],
        "operations": [
            {"action": operation["action"], "target": operation["target"], "status": "pending"}
            for operation in plan["operations"]
        ],
        "error": None,
    }


def validate_plan(plan: dict) -> None:
    if plan.get("schema_version") != 1 or plan.get("host") not in {"codex", "claude-code"}:
        raise BootstrapError("unsupported installation plan")
    marketplace = plan.get("marketplace")
    selection_plan = plan.get("selection_plan")
    if not isinstance(marketplace, dict) or not isinstance(selection_plan, dict):
        raise BootstrapError("installation plan is incomplete")
    if not selection_plan.get("packs"):
        raise BootstrapError("installation plan contains no packs")
    name, source, ref = marketplace.get("name"), marketplace.get("source"), marketplace.get("ref")
    if not isinstance(name, str) or not SAFE_IDENTIFIER.fullmatch(name):
        raise BootstrapError("installation plan contains an unsafe marketplace name")
    if not isinstance(source, str) or not source.strip():
        raise BootstrapError("installation plan contains no marketplace source")
    if not isinstance(ref, str) or not SAFE_REF.fullmatch(ref):
        raise BootstrapError("installation plan contains an unsafe Git ref")
    desired = desired_from_plan(plan)
    if len({item["id"] for item in desired}) != len(desired):
        raise BootstrapError("installation plan contains duplicate packs")
    if any(not SAFE_IDENTIFIER.fullmatch(item["id"]) or not item["version"] for item in desired):
        raise BootstrapError("installation plan contains an unsafe pack identity")
    expected_operations = [{"action": "ensure-marketplace", "target": name}]
    expected_operations.extend(
        {"action": "install-pack", "target": item["id"], "version": item["version"]}
        for item in desired
    )
    if plan.get("operations") != expected_operations:
        raise BootstrapError("installation plan operations do not match its pack selection")
    expected_id = plan_id_for(plan["host"], source, ref, selection_plan)
    if plan.get("plan_id") != expected_id:
        raise BootstrapError("installation plan identity does not match its contents")


def ensure_marketplace(plan: dict, state: dict) -> None:
    host = plan["host"]
    marketplace = plan["marketplace"]
    existing = next((row for row in marketplace_rows(host) if row.get("name") == marketplace["name"]), None)
    try:
        if existing:
            if not source_matches(existing, marketplace["source"]):
                raise BootstrapError(f"marketplace {marketplace['name']} already points to another source")
            # Both hosts already read a local marketplace directly. Trying to
            # update it as if it were a Git remote is either unsupported or
            # needlessly rewrites host state on an idempotent rerun.
            if not is_local_source(marketplace["source"]):
                run_checked(marketplace_update_command(host, marketplace["name"]), "marketplace update")
        else:
            run_checked(
                marketplace_add_command(host, marketplace["source"], marketplace["ref"]),
                "marketplace setup",
            )
        state["operations"][0]["status"] = "completed"
    except BootstrapError:
        state["operations"][0]["status"] = "failed"
        raise


def apply_plan(plan: dict, state_path: Path) -> dict:
    validate_plan(plan)
    state = initial_state(plan)
    host = plan["host"]
    marketplace = plan["marketplace"]["name"]
    state["installed_before"] = installed_rows(host, marketplace)
    state["status"] = "applying"
    write_json_atomic(state_path, state)
    before = {item["id"]: item["version"] for item in state["installed_before"]}
    installed_this_attempt: list[str] = []

    try:
        ensure_marketplace(plan, state)
        write_json_atomic(state_path, state)
        for index, desired in enumerate(state["desired"], 1):
            pack_id, version = desired["id"], desired["version"]
            if before.get(pack_id) == version:
                state["operations"][index]["status"] = "skipped"
                continue
            try:
                run_checked(install_command(host, pack_id, marketplace), f"install {pack_id}")
            except BootstrapError:
                state["operations"][index]["status"] = "failed"
                raise
            if pack_id not in before:
                installed_this_attempt.append(pack_id)
            state["operations"][index]["status"] = "completed"
            write_json_atomic(state_path, state)

        state["installed_after"] = installed_rows(host, marketplace)
        after = {item["id"]: item["version"] for item in state["installed_after"]}
        missing = [item["id"] for item in state["desired"] if after.get(item["id"]) != item["version"]]
        if missing:
            raise BootstrapError(f"installation readback did not confirm: {', '.join(missing)}")
        state["status"] = "ready"
        state["error"] = None
    except BootstrapError as exc:
        state["error"] = str(exc)
        rollback_failed = False
        for pack_id in reversed(installed_this_attempt):
            result = run(remove_command(host, pack_id, marketplace))
            operation = next(item for item in state["operations"] if item["target"] == pack_id)
            if result.returncode:
                operation["status"] = "rollback-failed"
                rollback_failed = True
            else:
                operation["status"] = "rolled-back"
        try:
            state["installed_after"] = installed_rows(host, marketplace)
        except BootstrapError:
            state["installed_after"] = []
            rollback_failed = True
        state["status"] = "partial" if rollback_failed else "failed"
    write_json_atomic(state_path, state)
    return state


def verify_plan(plan: dict) -> dict:
    validate_plan(plan)
    marketplace = plan["marketplace"]["name"]
    installed = installed_rows(plan["host"], marketplace)
    actual = {item["id"]: item["version"] for item in installed}
    desired = desired_from_plan(plan)
    ready = all(actual.get(item["id"]) == item["version"] for item in desired)
    return {"ready": ready, "desired": desired, "installed": installed}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("profile", type=Path)
    plan_parser.add_argument("--host", choices=("codex", "claude-code"), required=True)
    plan_parser.add_argument("--source", default=DEFAULT_SOURCE)
    plan_parser.add_argument("--ref", required=True)
    plan_parser.add_argument("--marketplace", default=DEFAULT_MARKETPLACE)
    plan_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    plan_parser.add_argument("--output", type=Path, required=True)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("plan", type=Path)
    apply_parser.add_argument("--state", type=Path, required=True)
    apply_parser.add_argument("--confirmed-by-user", action="store_true")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("plan", type=Path)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("state", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "plan":
            plan = make_plan(load_object(args.profile), load_object(args.catalog), args.host, args.source, args.ref, args.marketplace)
            write_json_atomic(args.output, plan)
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        if args.command == "apply":
            if not args.confirmed_by_user:
                raise BootstrapError("installation requires explicit user confirmation")
            state = apply_plan(load_object(args.plan), args.state)
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] == "ready" else 1
        if args.command == "verify":
            result = verify_plan(load_object(args.plan))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["ready"] else 1
        print(json.dumps(load_object(args.state), indent=2, ensure_ascii=False))
        return 0
    except (BootstrapError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
