#!/usr/bin/env python3
"""End-to-end bootstrap lifecycle tests with isolated fake host CLIs."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
BOOTSTRAP_PATH = ROOT / "packs" / "core" / "evidence-lab-core" / "skills" / "evidence-lab-onboarding" / "scripts" / "bootstrap.py"
SELECTOR_DIR = BOOTSTRAP_PATH.parent
CATALOG = ROOT / "packs" / "core" / "evidence-lab-core" / "catalog" / "packs.json"
PROFILE = ROOT / "tests" / "fixtures" / "onboarding" / "quantitative-full-cycle.profile.json"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SELECTOR_DIR))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(value, schema_name: str) -> None:
    errors = list(Draft202012Validator(load(SCHEMAS / schema_name)).iter_errors(value))
    if errors:
        raise AssertionError(f"{schema_name}: {errors[0].message}")


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("evidence_lab_bootstrap", BOOTSTRAP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def release_record(ref: str = "release-2026.08.1") -> dict:
    return {
        "tag": ref,
        "channel": "stable",
        "source_commit": "a" * 40,
        "lock_digest": "b" * 64,
    }


def test_source_matches_claude_marketplace_url(module) -> None:
    row = {
        "name": "evidence-lab-plugins",
        "source": "git",
        "url": "https://github.com/timsmykov/evidence-lab-plugins.git",
        "ref": "release-2026.08.1",
        "installLocation": "/tmp/evidence-lab-plugins",
    }
    assert module.source_matches(row, "timsmykov/evidence-lab-plugins")
    assert not module.source_matches(row, "another-owner/evidence-lab-plugins")


class FakeHost:
    def __init__(
        self,
        host: str,
        versions: dict[str, str],
        *,
        fail_on: str | None = None,
        fail_remove: str | None = None,
        version_sequences: dict[str, list[str]] | None = None,
    ):
        self.host = host
        self.versions = versions
        self.fail_on = fail_on
        self.fail_remove = fail_remove
        self.version_sequences = version_sequences or {}
        self.marketplace_source: str | None = None
        self.marketplace_ref: str | None = None
        self.installed: dict[str, str] = {}
        self.removed: list[str] = []
        self.commands: list[list[str]] = []

    def completed(self, command: list[str], payload=None, returncode: int = 0):
        stdout = "" if payload is None else json.dumps(payload)
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    def __call__(self, command: list[str]):
        self.commands.append(command)
        if command[:4] in (["codex", "plugin", "marketplace", "list"], ["claude", "plugin", "marketplace", "list"]):
            rows = []
            if self.marketplace_source:
                if self.host == "codex":
                    rows = [{"name": "evidence-lab-plugins", "marketplaceSource": {"source": self.marketplace_source}}]
                    return self.completed(command, {"marketplaces": rows})
                rows = [{"name": "evidence-lab-plugins", "repo": self.marketplace_source}]
            return self.completed(command, rows)

        if "marketplace" in command and "remove" in command:
            self.marketplace_source = None
            self.marketplace_ref = None
            return self.completed(command, {})

        if "marketplace" in command and ("add" in command or "upgrade" in command or "update" in command):
            if "add" in command:
                self.marketplace_source = "timsmykov/evidence-lab-plugins"
                if "--ref" in command:
                    self.marketplace_ref = command[command.index("--ref") + 1]
            return self.completed(command, {})

        if command[:3] in (["codex", "plugin", "list"], ["claude", "plugin", "list"]):
            if self.host == "codex":
                rows = [
                    {"pluginId": f"{name}@evidence-lab-plugins", "name": name, "marketplaceName": "evidence-lab-plugins", "version": version}
                    for name, version in sorted(self.installed.items())
                ]
                return self.completed(command, {"installed": rows})
            rows = [
                {"id": f"{name}@evidence-lab-plugins", "version": version}
                for name, version in sorted(self.installed.items())
            ]
            return self.completed(command, rows)

        if (self.host == "codex" and command[:3] == ["codex", "plugin", "add"]) or (
            self.host == "claude-code" and command[:3] in (["claude", "plugin", "install"], ["claude", "plugin", "update"])
        ):
            selector = command[3]
            name = selector.split("@", 1)[0]
            if name == self.fail_on:
                return self.completed(command, returncode=1)
            sequence = self.version_sequences.get(name, [])
            self.installed[name] = sequence.pop(0) if sequence else self.versions[name]
            return self.completed(command, {})

        if (self.host == "codex" and command[:3] == ["codex", "plugin", "remove"]) or (
            self.host == "claude-code" and command[:3] == ["claude", "plugin", "uninstall"]
        ):
            name = command[3].split("@", 1)[0]
            if name == self.fail_remove:
                return self.completed(command, returncode=1)
            self.installed.pop(name, None)
            self.removed.append(name)
            return self.completed(command, {})
        raise AssertionError(f"unexpected command: {command}")


def build_plan(module, host: str) -> dict:
    ref = "release-2026.08.1"
    return module.make_plan(
        load(PROFILE), load(CATALOG), host, "timsmykov/evidence-lab-plugins", ref,
        "evidence-lab-plugins", release_record(ref),
    )


def test_success_and_idempotence(module, host: str) -> None:
    plan = build_plan(module, host)
    validate(plan, "installation-plan.schema.json")
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost(host, versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        state = module.apply_plan(plan, state_path, {})
        validate(state, "installation-state.schema.json")
        assert state["status"] == "ready"
        assert fake.installed == versions
        assert module.verify_plan(plan, {})["ready"] is True
        second = module.apply_plan(plan, state_path, {})
        assert second["status"] == "ready"
        assert all(item["status"] == "skipped" for item in second["operations"][1:])


def test_failure_rolls_back(module, host: str) -> None:
    plan = build_plan(module, host)
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fail_target = "data-and-pdf"
    ordered_targets = [item["id"] for item in plan["selection_plan"]["packs"]]
    installed_before_failure = ordered_targets[:ordered_targets.index(fail_target)]
    fake = FakeHost(host, versions, fail_on=fail_target)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json", {})
        validate(state, "installation-state.schema.json")
        assert state["status"] == "failed"
        assert fake.installed == {}
        assert fake.removed == list(reversed(installed_before_failure))
        statuses = {item["target"]: item["status"] for item in state["operations"]}
        assert all(statuses[target] == "rolled-back" for target in installed_before_failure)
        assert statuses[fail_target] == "failed"


def test_wrong_marketplace_is_safe(module) -> None:
    plan = build_plan(module, "codex")
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost("codex", versions)
    fake.marketplace_source = "another-owner/another-repository"
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json", {})
        assert state["status"] == "failed"
        assert fake.installed == {}
        assert state["operations"][0]["status"] == "failed"


def test_tampered_plan_is_rejected(module) -> None:
    plan = build_plan(module, "codex")
    plan["selection_plan"]["packs"][0]["id"] = "unreviewed-pack"
    fake = FakeHost("codex", {})
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        try:
            module.apply_plan(plan, Path(temporary) / "state.json", {})
        except module.BootstrapError as exc:
            assert "identity" in str(exc) or "operations" in str(exc)
        else:
            raise AssertionError("tampered installation plan was accepted")
    assert fake.commands == []


def test_release_lock_mismatch_is_rejected_before_host_command(module) -> None:
    plan = build_plan(module, "codex")
    fake = FakeHost("codex", {})
    module.run = fake
    trusted = module.release_identity
    module.release_identity = lambda lock, ref, source, selection, catalog_path: {
        **release_record(ref),
        "source_commit": "0" * 40,
    }
    try:
        with tempfile.TemporaryDirectory() as temporary:
            try:
                module.apply_plan(plan, Path(temporary) / "state.json", {})
            except module.BootstrapError as exc:
                assert "verified release lock" in str(exc)
            else:
                raise AssertionError("apply accepted a plan that did not match the reverified release lock")
    finally:
        module.release_identity = trusted
    assert fake.commands == []


def test_local_marketplace_rerun_does_not_update(module, host: str) -> None:
    source = str(ROOT)
    ref = "release-2026.08.1"
    plan = module.make_plan(
        load(PROFILE), load(CATALOG), host, source, ref, "evidence-lab-plugins", release_record(ref),
    )
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost(host, versions)
    fake.marketplace_source = source
    fake.installed = dict(versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json", {})
        assert state["status"] == "ready"
        assert not any("upgrade" in command or "update" in command for command in fake.commands)


def build_reconcile_plan(module, host: str, installed: dict[str, str]) -> tuple[dict, dict[str, str]]:
    catalog = load(CATALOG)
    selection = module.select(load(PROFILE), catalog)
    versions = {item["id"]: item["version"] for item in selection["packs"]}
    plan = module.make_reconcile_plan(
        load(PROFILE),
        catalog,
        host,
        "timsmykov/evidence-lab-plugins",
        "release-2026.08.1",
        "evidence-lab-plugins",
        [{"id": name, "version": version} for name, version in installed.items()],
        "release-2026.07.1" if installed else None,
        release_record(),
        release_record("release-2026.07.1") if installed else None,
    )
    return plan, versions


def apply_reconcile(module, plan: dict, state_path: Path, profile: dict | None = None) -> dict:
    return module.apply_reconcile_plan(plan, state_path, profile or load(PROFILE), load(CATALOG), {}, {})


def remove_extras(module, plan: dict, state_path: Path, profile: dict | None = None) -> dict:
    return module.remove_reconcile_extras(plan, state_path, profile or load(PROFILE), load(CATALOG), {}, {})


def test_reconcile_update_retain_remove_restore(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0", "publication-monitoring": "0.1.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    validate(plan, "reconcile-plan.schema.json")
    assert [item["id"] for item in plan["diff"]["update"]] == ["evidence-lab-core"]
    assert plan["diff"]["retained_extra"] == [{"id": "publication-monitoring", "version": "0.1.0"}]
    fake = FakeHost(host, versions)
    fake.versions.setdefault("publication-monitoring", baseline["publication-monitoring"])
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "reconcile-state.json"
        state = apply_reconcile(module, plan, state_path)
        validate(state, "reconcile-state.schema.json")
        assert state["status"] == "ready"
        assert fake.installed["publication-monitoring"] == "0.1.0"
        marketplace_removals = [
            command for command in fake.commands
            if command[:4] in (
                ["codex", "plugin", "marketplace", "remove"],
                ["claude", "plugin", "marketplace", "remove"],
            )
        ]
        assert marketplace_removals
        if host == "claude-code":
            assert marketplace_removals[0][-2:] == ["--scope", "user"]
        else:
            assert marketplace_removals[0][-1] == "--json"

        removed = remove_extras(module, plan, state_path)
        validate(removed, "reconcile-state.schema.json")
        assert removed["status"] == "removed"
        assert "publication-monitoring" not in fake.installed

        fake.version_sequences["evidence-lab-core"] = ["0.5.0"]
        restored = module.restore_reconcile_state(plan, state_path, {}, {})
        validate(restored, "reconcile-state.schema.json")
        assert restored["status"] == "restored"
        assert fake.installed == baseline
        assert restored["active_ref"] == "release-2026.07.1"
        assert restored["release"] == plan["previous_release"]
        assert module.previous_ref_from_state(
            restored,
            plan,
            host,
            "evidence-lab-plugins",
            "timsmykov/evidence-lab-plugins",
        ) == "release-2026.07.1"
        assert module.previous_release_from_state(
            restored, plan, restored["active_ref"],
        ) == plan["previous_release"]
        next_plan = module.make_reconcile_plan(
            load(PROFILE),
            load(CATALOG),
            host,
            "timsmykov/evidence-lab-plugins",
            "release-2026.09.1",
            "evidence-lab-plugins",
            [{"id": name, "version": version} for name, version in baseline.items()],
            restored["active_ref"],
            release_record("release-2026.09.1"),
            restored["release"],
        )
        module.validate_reconcile_plan(next_plan)


def test_reconcile_stale_plan_rejected(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = {"evidence-lab-core": "0.4.0"}
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        try:
            apply_reconcile(module, plan, Path(temporary) / "state.json")
        except module.BootstrapError as exc:
            assert "stale reconcile plan" in str(exc)
        else:
            raise AssertionError("stale reconcile plan was applied")
    assert not any(" add " in f" {' '.join(command)} " or " update " in f" {' '.join(command)} " for command in fake.commands)


def test_reconcile_tamper_is_rejected(module, host: str) -> None:
    plan, versions = build_reconcile_plan(module, host, {"evidence-lab-core": "0.5.0"})
    plan["diff"]["add"][0]["version"] = "999.0.0"
    fake = FakeHost(host, versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        try:
            apply_reconcile(module, plan, Path(temporary) / "state.json")
        except module.BootstrapError as exc:
            assert "identity" in str(exc)
        else:
            raise AssertionError("tampered reconcile plan was applied")
    assert fake.commands == []


def test_installed_readback_excludes_unattributed_plugins(module, host: str) -> None:
    command_log = []

    def fake_run(command):
        command_log.append(command)
        if host == "codex":
            payload = {"installed": [
                {"name": "foreign-plugin", "version": "9.0.0"},
                {"pluginId": "evidence-lab-core@evidence-lab-plugins", "version": "0.6.0"},
            ]}
        else:
            payload = [
                {"name": "foreign-plugin", "version": "9.0.0"},
                {"id": "evidence-lab-core@evidence-lab-plugins", "version": "0.6.0"},
            ]
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    module.run = fake_run
    assert module.installed_rows(host, "evidence-lab-plugins") == [
        {"id": "evidence-lab-core", "version": "0.6.0"}
    ]
    assert command_log


def test_process_diagnostics_redact_secrets(module) -> None:
    result = subprocess.CompletedProcess(
        ["host"],
        1,
        stdout="",
        stderr=(
            "Authorization: Bearer TOPSECRET\ntoken=SECOND password: THIRD api_key=FOURTH https://"
            + "credential-user:credential-pass"
            + "@"
            + "example.test?access_token=FIFTH"
        ),
    )
    detail = module.safe_process_detail(result)
    for secret in ("TOPSECRET", "SECOND", "THIRD", "FOURTH", "credential-user:credential-pass", "FIFTH"):
        assert secret not in detail
    assert detail == "host command returned an error; inspect host logs"


def test_tampered_restore_snapshot_is_rejected(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        state = module.initial_reconcile_state(plan)
        state["pre_change_snapshot"] = {"installed": [], "digest": module.snapshot_digest([])}
        module.write_json_atomic(state_path, state)
        try:
            module.restore_reconcile_state(plan, state_path, {}, {})
        except module.BootstrapError as exc:
            assert "plan baseline" in str(exc)
        else:
            raise AssertionError("restore accepted a forged pre-change snapshot")
    assert fake.installed == baseline
    assert not any(command[:3] in (["codex", "plugin", "remove"], ["claude", "plugin", "uninstall"]) for command in fake.commands)


def test_restore_source_mismatch_never_removes_packs(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        state = apply_reconcile(module, plan, state_path)
        assert state["status"] == "ready"
        fake.marketplace_source = "another-owner/another-repository"
        installed_before = dict(fake.installed)
        command_index = len(fake.commands)
        restored = module.restore_reconcile_state(plan, state_path, {}, {})
        assert restored["status"] == "partial"
        assert fake.installed == installed_before
        new_commands = fake.commands[command_index:]
        assert not any(command[:3] in (["codex", "plugin", "remove"], ["claude", "plugin", "uninstall"]) for command in new_commands)


def test_remote_reconcile_requires_previous_release_ref(module, host: str) -> None:
    try:
        module.make_reconcile_plan(
            load(PROFILE),
            load(CATALOG),
            host,
            "timsmykov/evidence-lab-plugins",
            "release-2026.08.1",
            "evidence-lab-plugins",
            [{"id": "evidence-lab-core", "version": "0.5.0"}],
        )
    except module.BootstrapError as exc:
        assert "previous installation state" in str(exc)
    else:
        raise AssertionError("remote reconcile accepted installed packs without a previous release ref")


def test_legacy_state_recovers_ref_only_from_matching_plan(module, host: str) -> None:
    previous_plan = build_plan(module, host)
    legacy_state = module.initial_state(previous_plan)
    legacy_state["status"] = "ready"
    legacy_state.pop("marketplace")
    previous_ref = module.previous_ref_from_state(
        legacy_state,
        previous_plan,
        host,
        "evidence-lab-plugins",
        "timsmykov/evidence-lab-plugins",
    )
    assert previous_ref == "release-2026.08.1"
    mismatched_plan = dict(previous_plan)
    mismatched_plan["plan_id"] = "0" * 16
    try:
        module.previous_ref_from_state(
            legacy_state,
            mismatched_plan,
            host,
            "evidence-lab-plugins",
            "timsmykov/evidence-lab-plugins",
        )
    except module.BootstrapError:
        pass
    else:
        raise AssertionError("legacy state accepted a mismatched installation plan")


def test_modern_state_ref_is_bound_to_previous_plan(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0"}
    plan, _ = build_reconcile_plan(module, host, baseline)
    state = module.initial_reconcile_state(plan)
    state["status"] = "ready"
    state["active_ref"] = plan["marketplace"]["ref"]
    state["release"] = plan["release"]
    state["installed_after"] = module.expected_reconciled_snapshot(plan)
    state["operations"][0]["status"] = "completed"
    assert module.previous_ref_from_state(
        state,
        plan,
        host,
        "evidence-lab-plugins",
        "timsmykov/evidence-lab-plugins",
    ) == plan["marketplace"]["ref"]
    forged = json.loads(json.dumps(state))
    forged["active_ref"] = "main"
    try:
        module.previous_ref_from_state(
            forged,
            plan,
            host,
            "evidence-lab-plugins",
            "timsmykov/evidence-lab-plugins",
        )
    except module.BootstrapError:
        pass
    else:
        raise AssertionError("modern state accepted a rollback ref outside its previous plan")


def test_profile_change_makes_reconcile_plan_stale(module, host: str) -> None:
    plan, versions = build_reconcile_plan(module, host, {"evidence-lab-core": "0.5.0"})
    changed_profile = load(PROFILE)
    changed_profile["specialization_context"] = ["changed after planning"]
    fake = FakeHost(host, versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        try:
            apply_reconcile(module, plan, Path(temporary) / "state.json", changed_profile)
        except module.BootstrapError as exc:
            assert "profile or release catalog changed" in str(exc)
        else:
            raise AssertionError("reconcile accepted a changed profile")
    assert fake.commands == []


def test_profile_change_makes_removal_stale(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0", "qualitative-research": "0.1.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.versions.setdefault("qualitative-research", "0.1.0")
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        assert apply_reconcile(module, plan, state_path)["status"] == "ready"
        changed_profile = load(PROFILE)
        changed_profile["specialization_context"] = ["changed before removal"]
        try:
            remove_extras(module, plan, state_path, changed_profile)
        except module.BootstrapError as exc:
            assert "stale removal plan" in str(exc)
        else:
            raise AssertionError("removal accepted a changed profile")
        assert "qualitative-research" in fake.installed


def test_removal_source_mismatch_never_removes_packs(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0", "qualitative-research": "0.1.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.versions.setdefault("qualitative-research", "0.1.0")
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        assert apply_reconcile(module, plan, state_path)["status"] == "ready"
        fake.marketplace_source = "another-owner/another-repository"
        installed_before = dict(fake.installed)
        try:
            remove_extras(module, plan, state_path)
        except module.BootstrapError as exc:
            assert "another source" in str(exc)
        else:
            raise AssertionError("removal accepted a mismatched marketplace source")
        assert fake.installed == installed_before


def test_failed_update_reports_partial_when_exact_restore_is_unavailable(module, host: str) -> None:
    selection = module.select(load(PROFILE), load(CATALOG))
    versions = {item["id"]: item["version"] for item in selection["packs"]}
    baseline = {name: "0.0.1" for name in versions}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fail_target = plan["diff"]["update"][1]["id"]
    fake = FakeHost(host, versions, fail_on=fail_target)
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = apply_reconcile(module, plan, Path(temporary) / "state.json")
        validate(state, "reconcile-state.schema.json")
        assert state["status"] == "partial"
        assert state["installed_after"] == module.normalized_snapshot([
            {"id": name, "version": version} for name, version in fake.installed.items()
        ])


def test_exact_update_rollback_marks_operations(module, host: str) -> None:
    selection = module.select(load(PROFILE), load(CATALOG))
    versions = {item["id"]: item["version"] for item in selection["packs"]}
    baseline = {name: "0.0.1" for name in versions}
    plan, versions = build_reconcile_plan(module, host, baseline)
    first_update = plan["diff"]["update"][0]["id"]
    fail_target = plan["diff"]["update"][1]["id"]
    fake = FakeHost(
        host,
        versions,
        fail_on=fail_target,
        version_sequences={first_update: [versions[first_update], baseline[first_update]]},
    )
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = apply_reconcile(module, plan, Path(temporary) / "state.json")
        validate(state, "reconcile-state.schema.json")
        assert state["status"] == "failed"
        assert fake.installed == baseline
        operations = {(item["action"], item["target"]): item["status"] for item in state["operations"]}
        assert operations[("update-pack", first_update)] == "rolled-back"
        assert operations[("update-pack", fail_target)] == "failed"
        assert operations[("ensure-marketplace", "evidence-lab-plugins")] == "rolled-back"


def test_interrupted_run_recovery(module, host: str) -> None:
    baseline = {"evidence-lab-core": "0.5.0"}
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions)
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        state = module.initial_reconcile_state(plan)
        state["status"] = "applying"
        module.write_json_atomic(state_path, state)
        recovered = module.recover_reconcile_state(plan, state_path, {}, {})
        validate(recovered, "reconcile-state.schema.json")
        assert recovered["status"] == "failed"

        state["status"] = "restoring"
        module.write_json_atomic(state_path, state)
        recovered = module.recover_reconcile_state(plan, state_path, {}, {})
        assert recovered["status"] == "restored"


def test_partial_removal_preserves_exact_readback(module, host: str) -> None:
    baseline = {
        "evidence-lab-core": "0.5.0",
        "life-sciences": "0.1.0",
        "publication-monitoring": "0.1.0",
    }
    plan, versions = build_reconcile_plan(module, host, baseline)
    fake = FakeHost(host, versions, fail_remove="publication-monitoring")
    fake.versions.update({key: value for key, value in baseline.items() if key not in versions})
    fake.marketplace_source = "timsmykov/evidence-lab-plugins"
    fake.installed = dict(baseline)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        assert apply_reconcile(module, plan, state_path)["status"] == "ready"
        state = remove_extras(module, plan, state_path)
        validate(state, "reconcile-state.schema.json")
        assert state["status"] == "partial"
        assert state["installed_after"] == module.normalized_snapshot([
            {"id": name, "version": version} for name, version in fake.installed.items()
        ])
        assert state["error"]


def test_fused_plan_recommendation(module) -> None:
    profile = load(PROFILE)
    catalog = load(CATALOG)
    plan = module.make_plan(
        profile, catalog, "codex", "timsmykov/evidence-lab-plugins",
        "release-2026.08.1", "evidence-lab-plugins", release_record(),
    )
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "recommendation.md"
        rendered = module.render_recommendation(plan, "en", output)
        assert rendered.startswith("# Your Evidence Lab setup\n")
        assert output.read_text(encoding="utf-8") == rendered
        russian = module.render_recommendation(plan, "ru", output)
        assert russian.startswith("# ") and russian != rendered
        assert output.read_text(encoding="utf-8") == russian
    english_completion = module.render_completion("en")
    russian_completion = module.render_completion("ru")
    assert "Open a new task" in english_completion
    assert english_completion != russian_completion


def main() -> int:
    module = load_bootstrap()
    module.release_identity = lambda lock, ref, source, selection, catalog_path: release_record(ref)
    module.validate_previous_release_lock = lambda plan, lock, **kwargs: None
    for host in ("codex", "claude-code"):
        test_success_and_idempotence(module, host)
        test_failure_rolls_back(module, host)
        test_local_marketplace_rerun_does_not_update(module, host)
        test_reconcile_update_retain_remove_restore(module, host)
        test_reconcile_stale_plan_rejected(module, host)
        test_reconcile_tamper_is_rejected(module, host)
        test_installed_readback_excludes_unattributed_plugins(module, host)
        test_tampered_restore_snapshot_is_rejected(module, host)
        test_restore_source_mismatch_never_removes_packs(module, host)
        test_remote_reconcile_requires_previous_release_ref(module, host)
        test_legacy_state_recovers_ref_only_from_matching_plan(module, host)
        test_modern_state_ref_is_bound_to_previous_plan(module, host)
        test_profile_change_makes_reconcile_plan_stale(module, host)
        test_profile_change_makes_removal_stale(module, host)
        test_removal_source_mismatch_never_removes_packs(module, host)
        test_failed_update_reports_partial_when_exact_restore_is_unavailable(module, host)
        test_exact_update_rollback_marks_operations(module, host)
        test_interrupted_run_recovery(module, host)
        test_partial_removal_preserves_exact_readback(module, host)
    test_wrong_marketplace_is_safe(module)
    test_tampered_plan_is_rejected(module)
    test_release_lock_mismatch_is_rejected_before_host_command(module)
    test_process_diagnostics_redact_secrets(module)
    test_source_matches_claude_marketplace_url(module)
    test_fused_plan_recommendation(module)
    print("OK: bootstrap lifecycle verified for Codex and Claude Code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
