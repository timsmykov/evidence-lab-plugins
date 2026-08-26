#!/usr/bin/env python3
"""Build and verify immutable Evidence Lab release locks and notes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
CATALOG = ROOT / "packs/core/evidence-lab-core/catalog/packs.json"
SCHEMA = ROOT / "schemas/release-lock.schema.json"
CODEX_MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
DEFAULT_REPOSITORY = "timsmykov/evidence-lab-plugins"
TAG_PATTERN = re.compile(r"^release-[0-9]{4}\.(?:0[1-9]|1[0-2])\.[1-9][0-9]*$")
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


class ReleaseError(RuntimeError):
    pass


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ReleaseError(f"git {' '.join(args)} failed")
    return result.stdout.strip()


def assert_release_source(commit: str, require_main: bool) -> None:
    if git("status", "--porcelain"):
        raise ReleaseError("release source must be a clean worktree")
    if git("rev-parse", "HEAD") != commit:
        raise ReleaseError("release source commit must equal HEAD")
    if require_main:
        if git("rev-parse", "origin/main") != commit:
            raise ReleaseError("release snapshot commit must equal the current origin/main tip")


def release_tag_order(tag: str) -> tuple[int, int, int]:
    if not TAG_PATTERN.fullmatch(tag):
        raise ReleaseError("release tag must match release-YYYY.MM.N")
    year, month, sequence = tag.removeprefix("release-").split(".")
    return int(year), int(month), int(sequence)


def assert_newest_release_tag(tag: str) -> None:
    current = release_tag_order(tag)
    previous = [
        candidate for candidate in git("tag", "--list", "release-*").splitlines()
        if candidate != tag and TAG_PATTERN.fullmatch(candidate)
    ]
    if previous and current <= max(release_tag_order(candidate) for candidate in previous):
        raise ReleaseError("stable release tag must be newer than every existing stable release tag")


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    if root.is_symlink():
        raise ReleaseError(f"{root.relative_to(ROOT)}: release pack root may not be a symlink")
    digest = hashlib.sha256()
    files = [
        path for path in root.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
        and path.suffix != ".pyc"
    ]
    symlinks = [path for path in root.rglob("*") if path.is_symlink()]
    if symlinks:
        raise ReleaseError(f"{root.relative_to(ROOT)}: release packs may not contain symlinks")
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


def published_pack_roots() -> list[Path]:
    roots = []
    for pack_path in sorted(PACKS.glob("*/*/pack.json")):
        pack = load_json(pack_path)
        meta = load_json(pack_path.parent / "meta.json")
        if meta.get("status") != "reference":
            roots.append(pack_path.parent)
    return roots


def validate_pack_release_fields(root: Path, pack: dict, meta: dict) -> None:
    if not pack.get("license"):
        raise ReleaseError(f"{pack['id']}: missing license expression")
    provenance = meta.get("provenance", {})
    if not provenance.get("origin") or not provenance.get("evidence"):
        raise ReleaseError(f"{pack['id']}: incomplete provenance")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## \[([^]]+)\]", changelog, flags=re.MULTILINE)
    if not headings or headings[0] != pack["version"]:
        raise ReleaseError(f"{pack['id']}: current version is not the newest changelog entry")
    if f"## [{pack['version']}]" not in changelog:
        raise ReleaseError(f"{pack['id']}: changelog has no entry for {pack['version']}")


def build_lock(tag: str, commit: str, repository: str) -> dict:
    if not TAG_PATTERN.fullmatch(tag):
        raise ReleaseError("release tag must match release-YYYY.MM.N")
    packs = []
    for root in published_pack_roots():
        pack = load_json(root / "pack.json")
        meta = load_json(root / "meta.json")
        validate_pack_release_fields(root, pack, meta)
        packs.append({
            "id": pack["id"],
            "version": pack["version"],
            "layer": pack["layer"],
            "status": meta["status"],
            "path": root.relative_to(ROOT).as_posix(),
            "content_sha256": tree_digest(root),
            "hosts": sorted(pack["runtimes"]),
            "license": pack["license"],
        })
    expected_ids = {item["id"] for item in packs}
    codex_ids = {item["name"] for item in load_json(CODEX_MARKETPLACE)["plugins"]}
    claude_ids = {item["name"] for item in load_json(CLAUDE_MARKETPLACE)["plugins"]}
    if expected_ids != codex_ids or expected_ids != claude_ids:
        raise ReleaseError("published pack roots and host marketplaces do not match")
    return {
        "schema_version": 1,
        "release_tag": tag,
        "channel": "stable",
        "source": {"repository": repository, "commit": commit},
        "catalog_sha256": file_digest(CATALOG),
        "packs": sorted(packs, key=lambda item: item["id"]),
    }


def assert_tag_commit(tag: str, commit: str) -> None:
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if resolved.returncode or resolved.stdout.strip() != commit:
        raise ReleaseError("release tag does not exist or does not point to the locked commit")


def validate_lock(lock: dict, require_tag: bool = True) -> None:
    errors = sorted(Draft202012Validator(load_json(SCHEMA)).iter_errors(lock), key=lambda error: list(error.path))
    if errors:
        raise ReleaseError(f"release lock schema: {errors[0].message}")
    if git("rev-parse", "HEAD") != lock["source"]["commit"]:
        raise ReleaseError("release lock source commit does not match HEAD")
    if require_tag:
        assert_tag_commit(lock["release_tag"], lock["source"]["commit"])
    expected = build_lock(lock["release_tag"], lock["source"]["commit"], lock["source"]["repository"])
    if lock != expected:
        raise ReleaseError("release lock does not match repository pack contents")


def release_notes(lock: dict) -> str:
    lines = [
        f"# Evidence Lab {lock['release_tag']}",
        "",
        f"Immutable source: `{lock['source']['commit']}`",
        "",
        "| Pack | Version | Status | Hosts | Content SHA-256 |",
        "|---|---:|---|---|---|",
    ]
    for pack in lock["packs"]:
        lines.append(
            f"| `{pack['id']}` | `{pack['version']}` | {pack['status']} | "
            f"{', '.join(pack['hosts'])} | `{pack['content_sha256']}` |"
        )
    lines.extend([
        "",
        "This release lock is the machine-readable source of truth. Draft packs are included for reproducibility but remain clearly marked as draft.",
        "",
        "## Pack changelogs",
        "",
    ])
    for pack in lock["packs"]:
        changelog = (ROOT / pack["path"] / "CHANGELOG.md").read_text(encoding="utf-8")
        heading = f"## [{pack['version']}]"
        start = changelog.find(heading)
        if start < 0:
            raise ReleaseError(f"{pack['id']}: changelog entry disappeared while building notes")
        end = changelog.find("\n## [", start + len(heading))
        section = changelog[start:end if end >= 0 else None].strip()
        lines.extend([f"### {pack['id']} {pack['version']}", "", *section.splitlines()[1:], ""])
    return "\n".join(lines)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--tag", required=True)
    build.add_argument("--commit")
    build.add_argument("--repository", default=DEFAULT_REPOSITORY)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--notes", type=Path)
    build.add_argument("--require-main", action="store_true")
    verify = subparsers.add_parser("verify")
    verify.add_argument("lock", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            commit = args.commit or git("rev-parse", "HEAD")
            assert_release_source(commit, args.require_main)
            if args.require_main:
                assert_newest_release_tag(args.tag)
            lock = build_lock(args.tag, commit, args.repository)
            validate_lock(lock)
            write(args.output, json.dumps(lock, indent=2, ensure_ascii=False) + "\n")
            if args.notes:
                write(args.notes, release_notes(lock))
            print(f"built {args.tag}: {len(lock['packs'])} packs")
            return 0
        lock = load_json(args.lock)
        assert_release_source(lock["source"]["commit"], False)
        validate_lock(lock)
        print(f"verified {lock['release_tag']}: {len(lock['packs'])} packs")
        return 0
    except (ReleaseError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
