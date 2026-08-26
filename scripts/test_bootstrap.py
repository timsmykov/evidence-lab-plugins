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


class FakeHost:
    def __init__(self, host: str, versions: dict[str, str], *, fail_on: str | None = None):
        self.host = host
        self.versions = versions
        self.fail_on = fail_on
        self.marketplace_source: str | None = None
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

        if "marketplace" in command and ("add" in command or "upgrade" in command or "update" in command):
            if "add" in command:
                self.marketplace_source = "timsmykov/evidence-lab-plugins"
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
            self.host == "claude-code" and command[:3] == ["claude", "plugin", "install"]
        ):
            selector = command[3]
            name = selector.split("@", 1)[0]
            if name == self.fail_on:
                return self.completed(command, returncode=1)
            self.installed[name] = self.versions[name]
            return self.completed(command, {})

        if (self.host == "codex" and command[:3] == ["codex", "plugin", "remove"]) or (
            self.host == "claude-code" and command[:3] == ["claude", "plugin", "uninstall"]
        ):
            name = command[3].split("@", 1)[0]
            self.installed.pop(name, None)
            self.removed.append(name)
            return self.completed(command, {})
        raise AssertionError(f"unexpected command: {command}")


def build_plan(module, host: str) -> dict:
    return module.make_plan(load(PROFILE), load(CATALOG), host, "timsmykov/evidence-lab-plugins", "v0.3.0", "evidence-lab-plugins")


def test_success_and_idempotence(module, host: str) -> None:
    plan = build_plan(module, host)
    validate(plan, "installation-plan.schema.json")
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost(host, versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state_path = Path(temporary) / "state.json"
        state = module.apply_plan(plan, state_path)
        validate(state, "installation-state.schema.json")
        assert state["status"] == "ready"
        assert fake.installed == versions
        assert module.verify_plan(plan)["ready"] is True
        second = module.apply_plan(plan, state_path)
        assert second["status"] == "ready"
        assert all(item["status"] == "skipped" for item in second["operations"][1:])


def test_failure_rolls_back(module, host: str) -> None:
    plan = build_plan(module, host)
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost(host, versions, fail_on="data-and-pdf")
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json")
        validate(state, "installation-state.schema.json")
        assert state["status"] == "failed"
        assert fake.installed == {}
        assert fake.removed == ["evidence-lab-core"]
        statuses = {item["target"]: item["status"] for item in state["operations"]}
        assert statuses["evidence-lab-core"] == "rolled-back"
        assert statuses["data-and-pdf"] == "failed"


def test_wrong_marketplace_is_safe(module) -> None:
    plan = build_plan(module, "codex")
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost("codex", versions)
    fake.marketplace_source = "another-owner/another-repository"
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json")
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
            module.apply_plan(plan, Path(temporary) / "state.json")
        except module.BootstrapError as exc:
            assert "identity" in str(exc) or "operations" in str(exc)
        else:
            raise AssertionError("tampered installation plan was accepted")
    assert fake.commands == []


def test_local_marketplace_rerun_does_not_update(module, host: str) -> None:
    source = str(ROOT)
    plan = module.make_plan(load(PROFILE), load(CATALOG), host, source, "local-test", "evidence-lab-plugins")
    versions = {item["id"]: item["version"] for item in plan["selection_plan"]["packs"]}
    fake = FakeHost(host, versions)
    fake.marketplace_source = source
    fake.installed = dict(versions)
    module.run = fake
    with tempfile.TemporaryDirectory() as temporary:
        state = module.apply_plan(plan, Path(temporary) / "state.json")
        assert state["status"] == "ready"
        assert not any("upgrade" in command or "update" in command for command in fake.commands)


def main() -> int:
    module = load_bootstrap()
    for host in ("codex", "claude-code"):
        test_success_and_idempotence(module, host)
        test_failure_rolls_back(module, host)
        test_local_marketplace_rerun_does_not_update(module, host)
    test_wrong_marketplace_is_safe(module)
    test_tampered_plan_is_rejected(module)
    print("OK: bootstrap lifecycle verified for Codex and Claude Code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
