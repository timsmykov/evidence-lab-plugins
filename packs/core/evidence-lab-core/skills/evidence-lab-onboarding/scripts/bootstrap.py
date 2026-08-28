#!/usr/bin/env python3
"""Plan, apply, and verify an Evidence Lab installation for Codex or Claude Code."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
REPO_ROOT = HERE.parents[6]
DEFAULT_CATALOG = PACK_ROOT / "catalog" / "packs.json"
DEFAULT_SOURCE = "timsmykov/evidence-lab-plugins"
DEFAULT_MARKETPLACE = "evidence-lab-plugins"


class BootstrapError(RuntimeError):
    pass


SAFE_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_REF = re.compile(r"^[A-Za-z0-9._/-]+$")
RELEASE_TAG = re.compile(r"^release-[0-9]{4}[.](?:0[1-9]|1[0-2])[.][1-9][0-9]*$")


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def render_recommendation(plan: dict, locale: str, output: Path) -> str:
    renderer_path = REPO_ROOT / "scripts" / "render_plan.py"
    if not renderer_path.exists():
        raise BootstrapError("canonical recommendation renderer is unavailable")
    spec = importlib.util.spec_from_file_location("evidence_lab_plan_renderer", renderer_path)
    if spec is None or spec.loader is None:
        raise BootstrapError("canonical recommendation renderer could not be loaded")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    try:
        rendered = renderer.render(plan, renderer.load_copy(locale))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BootstrapError(f"canonical recommendation could not be rendered: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, output)
    return rendered


def plan_id_for(host: str, source: str, ref: str, selection_plan: dict, release: dict | None = None) -> str:
    identity_value = {"host": host, "source": source, "ref": ref, "selection_plan": selection_plan}
    if release is not None:
        identity_value["release"] = release
    identity = json.dumps(
        identity_value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(identity).hexdigest()[:16]


def make_plan(
    profile: dict,
    catalog: dict,
    host: str,
    source: str,
    ref: str,
    marketplace: str,
    release: dict | None = None,
) -> dict:
    selection_plan = select(profile, catalog)
    plan_id = plan_id_for(host, source, ref, selection_plan, release)
    operations = [{"action": "ensure-marketplace", "target": marketplace}]
    operations.extend(
        {"action": "install-pack", "target": pack["id"], "version": pack["version"]}
        for pack in selection_plan["packs"]
    )
    plan = {
        "schema_version": 1,
        "plan_id": plan_id,
        "host": host,
        "marketplace": {"name": marketplace, "source": source, "ref": ref},
        "selection_plan": selection_plan,
        "operations": operations,
    }
    if release is not None:
        plan["release"] = release
    return plan


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise BootstrapError(f"host executable not found: {command[0]}") from exc


def run_checked(command: list[str], label: str) -> str:
    result = run(command)
    if result.returncode:
        detail = safe_process_detail(result)
        suffix = f": {detail}" if detail else ""
        raise BootstrapError(f"{label} failed with exit code {result.returncode}{suffix}")
    return result.stdout


def safe_process_detail(result: subprocess.CompletedProcess[str]) -> str:
    lowered = (result.stderr or "").casefold()
    if any(term in lowered for term in ("unauthorized", "forbidden", "permission", "authentication")):
        return "host authentication or permission was denied"
    if any(term in lowered for term in ("not found", "unknown plugin", "unknown marketplace")):
        return "requested plugin or marketplace was not found"
    if any(term in lowered for term in ("version", "downgrade", "incompatible")):
        return "host could not apply the requested plugin version"
    if any(term in lowered for term in ("network", "timeout", "timed out", "connection")):
        return "host network request failed or timed out"
    return "host command returned an error; inspect host logs"


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


def marketplace_remove_command(host: str, name: str) -> list[str]:
    if host == "codex":
        return ["codex", "plugin", "marketplace", "remove", name, "--json"]
    return ["claude", "plugin", "marketplace", "remove", name, "--scope", "user"]


def is_local_source(source: str) -> bool:
    return source.startswith(("/", "."))


def install_command(host: str, pack_id: str, marketplace: str) -> list[str]:
    selector = f"{pack_id}@{marketplace}"
    if host == "codex":
        return ["codex", "plugin", "add", selector, "--json"]
    return ["claude", "plugin", "install", selector, "--scope", "user"]


def update_command(host: str, pack_id: str, marketplace: str) -> list[str]:
    selector = f"{pack_id}@{marketplace}"
    if host == "codex":
        return ["codex", "plugin", "add", selector, "--json"]
    return ["claude", "plugin", "update", selector, "--scope", "user"]


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
        if row_marketplace != marketplace:
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
    candidates = [
        row.get("repo"),
        row.get("source"),
        row.get("url"),
        row.get("path"),
        row.get("installLocation"),
    ]
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


def normalized_snapshot(rows: list[dict]) -> list[dict]:
    return sorted(
        ({"id": str(item["id"]), "version": str(item["version"])} for item in rows),
        key=lambda item: item["id"],
    )


def snapshot_digest(rows: list[dict]) -> str:
    rendered = json.dumps(normalized_snapshot(rows), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(rendered).hexdigest()


def reconcile_plan_id(payload: dict) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(rendered).hexdigest()[:16]


def object_digest(value: dict) -> str:
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(rendered).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_tree_digest(root: Path) -> str:
    if root.is_symlink() or not root.is_dir() or REPO_ROOT not in root.resolve().parents:
        raise BootstrapError("release lock contains an unsafe pack path")
    entries = list(root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        raise BootstrapError("release pack trees may not contain symlinks")
    files = [
        path for path in entries
        if path.is_file()
        and "__pycache__" not in path.relative_to(root).parts
        and path.suffix != ".pyc"
        and path.name != ".DS_Store"
    ]
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        executable = b"1" if os.access(path, os.X_OK) else b"0"
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(executable)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def resolve_git_commit(ref: str) -> str:
    if not SAFE_REF.fullmatch(ref):
        raise BootstrapError("release ref contains unsupported characters")
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{ref}^{{commit}}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if resolved.returncode or not re.fullmatch(r"[a-f0-9]{40}", resolved.stdout.strip()):
        raise BootstrapError("requested release tag is not available in the checked-out repository")
    return resolved.stdout.strip()


def release_identity(lock: dict, ref: str, source: str, selection_plan: dict, catalog_path: Path) -> dict:
    if set(lock) != {"schema_version", "release_tag", "channel", "source", "catalog_sha256", "packs"}:
        raise BootstrapError("release lock contains unsupported or missing fields")
    if not RELEASE_TAG.fullmatch(ref):
        raise BootstrapError("stable release ref must match release-YYYY.MM.N with a valid month and sequence")
    if lock.get("schema_version") != 1 or lock.get("release_tag") != ref or lock.get("channel") != "stable":
        raise BootstrapError("release lock identity does not match the requested stable release tag")
    lock_source = lock.get("source")
    if not isinstance(lock_source, dict) or set(lock_source) != {"repository", "commit"}:
        raise BootstrapError("release lock source contains unsupported or missing fields")
    if canonical_source(str(lock_source.get("repository", ""))) != canonical_source(source):
        raise BootstrapError("release lock repository does not match the requested source")
    commit = lock_source.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise BootstrapError("release lock contains an invalid source commit")
    checkout = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if checkout.returncode or checkout.stdout.strip() != commit:
        raise BootstrapError("checked-out repository commit does not match the release lock")
    if resolve_git_commit(ref) != commit:
        raise BootstrapError("requested release tag does not point to the release lock commit")
    if lock.get("catalog_sha256") != file_sha256(catalog_path):
        raise BootstrapError("release lock does not match the selected pack catalog")
    catalog = load_object(catalog_path)
    expected_ids = {item["id"] for item in catalog.get("packs", [])}
    lock_rows = lock.get("packs", [])
    if not isinstance(lock_rows, list) or not lock_rows:
        raise BootstrapError("release lock contains no packs")
    if lock_rows != sorted(lock_rows, key=lambda item: str(item.get("id", "")) if isinstance(item, dict) else ""):
        raise BootstrapError("release lock pack entries are not in canonical ID order")
    locked = {}
    locked_paths = set()
    for item in lock_rows:
        expected_fields = {"id", "version", "layer", "status", "path", "content_sha256", "hosts", "license"}
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise BootstrapError("release lock contains unsupported or missing pack fields")
        if not SAFE_IDENTIFIER.fullmatch(str(item.get("id", ""))):
            raise BootstrapError("release lock contains an invalid pack entry")
        pack_id = item["id"]
        if pack_id in locked:
            raise BootstrapError("release lock contains duplicate pack IDs")
        relative = item.get("path")
        if not isinstance(relative, str) or not re.fullmatch(
            r"packs/(core|workflows|domains|local)/[a-z0-9][a-z0-9-]*",
            relative,
        ):
            raise BootstrapError(f"{pack_id}: release lock contains an unsafe pack path")
        if relative in locked_paths:
            raise BootstrapError("release lock contains duplicate pack paths")
        locked_paths.add(relative)
        root = REPO_ROOT / relative
        if release_tree_digest(root) != item.get("content_sha256"):
            raise BootstrapError(f"{pack_id}: checked-out content does not match the release lock")
        pack = load_object(root / "pack.json")
        if pack.get("id") != pack_id or pack.get("version") != item.get("version"):
            raise BootstrapError(f"{pack_id}: release lock identity does not match pack.json")
        meta = load_object(root / "meta.json")
        if pack.get("layer") != item.get("layer") or meta.get("status") != item.get("status"):
            raise BootstrapError(f"{pack_id}: release lock layer or status does not match pack metadata")
        if sorted(pack.get("runtimes", [])) != item.get("hosts") or pack.get("license") != item.get("license"):
            raise BootstrapError(f"{pack_id}: release lock host or license metadata does not match pack.json")
        locked[pack_id] = item["version"]
    if set(locked) != expected_ids:
        raise BootstrapError("release lock does not contain the complete published catalog")
    for marketplace_path in (REPO_ROOT / ".agents/plugins/marketplace.json", REPO_ROOT / ".claude-plugin/marketplace.json"):
        marketplace_ids = {item["name"] for item in load_object(marketplace_path).get("plugins", [])}
        if marketplace_ids != set(locked):
            raise BootstrapError("release lock does not match a host marketplace")
    missing = [item["id"] for item in selection_plan["packs"] if locked.get(item["id"]) != item["version"]]
    if missing:
        raise BootstrapError(f"release lock does not contain selected versions: {', '.join(missing)}")
    return {
        "tag": ref,
        "channel": "stable",
        "source_commit": commit,
        "lock_digest": object_digest(lock),
    }


def validate_release_record(release: dict | None, ref: str) -> None:
    if release is None:
        raise BootstrapError("installation plan requires an immutable release identity")
    if set(release) != {"tag", "channel", "source_commit", "lock_digest"}:
        raise BootstrapError("release identity contains unsupported fields")
    if not RELEASE_TAG.fullmatch(ref) or release.get("tag") != ref or release.get("channel") != "stable":
        raise BootstrapError("release identity does not match the plan ref")
    if not re.fullmatch(r"[a-f0-9]{40}", str(release.get("source_commit", ""))):
        raise BootstrapError("release identity contains an invalid source commit")
    if not re.fullmatch(r"[a-f0-9]{64}", str(release.get("lock_digest", ""))):
        raise BootstrapError("release identity contains an invalid lock digest")


def validate_plan_release(plan: dict, release_lock: dict, catalog_path: Path) -> None:
    marketplace = plan["marketplace"]
    actual = release_identity(
        release_lock,
        marketplace["ref"],
        marketplace["source"],
        plan["selection_plan"],
        catalog_path,
    )
    if actual != plan.get("release"):
        raise BootstrapError("installation plan release identity does not match the verified release lock")


def validate_previous_release_lock(
    plan: dict,
    previous_release_lock: dict,
    *,
    include_removals: bool = False,
) -> None:
    previous_ref = plan["marketplace"].get("previous_ref")
    previous_release = plan.get("previous_release")
    if not isinstance(previous_ref, str) or not isinstance(previous_release, dict):
        raise BootstrapError("reconcile plan requires the previous immutable release identity")
    validate_release_record(previous_release, previous_ref)
    if object_digest(previous_release_lock) != previous_release["lock_digest"]:
        raise BootstrapError("previous release lock does not match the reconcile plan")
    lock_source = previous_release_lock.get("source")
    if (
        previous_release_lock.get("release_tag") != previous_ref
        or previous_release_lock.get("channel") != "stable"
        or not isinstance(lock_source, dict)
        or canonical_source(str(lock_source.get("repository", "")))
        != canonical_source(plan["marketplace"]["source"])
        or lock_source.get("commit") != previous_release["source_commit"]
    ):
        raise BootstrapError("previous release lock source identity does not match the reconcile plan")
    if resolve_git_commit(previous_ref) != previous_release["source_commit"]:
        raise BootstrapError("previous release tag no longer points to its locked commit")
    locked_versions = {
        item.get("id"): item.get("version")
        for item in previous_release_lock.get("packs", [])
        if isinstance(item, dict)
    }
    required_versions = {item["id"]: item["from_version"] for item in plan["diff"]["update"]}
    if include_removals:
        required_versions.update({item["id"]: item["version"] for item in plan["diff"]["remove_candidates"]})
    missing = [pack_id for pack_id, version in required_versions.items() if locked_versions.get(pack_id) != version]
    if missing:
        raise BootstrapError(f"previous release lock does not contain baseline versions: {', '.join(missing)}")


def make_reconcile_plan(
    profile: dict,
    catalog: dict,
    host: str,
    source: str,
    ref: str,
    marketplace: str,
    installed: list[dict],
    previous_ref: str | None = None,
    release: dict | None = None,
    previous_release: dict | None = None,
) -> dict:
    selection_plan = select(profile, catalog)
    desired = desired_from_plan({"selection_plan": selection_plan})
    baseline = normalized_snapshot(installed)
    if not baseline:
        raise BootstrapError("no existing Evidence Lab packs were found; use a clean installation plan")
    desired_by_id = {item["id"]: item["version"] for item in desired}
    installed_by_id = {item["id"]: item["version"] for item in baseline}
    add = [item for item in desired if item["id"] not in installed_by_id]
    update = [
        {"id": item["id"], "from_version": installed_by_id[item["id"]], "to_version": item["version"]}
        for item in desired
        if item["id"] in installed_by_id and installed_by_id[item["id"]] != item["version"]
    ]
    if previous_ref is None and not is_local_source(source):
        raise BootstrapError("reconciling installed packs requires the previous installation state and release ref")
    retain = [item for item in desired if installed_by_id.get(item["id"]) == item["version"]]
    extras = [item for item in baseline if item["id"] not in desired_by_id]
    operations = [{"action": "ensure-marketplace", "target": marketplace}]
    operations.extend({"action": "install-pack", "target": item["id"], "version": item["version"]} for item in add)
    operations.extend(
        {
            "action": "update-pack",
            "target": item["id"],
            "from_version": item["from_version"],
            "version": item["to_version"],
        }
        for item in update
    )
    payload = {
        "schema_version": 1,
        "host": host,
        "marketplace": {"name": marketplace, "source": source, "ref": ref, "previous_ref": previous_ref},
        "previous_release": previous_release,
        "profile_digest": object_digest(profile),
        "catalog_digest": object_digest(catalog),
        "selection_plan": selection_plan,
        "baseline": {"installed": baseline, "digest": snapshot_digest(baseline)},
        "diff": {
            "add": add,
            "update": update,
            "retain": retain,
            "retained_extra": extras,
            "remove_candidates": extras,
        },
        "operations": operations,
    }
    if release is not None:
        payload["release"] = release
    return {"plan_id": reconcile_plan_id(payload), **payload}


def expected_reconciled_snapshot(plan: dict) -> list[dict]:
    return normalized_snapshot([*desired_from_plan(plan), *plan["diff"]["retained_extra"]])


def release_for_ref(plan: dict, ref: str) -> dict:
    if ref == plan["marketplace"]["ref"]:
        return plan["release"]
    if ref == plan["marketplace"].get("previous_ref"):
        return plan["previous_release"]
    raise BootstrapError("reconcile state contains an unknown active release ref")


def validate_reconcile_plan(plan: dict) -> None:
    if plan.get("schema_version") != 1 or plan.get("host") not in {"codex", "claude-code"}:
        raise BootstrapError("unsupported reconcile plan")
    marketplace = plan.get("marketplace")
    baseline = plan.get("baseline")
    diff = plan.get("diff")
    if not all(isinstance(value, dict) for value in (marketplace, baseline, diff, plan.get("selection_plan"))):
        raise BootstrapError("reconcile plan is incomplete")
    name, source, ref = marketplace.get("name"), marketplace.get("source"), marketplace.get("ref")
    previous_ref = marketplace.get("previous_ref")
    if not all(
        isinstance(plan.get(field), str) and re.fullmatch(r"[a-f0-9]{64}", plan[field])
        for field in ("profile_digest", "catalog_digest")
    ):
        raise BootstrapError("reconcile plan contains an invalid profile or catalog digest")
    if not isinstance(name, str) or not SAFE_IDENTIFIER.fullmatch(name):
        raise BootstrapError("reconcile plan contains an unsafe marketplace name")
    if not isinstance(source, str) or not source.strip() or not isinstance(ref, str) or not SAFE_REF.fullmatch(ref):
        raise BootstrapError("reconcile plan contains an unsafe source or Git ref")
    if previous_ref is not None and (not isinstance(previous_ref, str) or not SAFE_REF.fullmatch(previous_ref)):
        raise BootstrapError("reconcile plan contains an unsafe previous Git ref")
    validate_release_record(plan.get("release"), ref)
    validate_release_record(plan.get("previous_release"), previous_ref)
    try:
        baseline_rows = normalized_snapshot(baseline.get("installed", []))
    except (KeyError, TypeError) as exc:
        raise BootstrapError("reconcile plan contains an invalid installed baseline") from exc
    if baseline.get("installed") != baseline_rows or baseline.get("digest") != snapshot_digest(baseline_rows):
        raise BootstrapError("reconcile plan baseline does not match its digest")
    payload = {key: value for key, value in plan.items() if key != "plan_id"}
    if plan.get("plan_id") != reconcile_plan_id(payload):
        raise BootstrapError("reconcile plan identity does not match its contents")
    try:
        desired = desired_from_plan(plan)
    except (KeyError, TypeError) as exc:
        raise BootstrapError("reconcile plan contains an invalid selection") from exc
    if not desired or len({item["id"] for item in desired}) != len(desired):
        raise BootstrapError("reconcile plan contains no packs or duplicate packs")
    if any(not SAFE_IDENTIFIER.fullmatch(item["id"]) or not item["version"] for item in desired):
        raise BootstrapError("reconcile plan contains an unsafe pack identity")
    baseline_by_id = {item["id"]: item["version"] for item in baseline_rows}
    desired_by_id = {item["id"]: item["version"] for item in desired}
    expected_diff = {
        "add": [item for item in desired if item["id"] not in baseline_by_id],
        "update": [
            {"id": item["id"], "from_version": baseline_by_id[item["id"]], "to_version": item["version"]}
            for item in desired
            if item["id"] in baseline_by_id and baseline_by_id[item["id"]] != item["version"]
        ],
        "retain": [item for item in desired if baseline_by_id.get(item["id"]) == item["version"]],
        "retained_extra": [item for item in baseline_rows if item["id"] not in desired_by_id],
        "remove_candidates": [item for item in baseline_rows if item["id"] not in desired_by_id],
    }
    if diff != expected_diff:
        raise BootstrapError("reconcile plan diff does not match desired and installed packs")
    expected_operations = [{"action": "ensure-marketplace", "target": name}]
    expected_operations.extend({"action": "install-pack", "target": item["id"], "version": item["version"]} for item in expected_diff["add"])
    expected_operations.extend(
        {"action": "update-pack", "target": item["id"], "from_version": item["from_version"], "version": item["to_version"]}
        for item in expected_diff["update"]
    )
    if plan.get("operations") != expected_operations:
        raise BootstrapError("reconcile operations do not match its diff")


def initial_reconcile_state(plan: dict) -> dict:
    operations = [
        {"action": item["action"], "target": item["target"], "status": "pending"}
        for item in plan["operations"]
    ]
    operations.extend(
        {"action": "remove-pack", "target": item["id"], "status": "pending"}
        for item in plan["diff"]["remove_candidates"]
    )
    return {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "host": plan["host"],
        "marketplace": plan["marketplace"],
        "release": release_for_ref(plan, plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"]),
        "active_ref": plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"],
        "status": "planned",
        "desired": normalized_snapshot(desired_from_plan(plan)),
        "pre_change_snapshot": plan["baseline"],
        "installed_after": plan["baseline"]["installed"],
        "diff": plan["diff"],
        "operations": operations,
        "removal_approved": False,
        "recovery_action": None,
        "error": None,
    }


def validate_reconcile_state(state: dict, plan: dict) -> None:
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise BootstrapError("unsupported reconcile state")
    if state.get("plan_id") != plan["plan_id"] or state.get("host") != plan["host"]:
        raise BootstrapError("reconcile state does not belong to this plan and host")
    if state.get("marketplace") != plan["marketplace"]:
        raise BootstrapError("reconcile state marketplace does not match its plan")
    if state.get("active_ref") not in {plan["marketplace"]["ref"], plan["marketplace"].get("previous_ref")}:
        raise BootstrapError("reconcile state contains an unknown active release ref")
    if state.get("release") != release_for_ref(plan, state["active_ref"]):
        raise BootstrapError("reconcile state release identity does not match its active ref")
    if state.get("diff") != plan["diff"] or state.get("desired") != normalized_snapshot(desired_from_plan(plan)):
        raise BootstrapError("reconcile state desired packs or diff do not match its plan")
    expected_operations = [
        {"action": item["action"], "target": item["target"]}
        for item in plan["operations"]
    ]
    expected_operations.extend(
        {"action": "remove-pack", "target": item["id"]}
        for item in plan["diff"]["remove_candidates"]
    )
    actual_operations = [
        {"action": item.get("action"), "target": item.get("target")}
        for item in state.get("operations", [])
        if isinstance(item, dict)
    ]
    if actual_operations != expected_operations:
        raise BootstrapError("reconcile state operations do not match its plan")
    snapshot = state.get("pre_change_snapshot")
    if not isinstance(snapshot, dict):
        raise BootstrapError("reconcile state has no pre-change snapshot")
    try:
        installed = normalized_snapshot(snapshot.get("installed", []))
        installed_after = normalized_snapshot(state.get("installed_after", []))
    except (KeyError, TypeError) as exc:
        raise BootstrapError("reconcile state contains an invalid installed snapshot") from exc
    if snapshot.get("installed") != installed or snapshot.get("digest") != snapshot_digest(installed):
        raise BootstrapError("reconcile state pre-change snapshot does not match its digest")
    if snapshot != plan["baseline"]:
        raise BootstrapError("reconcile state pre-change snapshot does not match its plan baseline")
    if state.get("installed_after") != installed_after:
        raise BootstrapError("reconcile state installed readback is not normalized")
    if any(not SAFE_IDENTIFIER.fullmatch(item["id"]) or not item["version"] for item in [*installed, *installed_after]):
        raise BootstrapError("reconcile state contains an unsafe pack identity")
    stable_expected_refs = {
        "ready": plan["marketplace"]["ref"],
        "removed": plan["marketplace"]["ref"],
        "restored": plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"],
        "failed": plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"],
    }
    if state.get("status") in stable_expected_refs and state["active_ref"] != stable_expected_refs[state["status"]]:
        raise BootstrapError("reconcile state status does not match its active release ref")


def previous_ref_from_state(
    previous_state: dict,
    previous_plan: dict,
    host: str,
    marketplace_name: str,
    source: str,
) -> str:
    if not isinstance(previous_plan, dict):
        raise BootstrapError("reconciliation requires the matching previous plan")
    if "baseline" in previous_plan:
        validate_reconcile_plan(previous_plan)
        validate_reconcile_state(previous_state, previous_plan)
    else:
        validate_plan(previous_plan)
        if previous_state.get("plan_id") != previous_plan.get("plan_id"):
            raise BootstrapError("installation state does not match the previous installation plan")
        if previous_state.get("status") != "ready":
            raise BootstrapError("previous installation state is not ready; recover it before reconciliation")
    previous_marketplace = previous_state.get("marketplace")
    if not isinstance(previous_marketplace, dict):
        previous_marketplace = previous_plan["marketplace"]
    if previous_state.get("host") != host or previous_marketplace.get("name") != marketplace_name:
        raise BootstrapError("previous state does not match the requested host and marketplace")
    if not source_matches(previous_marketplace, source):
        raise BootstrapError("previous state does not match the requested marketplace source")
    previous_ref = previous_state.get("active_ref") or previous_marketplace.get("ref")
    if not isinstance(previous_ref, str) or not SAFE_REF.fullmatch(previous_ref):
        raise BootstrapError("previous state has no safe release ref")
    return previous_ref


def previous_release_from_state(previous_state: dict, previous_plan: dict, previous_ref: str) -> dict:
    expected = (
        release_for_ref(previous_plan, previous_ref)
        if "baseline" in previous_plan
        else previous_plan.get("release")
    )
    actual = previous_state.get("release")
    if actual != expected:
        raise BootstrapError("previous state release identity does not match its active saved-plan ref")
    validate_release_record(actual, previous_ref)
    return actual


def initial_state(plan: dict) -> dict:
    return {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "host": plan["host"],
        "marketplace": plan["marketplace"],
        "release": plan.get("release"),
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
    validate_release_record(plan.get("release"), ref)
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
    expected_id = plan_id_for(plan["host"], source, ref, selection_plan, plan.get("release"))
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


def apply_plan(plan: dict, state_path: Path, release_lock: dict, catalog_path: Path = DEFAULT_CATALOG) -> dict:
    validate_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
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


def assert_live_snapshot(plan: dict, expected_digest: str, label: str) -> list[dict]:
    installed = installed_rows(plan["host"], plan["marketplace"]["name"])
    if snapshot_digest(installed) != expected_digest:
        raise BootstrapError(f"stale reconcile plan: installed state changed before {label}")
    return installed


def pin_reconcile_marketplace(plan: dict, state: dict, target_ref: str, *, force_repin: bool = False) -> None:
    host = plan["host"]
    marketplace = plan["marketplace"]
    existing = next((row for row in marketplace_rows(host) if row.get("name") == marketplace["name"]), None)
    try:
        if existing and not source_matches(existing, marketplace["source"]):
            raise BootstrapError(f"marketplace {marketplace['name']} already points to another source")
        if is_local_source(marketplace["source"]):
            if not existing:
                run_checked(marketplace_add_command(host, marketplace["source"], target_ref), "marketplace setup")
        elif existing and (force_repin or marketplace.get("previous_ref") != target_ref):
            run_checked(marketplace_remove_command(host, marketplace["name"]), "marketplace unpin")
            run_checked(marketplace_add_command(host, marketplace["source"], target_ref), "marketplace repin")
        elif existing:
            run_checked(marketplace_update_command(host, marketplace["name"]), "marketplace update")
        else:
            run_checked(marketplace_add_command(host, marketplace["source"], target_ref), "marketplace setup")
        state["operations"][0]["status"] = "completed"
        state["active_ref"] = target_ref
        state["release"] = release_for_ref(plan, target_ref)
    except BootstrapError:
        state["operations"][0]["status"] = "failed"
        raise


def restore_snapshot(plan: dict, target: list[dict], state: dict | None = None) -> tuple[list[dict], bool, list[str]]:
    host = plan["host"]
    marketplace = plan["marketplace"]["name"]
    target_by_id = {item["id"]: item["version"] for item in target}
    failed = False
    errors: list[str] = []
    previous_ref = plan["marketplace"].get("previous_ref")
    if previous_ref and previous_ref != plan["marketplace"]["ref"]:
        restore_state = state if state is not None else {"operations": [{"status": "pending"}]}
        try:
            pin_reconcile_marketplace(plan, restore_state, previous_ref, force_repin=True)
        except BootstrapError as exc:
            return installed_rows(host, marketplace), True, [str(exc)]
    current = installed_rows(host, marketplace)
    current_by_id = {item["id"]: item["version"] for item in current}
    for pack_id in sorted(set(current_by_id) - set(target_by_id), reverse=True):
        result = run(remove_command(host, pack_id, marketplace))
        if result.returncode:
            failed = True
            errors.append(f"remove {pack_id}: {safe_process_detail(result) or f'exit {result.returncode}'}")
    current = installed_rows(host, marketplace)
    current_by_id = {item["id"]: item["version"] for item in current}
    for pack_id, version in sorted(target_by_id.items()):
        if current_by_id.get(pack_id) == version:
            continue
        command = update_command(host, pack_id, marketplace) if pack_id in current_by_id else install_command(host, pack_id, marketplace)
        result = run(command)
        if result.returncode:
            failed = True
            errors.append(f"restore {pack_id}: {safe_process_detail(result) or f'exit {result.returncode}'}")
    restored = installed_rows(host, marketplace)
    return restored, failed or restored != normalized_snapshot(target), errors


def mark_rolled_back_operations(state: dict, plan: dict) -> None:
    baseline = {item["id"]: item["version"] for item in plan["baseline"]["installed"]}
    actual = {item["id"]: item["version"] for item in state["installed_after"]}
    previous_ref = plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"]
    for operation in state["operations"]:
        if operation["status"] != "completed":
            continue
        action, target = operation["action"], operation["target"]
        if action == "ensure-marketplace" and state["active_ref"] == previous_ref:
            operation["status"] = "rolled-back"
        elif action == "install-pack" and target not in baseline and target not in actual:
            operation["status"] = "rolled-back"
        elif action == "update-pack" and actual.get(target) == baseline.get(target):
            operation["status"] = "rolled-back"
        elif action == "remove-pack" and actual.get(target) == baseline.get(target):
            operation["status"] = "rolled-back"


def apply_reconcile_plan(
    plan: dict,
    state_path: Path,
    profile: dict,
    catalog: dict,
    release_lock: dict,
    previous_release_lock: dict,
    catalog_path: Path = DEFAULT_CATALOG,
) -> dict:
    validate_reconcile_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
    validate_previous_release_lock(plan, previous_release_lock)
    if plan["profile_digest"] != object_digest(profile) or plan["catalog_digest"] != object_digest(catalog):
        raise BootstrapError("stale reconcile plan: profile or release catalog changed before apply")
    assert_live_snapshot(plan, plan["baseline"]["digest"], "apply")
    state = initial_reconcile_state(plan)
    state["status"] = "applying"
    state["recovery_action"] = "apply"
    write_json_atomic(state_path, state)
    host = plan["host"]
    marketplace = plan["marketplace"]["name"]
    try:
        pin_reconcile_marketplace(plan, state, plan["marketplace"]["ref"])
        write_json_atomic(state_path, state)
        for index, operation in enumerate(plan["operations"][1:], 1):
            command = (
                install_command(host, operation["target"], marketplace)
                if operation["action"] == "install-pack"
                else update_command(host, operation["target"], marketplace)
            )
            try:
                run_checked(command, f"{operation['action']} {operation['target']}")
            except BootstrapError:
                state["operations"][index]["status"] = "failed"
                raise
            state["operations"][index]["status"] = "completed"
            write_json_atomic(state_path, state)
        state["installed_after"] = installed_rows(host, marketplace)
        expected = expected_reconciled_snapshot(plan)
        if state["installed_after"] != expected:
            raise BootstrapError("reconcile readback did not exactly match desired packs plus retained extras")
        state["status"] = "ready"
        state["recovery_action"] = None
        state["error"] = None
    except BootstrapError as exc:
        state["error"] = str(exc)
        restored, restore_failed, restore_errors = restore_snapshot(plan, plan["baseline"]["installed"], state)
        state["installed_after"] = restored
        mark_rolled_back_operations(state, plan)
        state["status"] = "partial" if restore_failed else "failed"
        if restore_errors:
            state["error"] = f"{state['error']}; restore: {'; '.join(restore_errors)}"
        state["recovery_action"] = None
    write_json_atomic(state_path, state)
    return state


def remove_reconcile_extras(
    plan: dict,
    state_path: Path,
    profile: dict,
    catalog: dict,
    release_lock: dict,
    previous_release_lock: dict,
    catalog_path: Path = DEFAULT_CATALOG,
) -> dict:
    validate_reconcile_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
    validate_previous_release_lock(plan, previous_release_lock, include_removals=True)
    if plan["profile_digest"] != object_digest(profile) or plan["catalog_digest"] != object_digest(catalog):
        raise BootstrapError("stale removal plan: profile or release catalog changed before removal")
    state = load_object(state_path)
    validate_reconcile_state(state, plan)
    if state.get("status") != "ready":
        raise BootstrapError("removal requires a ready state for the same reconcile plan")
    expected = expected_reconciled_snapshot(plan)
    assert_live_snapshot(plan, snapshot_digest(expected), "removal")
    state["status"] = "removing"
    state["removal_approved"] = True
    state["recovery_action"] = "remove"
    write_json_atomic(state_path, state)
    try:
        pin_reconcile_marketplace(
            plan,
            state,
            plan["marketplace"]["ref"],
            force_repin=not is_local_source(plan["marketplace"]["source"]),
        )
    except BootstrapError as exc:
        state["status"] = "interrupted"
        state["error"] = f"marketplace preparation failed before removal: {exc}"
        write_json_atomic(state_path, state)
        raise
    write_json_atomic(state_path, state)
    marketplace = plan["marketplace"]["name"]
    failed = False
    removal_errors: list[str] = []
    for item in plan["diff"]["remove_candidates"]:
        operation = next(
            row for row in state["operations"]
            if row["action"] == "remove-pack" and row["target"] == item["id"]
        )
        result = run(remove_command(plan["host"], item["id"], marketplace))
        operation["status"] = "failed" if result.returncode else "completed"
        failed = failed or bool(result.returncode)
        if result.returncode:
            removal_errors.append(f"remove {item['id']}: {safe_process_detail(result) or f'exit {result.returncode}'}")
        write_json_atomic(state_path, state)
    state["installed_after"] = installed_rows(plan["host"], marketplace)
    desired = normalized_snapshot(desired_from_plan(plan))
    if failed or state["installed_after"] != desired:
        state["status"] = "partial"
        detail = f": {'; '.join(removal_errors)}" if removal_errors else ""
        state["error"] = f"removal readback did not exactly match the desired pack set{detail}"
    else:
        state["status"] = "removed"
        state["error"] = None
    state["recovery_action"] = None
    write_json_atomic(state_path, state)
    return state


def restore_reconcile_state(
    plan: dict,
    state_path: Path,
    release_lock: dict,
    previous_release_lock: dict,
    catalog_path: Path = DEFAULT_CATALOG,
) -> dict:
    validate_reconcile_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
    validate_previous_release_lock(plan, previous_release_lock, include_removals=True)
    state = load_object(state_path)
    validate_reconcile_state(state, plan)
    assert_live_snapshot(plan, snapshot_digest(state.get("installed_after", [])), "restore")
    state["status"] = "restoring"
    state["recovery_action"] = "restore"
    write_json_atomic(state_path, state)
    restored, failed, restore_errors = restore_snapshot(plan, state["pre_change_snapshot"]["installed"], state)
    state["installed_after"] = restored
    mark_rolled_back_operations(state, plan)
    state["status"] = "partial" if failed else "restored"
    detail = f": {'; '.join(restore_errors)}" if restore_errors else ""
    state["error"] = f"host could not restore the exact pre-change versions{detail}" if failed else None
    state["recovery_action"] = None
    write_json_atomic(state_path, state)
    return state


def recover_reconcile_state(
    plan: dict,
    state_path: Path,
    release_lock: dict,
    previous_release_lock: dict,
    catalog_path: Path = DEFAULT_CATALOG,
) -> dict:
    validate_reconcile_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
    validate_previous_release_lock(plan, previous_release_lock)
    state = load_object(state_path)
    validate_reconcile_state(state, plan)
    interrupted_status = state.get("status")
    if interrupted_status not in {"applying", "removing", "restoring", "interrupted"}:
        return state
    recovery_action = state.get("recovery_action") or (
        "restore" if interrupted_status == "restoring" else "remove" if interrupted_status == "removing" else "apply"
    )
    if recovery_action in {"remove", "restore"}:
        validate_previous_release_lock(plan, previous_release_lock, include_removals=True)
    target_ref = (
        plan["marketplace"].get("previous_ref") or plan["marketplace"]["ref"]
        if recovery_action == "restore"
        else plan["marketplace"]["ref"]
    )
    try:
        pin_reconcile_marketplace(plan, state, target_ref, force_repin=not is_local_source(plan["marketplace"]["source"]))
    except BootstrapError as exc:
        state["status"] = "interrupted"
        state["recovery_action"] = recovery_action
        state["error"] = f"marketplace recovery failed: {exc}"
        write_json_atomic(state_path, state)
        return state
    live = installed_rows(plan["host"], plan["marketplace"]["name"])
    state["installed_after"] = live
    if live == normalized_snapshot(state["pre_change_snapshot"]["installed"]):
        state["status"] = "restored" if recovery_action == "restore" else "failed"
        state["error"] = None
        mark_rolled_back_operations(state, plan)
    elif live == normalized_snapshot(desired_from_plan(plan)) and state.get("removal_approved"):
        state["status"] = "removed"
        state["error"] = None
    elif live == expected_reconciled_snapshot(plan):
        state["status"] = "ready"
        state["error"] = None
    else:
        state["status"] = "interrupted"
        state["error"] = "interrupted run requires explicit restore before retry"
        state["recovery_action"] = recovery_action
        write_json_atomic(state_path, state)
        return state
    state["recovery_action"] = None
    write_json_atomic(state_path, state)
    return state


def verify_plan(plan: dict, release_lock: dict, catalog_path: Path = DEFAULT_CATALOG) -> dict:
    validate_plan(plan)
    validate_plan_release(plan, release_lock, catalog_path)
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
    plan_parser.add_argument("--release-lock", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--locale", choices=("en", "ru"))
    plan_parser.add_argument("--recommendation", type=Path)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("plan", type=Path)
    apply_parser.add_argument("--state", type=Path, required=True)
    apply_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    apply_parser.add_argument("--release-lock", type=Path, required=True)
    apply_parser.add_argument("--confirmed-by-user", action="store_true")

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("profile", type=Path)
    reconcile_parser.add_argument("--host", choices=("codex", "claude-code"), required=True)
    reconcile_parser.add_argument("--source", default=DEFAULT_SOURCE)
    reconcile_parser.add_argument("--ref", required=True)
    reconcile_parser.add_argument("--marketplace", default=DEFAULT_MARKETPLACE)
    reconcile_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    reconcile_parser.add_argument("--release-lock", type=Path, required=True)
    reconcile_parser.add_argument("--previous-release-lock", type=Path, required=True)
    reconcile_parser.add_argument("--previous-state", type=Path, required=True)
    reconcile_parser.add_argument("--previous-plan", type=Path, required=True)
    reconcile_parser.add_argument("--output", type=Path, required=True)

    reconcile_apply_parser = subparsers.add_parser("apply-reconcile")
    reconcile_apply_parser.add_argument("plan", type=Path)
    reconcile_apply_parser.add_argument("--state", type=Path, required=True)
    reconcile_apply_parser.add_argument("--profile", type=Path, required=True)
    reconcile_apply_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    reconcile_apply_parser.add_argument("--release-lock", type=Path, required=True)
    reconcile_apply_parser.add_argument("--previous-release-lock", type=Path, required=True)
    reconcile_apply_parser.add_argument("--confirmed-by-user", action="store_true")

    remove_parser = subparsers.add_parser("remove-extras")
    remove_parser.add_argument("plan", type=Path)
    remove_parser.add_argument("--state", type=Path, required=True)
    remove_parser.add_argument("--profile", type=Path, required=True)
    remove_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    remove_parser.add_argument("--release-lock", type=Path, required=True)
    remove_parser.add_argument("--previous-release-lock", type=Path, required=True)
    remove_parser.add_argument("--confirmed-by-user", action="store_true")

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("plan", type=Path)
    restore_parser.add_argument("--state", type=Path, required=True)
    restore_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    restore_parser.add_argument("--release-lock", type=Path, required=True)
    restore_parser.add_argument("--previous-release-lock", type=Path, required=True)
    restore_parser.add_argument("--confirmed-by-user", action="store_true")

    recover_parser = subparsers.add_parser("recover")
    recover_parser.add_argument("plan", type=Path)
    recover_parser.add_argument("--state", type=Path, required=True)
    recover_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    recover_parser.add_argument("--release-lock", type=Path, required=True)
    recover_parser.add_argument("--previous-release-lock", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("plan", type=Path)
    verify_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    verify_parser.add_argument("--release-lock", type=Path, required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("state", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "plan":
            profile = load_object(args.profile)
            catalog = load_object(args.catalog)
            selection_plan = select(profile, catalog)
            release = release_identity(load_object(args.release_lock), args.ref, args.source, selection_plan, args.catalog)
            plan = make_plan(profile, catalog, args.host, args.source, args.ref, args.marketplace, release)
            write_json_atomic(args.output, plan)
            if bool(args.locale) != bool(args.recommendation):
                raise BootstrapError("--locale and --recommendation must be used together")
            if args.recommendation:
                print(render_recommendation(plan, args.locale, args.recommendation), end="")
            else:
                print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        if args.command == "apply":
            if not args.confirmed_by_user:
                raise BootstrapError("installation requires explicit user confirmation")
            state = apply_plan(load_object(args.plan), args.state, load_object(args.release_lock), args.catalog)
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] == "ready" else 1
        if args.command == "reconcile":
            installed = installed_rows(args.host, args.marketplace)
            previous_ref = None
            previous_release = None
            if args.previous_state:
                previous_state = load_object(args.previous_state)
                previous_plan = load_object(args.previous_plan)
                previous_ref = previous_ref_from_state(
                    previous_state,
                    previous_plan,
                    args.host,
                    args.marketplace,
                    args.source,
                )
                previous_release = previous_release_from_state(previous_state, previous_plan, previous_ref)
            profile = load_object(args.profile)
            catalog = load_object(args.catalog)
            selection_plan = select(profile, catalog)
            release = release_identity(load_object(args.release_lock), args.ref, args.source, selection_plan, args.catalog)
            plan = make_reconcile_plan(
                profile,
                catalog,
                args.host,
                args.source,
                args.ref,
                args.marketplace,
                installed,
                previous_ref,
                release,
                previous_release,
            )
            validate_previous_release_lock(plan, load_object(args.previous_release_lock))
            write_json_atomic(args.output, plan)
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        if args.command == "apply-reconcile":
            if not args.confirmed_by_user:
                raise BootstrapError("reconcile apply requires explicit user confirmation")
            state = apply_reconcile_plan(
                load_object(args.plan),
                args.state,
                load_object(args.profile),
                load_object(args.catalog),
                load_object(args.release_lock),
                load_object(args.previous_release_lock),
                args.catalog,
            )
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] == "ready" else 1
        if args.command == "remove-extras":
            if not args.confirmed_by_user:
                raise BootstrapError("pack removal requires separate explicit user confirmation")
            state = remove_reconcile_extras(
                load_object(args.plan),
                args.state,
                load_object(args.profile),
                load_object(args.catalog),
                load_object(args.release_lock),
                load_object(args.previous_release_lock),
                args.catalog,
            )
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] == "removed" else 1
        if args.command == "restore":
            if not args.confirmed_by_user:
                raise BootstrapError("restore requires explicit user confirmation")
            state = restore_reconcile_state(
                load_object(args.plan), args.state, load_object(args.release_lock),
                load_object(args.previous_release_lock), args.catalog,
            )
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] == "restored" else 1
        if args.command == "recover":
            state = recover_reconcile_state(
                load_object(args.plan), args.state, load_object(args.release_lock),
                load_object(args.previous_release_lock), args.catalog,
            )
            print(json.dumps(state, indent=2, ensure_ascii=False))
            return 0 if state["status"] in {"ready", "removed", "restored", "failed"} else 1
        if args.command == "verify":
            result = verify_plan(load_object(args.plan), load_object(args.release_lock), args.catalog)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["ready"] else 1
        print(json.dumps(load_object(args.state), indent=2, ensure_ascii=False))
        return 0
    except (BootstrapError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
