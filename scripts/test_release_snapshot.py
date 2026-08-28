#!/usr/bin/env python3
"""Deterministic release-lock tests without creating a repository tag."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/release_snapshot.py"
SCHEMA = ROOT / "schemas/release-lock.schema.json"
BOOTSTRAP = ROOT / "packs/core/evidence-lab-core/skills/evidence-lab-onboarding/scripts/bootstrap.py"
BOOTSTRAP_DIR = BOOTSTRAP.parent
CATALOG = ROOT / "packs/core/evidence-lab-core/catalog/packs.json"
PROFILE = ROOT / "tests/fixtures/onboarding/quantitative-full-cycle.profile.json"
sys.dont_write_bytecode = True
sys.path.insert(0, str(BOOTSTRAP_DIR))


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_lab_release_snapshot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("evidence_lab_release_bootstrap", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def unused_release_tag(module) -> str:
    """Return a valid stable tag that is guaranteed to be absent in this clone."""
    existing = set(module.git("tag", "--list", "release-*").splitlines())
    sequence = 999_999
    while True:
        candidate = f"release-9999.12.{sequence}"
        if candidate not in existing:
            return candidate
        sequence += 1


def main() -> int:
    module = load_module()
    commit = module.git("rev-parse", "HEAD")
    absent_tag = unused_release_tag(module)
    first = module.build_lock(absent_tag, commit, module.DEFAULT_REPOSITORY)
    second = module.build_lock(absent_tag, commit, module.DEFAULT_REPOSITORY)
    assert first == second
    assert len(first["packs"]) == 14
    assert [item["id"] for item in first["packs"]] == sorted(item["id"] for item in first["packs"])
    assert not list(Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).iter_errors(first))
    module.validate_lock(first, require_tag=False)
    try:
        module.validate_lock(first)
    except module.ReleaseError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("standalone verifier accepted a lock without its release tag")
    for invalid_tag in ("release-2026.00.1", "release-2026.13.1", "release-2026.08.0", "v1"):
        try:
            module.build_lock(invalid_tag, commit, module.DEFAULT_REPOSITORY)
        except module.ReleaseError:
            pass
        else:
            raise AssertionError(f"invalid stable release tag was accepted: {invalid_tag}")

    real_git = module.git
    module.git = lambda *args: (
        "" if args == ("status", "--porcelain") else
        commit if args in (("rev-parse", "HEAD"), ("rev-parse", "origin/main")) else
        "release-2026.07.2\nrelease-2026.08.1" if args == ("tag", "--list", "release-*") else
        real_git(*args)
    )
    module.assert_release_source(commit, True)
    module.assert_newest_release_tag("release-2026.08.2")
    try:
        module.assert_newest_release_tag("release-2026.07.3")
    except module.ReleaseError as exc:
        assert "newer" in str(exc)
    else:
        raise AssertionError("non-increasing stable release tag was accepted")
    module.git = lambda *args: "f" * 40 if args == ("rev-parse", "origin/main") else (
        "" if args == ("status", "--porcelain") else commit
    )
    try:
        module.assert_release_source(commit, True)
    except module.ReleaseError as exc:
        assert "origin/main tip" in str(exc)
    else:
        raise AssertionError("release source behind the main tip was accepted")
    module.git = real_git

    bootstrap = load_bootstrap()
    real_resolve_git_commit = bootstrap.resolve_git_commit
    bootstrap.resolve_git_commit = lambda ref: commit
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selection = bootstrap.select(profile, catalog)
    release = bootstrap.release_identity(first, first["release_tag"], module.DEFAULT_REPOSITORY, selection, CATALOG)
    plan = bootstrap.make_plan(
        profile,
        catalog,
        "codex",
        module.DEFAULT_REPOSITORY,
        first["release_tag"],
        "evidence-lab-plugins",
        release,
    )
    assert plan["release"] == release
    state = bootstrap.initial_state(plan)
    assert state["release"] == release
    bootstrap.validate_plan(plan)
    for value, schema_name in (
        (plan, "installation-plan.schema.json"),
        (state, "installation-state.schema.json"),
    ):
        schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
        assert not list(Draft202012Validator(schema).iter_errors(value))

    previous_lock = module.build_lock("release-2026.07.1", commit, module.DEFAULT_REPOSITORY)
    previous_release = {
        "tag": previous_lock["release_tag"],
        "channel": "stable",
        "source_commit": commit,
        "lock_digest": bootstrap.object_digest(previous_lock),
    }
    reconcile_plan = bootstrap.make_reconcile_plan(
        profile,
        catalog,
        "codex",
        module.DEFAULT_REPOSITORY,
        first["release_tag"],
        "evidence-lab-plugins",
        [{"id": item["id"], "version": item["version"]} for item in selection["packs"]],
        previous_lock["release_tag"],
        release,
        previous_release,
    )
    bootstrap.validate_previous_release_lock(reconcile_plan, previous_lock)
    reconcile_state = bootstrap.initial_reconcile_state(reconcile_plan)
    for value, schema_name in (
        (reconcile_plan, "reconcile-plan.schema.json"),
        (reconcile_state, "reconcile-state.schema.json"),
    ):
        schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
        assert not list(Draft202012Validator(schema).iter_errors(value))
    tampered_previous = json.loads(json.dumps(previous_lock))
    tampered_previous["packs"][0]["version"] = "0.0.0"
    try:
        bootstrap.validate_previous_release_lock(reconcile_plan, tampered_previous)
    except bootstrap.BootstrapError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("rollback accepted a previous lock with a different digest")

    selected_ids = {item["id"] for item in selection["packs"]}
    extra = next(item for item in previous_lock["packs"] if item["id"] not in selected_ids)
    baseline_with_old_extra = [
        {"id": item["id"], "version": item["version"]} for item in selection["packs"]
    ] + [{"id": extra["id"], "version": "0.0.1"}]
    retained_extra_plan = bootstrap.make_reconcile_plan(
        profile,
        catalog,
        "codex",
        module.DEFAULT_REPOSITORY,
        first["release_tag"],
        "evidence-lab-plugins",
        baseline_with_old_extra,
        previous_lock["release_tag"],
        release,
        previous_release,
    )
    bootstrap.validate_previous_release_lock(retained_extra_plan, previous_lock)
    try:
        bootstrap.validate_previous_release_lock(retained_extra_plan, previous_lock, include_removals=True)
    except bootstrap.BootstrapError as exc:
        assert "baseline versions" in str(exc)
    else:
        raise AssertionError("removal was allowed without a reproducible prior extra version")

    wrong_checkout = json.loads(json.dumps(first))
    wrong_checkout["source"]["commit"] = "0" * 40
    try:
        bootstrap.release_identity(
            wrong_checkout,
            first["release_tag"],
            module.DEFAULT_REPOSITORY,
            selection,
            CATALOG,
        )
    except bootstrap.BootstrapError as exc:
        assert "commit does not match" in str(exc)
    else:
        raise AssertionError("bootstrap accepted a lock for another checkout")

    bootstrap.resolve_git_commit = lambda ref: "f" * 40
    try:
        bootstrap.release_identity(first, first["release_tag"], module.DEFAULT_REPOSITORY, selection, CATALOG)
    except bootstrap.BootstrapError as exc:
        assert "does not point" in str(exc)
    else:
        raise AssertionError("bootstrap accepted a release tag pointing to another commit")
    bootstrap.resolve_git_commit = lambda ref: commit

    wrong_tree = json.loads(json.dumps(first))
    wrong_tree["packs"][0]["content_sha256"] = "0" * 64
    try:
        bootstrap.release_identity(
            wrong_tree,
            first["release_tag"],
            module.DEFAULT_REPOSITORY,
            selection,
            CATALOG,
        )
    except bootstrap.BootstrapError as exc:
        assert "content does not match" in str(exc)
    else:
        raise AssertionError("bootstrap accepted a lock with a forged pack tree")

    incomplete = json.loads(json.dumps(first))
    incomplete["packs"] = [item for item in incomplete["packs"] if item["id"] in {row["id"] for row in selection["packs"]}]
    try:
        bootstrap.release_identity(
            incomplete,
            first["release_tag"],
            module.DEFAULT_REPOSITORY,
            selection,
            CATALOG,
        )
    except bootstrap.BootstrapError as exc:
        assert "complete published catalog" in str(exc)
    else:
        raise AssertionError("bootstrap accepted an incomplete release lock")

    reordered = json.loads(json.dumps(first))
    reordered["packs"].reverse()
    try:
        bootstrap.release_identity(
            reordered,
            first["release_tag"],
            module.DEFAULT_REPOSITORY,
            selection,
            CATALOG,
        )
    except bootstrap.BootstrapError as exc:
        assert "canonical ID order" in str(exc)
    else:
        raise AssertionError("bootstrap accepted a reordered release lock")

    notes = module.release_notes(first)
    assert first["release_tag"] in notes
    assert all(item["id"] in notes for item in first["packs"])

    tampered = json.loads(json.dumps(first))
    tampered["packs"][0]["content_sha256"] = "0" * 64
    try:
        module.validate_lock(tampered, require_tag=False)
    except module.ReleaseError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("tampered release lock was accepted")

    wrong_commit = json.loads(json.dumps(first))
    wrong_commit["source"]["commit"] = "0" * 40
    try:
        module.validate_lock(wrong_commit, require_tag=False)
    except module.ReleaseError as exc:
        assert "does not match HEAD" in str(exc)
    else:
        raise AssertionError("release verifier accepted a lock for another commit")

    fork_repository = "evidence-lab/example-fork"
    fork_lock = module.build_lock("release-2026.08.1", commit, fork_repository)
    fork_release = bootstrap.release_identity(
        fork_lock,
        fork_lock["release_tag"],
        fork_repository,
        selection,
        CATALOG,
    )
    assert fork_release["source_commit"] == commit

    for schema_name in ("installation-state.schema.json", "reconcile-state.schema.json"):
        release_schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))["properties"]["release"]
        assert list(Draft202012Validator(release_schema).iter_errors({"unexpected": True}))
        assert list(Draft202012Validator(release_schema).iter_errors({
            "tag": "release-2026.08.1",
            "channel": "stable",
            "source_commit": "a" * 40,
        }))

    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary)
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.email", "release-test.invalid"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.name", "Release Test"], cwd=repository, check=True)
        (repository / "fixture.txt").write_text("release fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "fixture.txt"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "fixture"], cwd=repository, check=True)
        subprocess.run(["git", "branch", "release-2026.08.1"], cwd=repository, check=True)
        original_root = bootstrap.REPO_ROOT
        bootstrap.REPO_ROOT = repository
        bootstrap.resolve_git_commit = real_resolve_git_commit
        try:
            try:
                bootstrap.resolve_git_commit("release-2026.08.1")
            except bootstrap.BootstrapError as exc:
                assert "not available" in str(exc)
            else:
                raise AssertionError("a release-shaped branch was accepted as an immutable tag")
            subprocess.run(["git", "tag", "release-2026.08.1"], cwd=repository, check=True)
            assert bootstrap.resolve_git_commit("release-2026.08.1") == subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repository, capture_output=True, text=True, check=True,
            ).stdout.strip()
        finally:
            bootstrap.REPO_ROOT = original_root

    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "release-lock.json"
        module.write(output, json.dumps(first, indent=2) + "\n")
        assert json.loads(output.read_text(encoding="utf-8")) == first

    print("OK: immutable release lock verified for 14 published packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
