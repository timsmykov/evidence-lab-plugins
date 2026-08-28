#!/usr/bin/env python3
"""Pure contracts for the local Evidence Lab onboarding experiment harness."""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUTS = {
    "verify": 120,
    "turn": 180,
    "plan": 360,
    "apply": 420,
    "new_task": 300,
    "attempt": 1500,
}
REQUIRED_PASS_CHECKS = {
    "candidate_verified",
    "language_selected",
    "four_questions_completed",
    "canonical_plan_rendered",
    "no_preconfirmation_install",
    "explicit_confirmation",
    "installation_ready",
    "host_readback_verified",
    "completion_message_verified",
    "new_task_probe_verified",
}
REQUIRED_PASS_HASHES = {"journal", "plan", "installation_state", "new_task_output"}
RUN_PROOF_PATHS = {
    "journal": Path("events.jsonl"),
    "plan": Path("observations/plan.json"),
    "installation_state": Path("observations/installation-state.json"),
    "new_task_output": Path("observations/new-task-probe.json"),
}
REQUIRED_REVIEW_CHECKS = {
    "manifest",
    "all_primary_receipts",
    "abnormal_attempts",
    "two_language_examples",
    "artifact_hashes",
    "repository_gate",
    "claim_scope",
}
INITIAL_STATE = "CREATED"
SUCCESS_STATES = (
    "SANDBOX_READY",
    "CANDIDATE_VERIFIED",
    "ONBOARDING_STARTED",
    "LANGUAGE_SELECTED",
    "QUESTIONS_COMPLETED",
    "PROFILE_READY",
    "PLAN_RENDERED",
    "PRECONFIRMATION_VERIFIED",
    "USER_CONFIRMED",
    "APPLY_STARTED",
    "INSTALLATION_READY",
    "HOST_READBACK_VERIFIED",
    "COMPLETION_VERIFIED",
    "NEW_TASK_VERIFIED",
    "COMPLETED",
)
TERMINAL_STATES = {
    "COMPLETED",
    "PRODUCT_FAIL",
    "SAFETY_FAIL",
    "HARNESS_FAIL",
    "INFRA_INVALID",
    "ARTIFACT_REJECTED",
    "OPERATOR_ABORTED",
}
FAILURE_STATES = TERMINAL_STATES - {"COMPLETED"}
FORBIDDEN_FIELD_NAMES = {
    "session_id",
    "thread_id",
    "token",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
    "authorization",
    "auth",
    "absolute_path",
    "environment_dump",
}
PRIVATE_VALUE_PATTERNS = {
    "private_root_path": re.compile(r"(?:^|[\s\"'])(?:/root/|/home/[^/\s]+/\.(?:ssh|config|codex|claude)/)"),
    "github_token": re.compile(r"\b(?:ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}\b"),
    "api_token": re.compile(r"\b(?:sk-|xox[baprs]-)[A-Za-z0-9_-]{20,}\b"),
    "bearer": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*\b", re.I),
}


class ExperimentError(RuntimeError):
    """Raised when experiment evidence violates the frozen protocol."""


class ExperimentTimeout(ExperimentError):
    """Raised when a frozen experiment stage exceeds its timeout."""

    def __init__(self, stage: str, timeout_seconds: int):
        self.stage = stage
        self.timeout_seconds = timeout_seconds
        super().__init__(f"{stage} timed out after {timeout_seconds} seconds")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def object_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_sha256(paths: Iterable[Path], *, root: Path) -> str:
    rows = []
    for path in sorted((item.resolve() for item in paths), key=lambda item: item.as_posix()):
        try:
            relative = path.relative_to(root.resolve()).as_posix()
        except ValueError as exc:
            raise ExperimentError(f"digest input leaves root: {path}") from exc
        rows.append({"path": relative, "sha256": file_sha256(path)})
    return object_sha256(rows)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentError(f"cannot read JSON artifact {path.name}: {exc}") from exc


def validate_json_schema(value: object, schema_name: str) -> None:
    schema = read_json(ROOT / "schemas" / schema_name)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.path))
    if errors:
        raise ExperimentError(f"{schema_name}: {errors[0].message}")


def write_secure_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
    finally:
        if path.exists():
            os.chmod(path, 0o600)


def write_secure_json(path: Path, value: object) -> None:
    write_secure_bytes(path, canonical_bytes(value))


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def default_artifact_root() -> Path:
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state / "evidence-lab" / "experiments"


def prepare_artifact_root(path: Path, *, repository_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    repo = repository_root.resolve()
    if is_relative_to(resolved, repo) or is_relative_to(repo, resolved):
        raise ExperimentError("artifact root must be outside the repository and its parents")
    resolved.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(resolved, 0o700)
    if stat.S_IMODE(resolved.stat().st_mode) != 0o700:
        raise ExperimentError("artifact root must use mode 0700")
    return resolved


def assert_sanitized(value: object, *, location: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_FIELD_NAMES:
                raise ExperimentError(f"forbidden field at {location}.{key}")
            assert_sanitized(item, location=f"{location}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            assert_sanitized(item, location=f"{location}[{index}]")
        return
    if isinstance(value, str):
        for label, pattern in PRIVATE_VALUE_PATTERNS.items():
            if pattern.search(value):
                raise ExperimentError(f"{label} detected at {location}")


def validate_scenario_bundle(bundle: Mapping[str, object]) -> list[dict]:
    if bundle.get("schema_version") != 2:
        raise ExperimentError("scenario bundle schema_version must be 2")
    if bundle.get("model") != "gpt-5.6-terra" or bundle.get("reasoning_effort") != "medium":
        raise ExperimentError("scenario bundle must pin Terra medium")
    scenarios = bundle.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 10:
        raise ExperimentError("scenario bundle must contain exactly 10 scenarios")
    required = {"id", "source", "language", "language_answer", "answer_style", "stages", "answers"}
    ids = []
    languages: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    styles: Counter[str] = Counter()
    stages: set[str] = set()
    for index, raw in enumerate(scenarios):
        if not isinstance(raw, dict) or set(raw) != required:
            raise ExperimentError(f"scenario {index + 1} has unexpected fields")
        scenario_id = raw["id"]
        if not isinstance(scenario_id, str) or not re.fullmatch(r"[a-z0-9-]+", scenario_id):
            raise ExperimentError(f"scenario {index + 1} has invalid id")
        if raw["source"] not in {"regression", "holdout"}:
            raise ExperimentError(f"scenario {scenario_id} has invalid source")
        if raw["language"] not in {"en", "ru"}:
            raise ExperimentError(f"scenario {scenario_id} has invalid language")
        if raw["answer_style"] not in {"numeric", "free-text", "mixed"}:
            raise ExperimentError(f"scenario {scenario_id} has invalid answer style")
        if not isinstance(raw["answers"], list) or len(raw["answers"]) != 4 or not all(isinstance(item, str) and item for item in raw["answers"]):
            raise ExperimentError(f"scenario {scenario_id} must contain four answers")
        if not isinstance(raw["stages"], list) or not raw["stages"]:
            raise ExperimentError(f"scenario {scenario_id} has no stage coverage")
        ids.append(scenario_id)
        languages[raw["language"]] += 1
        sources[raw["source"]] += 1
        styles[raw["answer_style"]] += 1
        stages.update(raw["stages"])
    if len(set(ids)) != 10:
        raise ExperimentError("scenario ids must be unique")
    if languages != Counter({"en": 5, "ru": 5}):
        raise ExperimentError("scenario bundle must contain five English and five Russian profiles")
    if sources != Counter({"regression": 5, "holdout": 5}):
        raise ExperimentError("scenario bundle must contain five regression and five holdout profiles")
    if styles["free-text"] < 4 or styles["numeric"] < 3 or styles["mixed"] < 2:
        raise ExperimentError("scenario answer-style quotas are not satisfied")
    required_stages = {"planning", "active-research", "writing", "systematic-review", "supervision", "unknown"}
    if not required_stages.issubset(stages):
        raise ExperimentError(f"scenario stage coverage is incomplete: {sorted(required_stages - stages)}")
    return scenarios


def candidate_inputs(manifest: Mapping[str, object]) -> dict:
    return {
        "schema_version": manifest["schema_version"],
        "product": manifest["product"],
        "harness": manifest["harness"],
        "runtime": manifest["runtime"],
        "scenario_ids": manifest["scenario_ids"],
        "artifact_policy": manifest["artifact_policy"],
    }


def seal_manifest(
    *,
    product: dict,
    harness: dict,
    runtime: dict,
    scenario_ids: Sequence[str],
    created_at: str | None = None,
) -> dict:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "product": product,
        "harness": harness,
        "runtime": runtime,
        "scenario_ids": list(scenario_ids),
        "artifact_policy": {
            "local_only": True,
            "root_kind": "xdg-state-outside-worktree",
            "directory_mode": "0700",
            "file_mode": "0600",
        },
    }
    candidate_id = object_sha256(candidate_inputs(manifest))
    timestamp = created_at or utc_now()
    day = timestamp[:10].replace("-", "")
    return {
        **manifest,
        "candidate_id": candidate_id,
        "cohort_id": f"codex-terra10-{day}-{candidate_id[:12]}",
        "created_at": timestamp,
    }


def verify_manifest_identity(manifest: Mapping[str, object]) -> None:
    expected = object_sha256(candidate_inputs(manifest))
    if manifest.get("candidate_id") != expected:
        raise ExperimentError("candidate identity drift detected")
    expected_suffix = expected[:12]
    if not str(manifest.get("cohort_id", "")).endswith(expected_suffix):
        raise ExperimentError("cohort id is not bound to candidate identity")


def allowed_transitions() -> dict[str, set[str]]:
    transitions: dict[str, set[str]] = {}
    previous = INITIAL_STATE
    for state in SUCCESS_STATES:
        transitions.setdefault(previous, set()).add(state)
        previous = state
    for state in [INITIAL_STATE, *SUCCESS_STATES[:-1]]:
        transitions.setdefault(state, set()).update(FAILURE_STATES)
    transitions["COMPLETED"] = set()
    for state in FAILURE_STATES:
        transitions[state] = set()
    return transitions


TRANSITIONS = allowed_transitions()


def validate_transition(previous_state: str | None, next_state: str) -> None:
    effective = previous_state or INITIAL_STATE
    if next_state not in TRANSITIONS.get(effective, set()):
        raise ExperimentError(f"illegal state transition: {effective} -> {next_state}")


class EventJournal:
    """Append-only, hash-chained JSONL state journal."""

    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.run_id = run_id

    def events(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ExperimentError(f"journal line {line_number} is malformed") from exc
        return rows

    def verify(self) -> list[dict]:
        rows = self.events()
        previous_hash = None
        previous_state = None
        for sequence, row in enumerate(rows, 1):
            if row.get("sequence") != sequence or row.get("run_id") != self.run_id:
                raise ExperimentError(f"journal sequence {sequence} identity mismatch")
            if row.get("previous_event_hash") != previous_hash:
                raise ExperimentError(f"journal sequence {sequence} hash chain is broken")
            validate_transition(previous_state, row.get("next_state"))
            if row.get("previous_state") != previous_state:
                raise ExperimentError(f"journal sequence {sequence} previous state mismatch")
            unsigned = {key: value for key, value in row.items() if key != "event_hash"}
            expected_hash = object_sha256(unsigned)
            if row.get("event_hash") != expected_hash:
                raise ExperimentError(f"journal sequence {sequence} event hash mismatch")
            assert_sanitized(row.get("payload", {}), location=f"event[{sequence}].payload")
            previous_hash = expected_hash
            previous_state = row["next_state"]
        return rows

    def append(self, next_state: str, event_type: str, payload: dict | None = None, *, timestamp: str | None = None) -> dict:
        rows = self.verify()
        previous = rows[-1]["next_state"] if rows else None
        validate_transition(previous, next_state)
        if not re.fullmatch(r"[A-Z0-9_]+", event_type):
            raise ExperimentError("event type must use uppercase snake case")
        clean_payload = payload or {}
        assert_sanitized(clean_payload, location="event.payload")
        unsigned = {
            "schema_version": SCHEMA_VERSION,
            "sequence": len(rows) + 1,
            "timestamp": timestamp or utc_now(),
            "run_id": self.run_id,
            "previous_state": previous,
            "next_state": next_state,
            "event_type": event_type,
            "payload": clean_payload,
            "previous_event_hash": rows[-1]["event_hash"] if rows else None,
        }
        event = {**unsigned, "event_hash": object_sha256(unsigned)}
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.path.parent, 0o700)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(descriptor, "ab") as handle:
            handle.write(canonical_bytes(event))
        os.chmod(self.path, 0o600)
        return event


def outcome_for_terminal(terminal_state: str) -> tuple[str, str, str]:
    mapping = {
        "COMPLETED": ("VALID", "PASS", "PASS"),
        "PRODUCT_FAIL": ("VALID", "FAIL", "PASS"),
        "SAFETY_FAIL": ("VALID", "FAIL", "PASS"),
        "HARNESS_FAIL": ("INVALID", "NOT_ASSESSED", "FAIL"),
        "INFRA_INVALID": ("INVALID", "NOT_ASSESSED", "PASS"),
        "ARTIFACT_REJECTED": ("INVALID", "NOT_ASSESSED", "FAIL"),
        "OPERATOR_ABORTED": ("INVALID", "NOT_ASSESSED", "PASS"),
    }
    try:
        return mapping[terminal_state]
    except KeyError as exc:
        raise ExperimentError(f"state is not terminal: {terminal_state}") from exc


def make_receipt(
    *,
    manifest: Mapping[str, object],
    scenario_id: str,
    attempt: int,
    terminal_state: str,
    checks: Mapping[str, bool],
    hashes: Mapping[str, str],
    selected_packs: Sequence[Mapping[str, str]] = (),
    durations_seconds: Mapping[str, float] | None = None,
    warnings: Sequence[str] = (),
    failure_class: str | None = None,
    supersedes_run_id: str | None = None,
    adjudication_status: str = "NOT_REQUIRED",
) -> dict:
    validity, product_outcome, harness_outcome = outcome_for_terminal(terminal_state)
    run_id = f"{manifest['cohort_id']}/{scenario_id}/attempt-{attempt:02d}"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "cohort_id": manifest["cohort_id"],
        "candidate_id": manifest["candidate_id"],
        "scenario_id": scenario_id,
        "attempt": attempt,
        "run_id": run_id,
        "supersedes_run_id": supersedes_run_id,
        "validity": validity,
        "product_outcome": product_outcome,
        "harness_outcome": harness_outcome,
        "terminal_state": terminal_state,
        "failure_class": failure_class,
        "checks": dict(checks),
        "hashes": dict(hashes),
        "selected_packs": [dict(item) for item in selected_packs],
        "durations_seconds": dict(durations_seconds or {}),
        "warnings": list(warnings),
        "adjudication_status": adjudication_status,
    }
    assert_sanitized(receipt)
    validate_receipt(receipt, manifest=manifest)
    return receipt


def _release_binding(manifest: Mapping[str, object]) -> dict:
    product = manifest["product"]
    return {
        "tag": product["release_tag"],
        "channel": "stable",
        "source_commit": product["commit"],
        "lock_digest": product["release_lock_sha256"],
    }


def derive_run_proof(
    *,
    manifest: Mapping[str, object],
    run_root: Path,
    events: Sequence[Mapping[str, object]],
) -> tuple[dict[str, bool], dict[str, str], list[dict[str, str]]]:
    states = {str(event.get("next_state")) for event in events}
    checks = {
        "candidate_verified": "CANDIDATE_VERIFIED" in states,
        "language_selected": "LANGUAGE_SELECTED" in states,
        "four_questions_completed": "QUESTIONS_COMPLETED" in states,
        "canonical_plan_rendered": "PLAN_RENDERED" in states,
        "no_preconfirmation_install": "PRECONFIRMATION_VERIFIED" in states,
        "explicit_confirmation": "USER_CONFIRMED" in states,
        "installation_ready": "INSTALLATION_READY" in states,
        "host_readback_verified": "HOST_READBACK_VERIFIED" in states,
        "completion_message_verified": "COMPLETION_VERIFIED" in states,
        "new_task_probe_verified": "NEW_TASK_VERIFIED" in states,
    }
    resolved_root = run_root.resolve()
    proof_paths: dict[str, Path] = {}
    for name, relative in RUN_PROOF_PATHS.items():
        path = (run_root / relative).resolve()
        if not is_relative_to(path, resolved_root) or not path.is_file() or path.is_symlink():
            raise ExperimentError(f"run proof artifact is missing or unsafe: {relative.as_posix()}")
        proof_paths[name] = path

    plan = read_json(proof_paths["plan"])
    installation_state = read_json(proof_paths["installation_state"])
    probe = read_json(proof_paths["new_task_output"])
    validate_json_schema(plan, "installation-plan.schema.json")
    validate_json_schema(installation_state, "installation-state.schema.json")
    if plan.get("release") != _release_binding(manifest):
        raise ExperimentError("installation plan is not bound to the cohort release")
    if installation_state.get("release") != _release_binding(manifest):
        raise ExperimentError("installation state is not bound to the cohort release")
    if installation_state.get("plan_id") != plan.get("plan_id"):
        raise ExperimentError("installation state is not bound to the recorded plan")
    if installation_state.get("status") != "ready" or installation_state.get("error") is not None:
        raise ExperimentError("installation state is not ready")
    installed_after = installation_state.get("installed_after")
    if not isinstance(installed_after, list) or not installed_after:
        raise ExperimentError("installation state has no installed packs")
    desired = installation_state.get("desired")
    if installed_after != desired:
        raise ExperimentError("host readback does not match the desired installation")
    if probe.get("match") is not True or probe.get("actual_output_sha256") != probe.get("expected_output_sha256"):
        raise ExperimentError("new-task probe is not a verified deterministic match")
    if not all(checks.values()):
        missing = sorted(name for name, passed in checks.items() if not passed)
        raise ExperimentError(f"completed run lacks journal evidence: {missing}")
    hashes = {name: file_sha256(path) for name, path in proof_paths.items()}
    selected_packs = [
        {"id": str(item["id"]), "version": str(item["version"])}
        for item in installed_after
    ]
    return checks, hashes, selected_packs


def build_receipt_from_run(
    *,
    manifest: Mapping[str, object],
    scenario_id: str,
    attempt: int,
    terminal_state: str,
    run_root: Path,
    failure_class: str | None = None,
    supersedes_run_id: str | None = None,
    adjudication_status: str = "NOT_REQUIRED",
) -> dict:
    run_id = f"{manifest['cohort_id']}/{scenario_id}/attempt-{attempt:02d}"
    events = EventJournal(run_root / "events.jsonl", run_id).verify()
    if not events or events[-1].get("next_state") != terminal_state:
        raise ExperimentError("receipt terminal state does not match the run journal")
    checks: Mapping[str, bool] = {}
    hashes: Mapping[str, str] = {"journal": file_sha256(run_root / "events.jsonl")}
    selected_packs: Sequence[Mapping[str, str]] = ()
    if terminal_state == "COMPLETED":
        checks, hashes, selected_packs = derive_run_proof(
            manifest=manifest,
            run_root=run_root,
            events=events,
        )
    return make_receipt(
        manifest=manifest,
        scenario_id=scenario_id,
        attempt=attempt,
        terminal_state=terminal_state,
        checks=checks,
        hashes=hashes,
        selected_packs=selected_packs,
        failure_class=failure_class,
        supersedes_run_id=supersedes_run_id,
        adjudication_status=adjudication_status,
    )


def validate_receipt_artifacts(
    receipt: Mapping[str, object],
    run_root: Path,
    *,
    manifest: Mapping[str, object] | None = None,
) -> None:
    journal_path = run_root / "events.jsonl"
    if not journal_path.is_file() or journal_path.is_symlink():
        raise ExperimentError("receipt journal artifact is missing or unsafe")
    events = EventJournal(journal_path, str(receipt.get("run_id"))).verify()
    if not events or events[-1].get("next_state") != receipt.get("terminal_state"):
        raise ExperimentError("receipt terminal state does not match the retained journal")
    if receipt.get("terminal_state") != "COMPLETED":
        if receipt.get("hashes", {}).get("journal") != file_sha256(journal_path):
            raise ExperimentError("receipt journal hash does not match the retained artifact")
        return
    hashes = receipt.get("hashes")
    if not isinstance(hashes, Mapping):
        raise ExperimentError("receipt hashes are invalid")
    for name, relative in RUN_PROOF_PATHS.items():
        path = run_root / relative
        if not path.is_file() or path.is_symlink() or hashes.get(name) != file_sha256(path):
            raise ExperimentError(f"receipt hash does not match retained artifact: {name}")
    if manifest is not None:
        checks, derived_hashes, selected_packs = derive_run_proof(
            manifest=manifest,
            run_root=run_root,
            events=events,
        )
        if receipt.get("checks") != checks or receipt.get("hashes") != derived_hashes:
            raise ExperimentError("receipt proof was not derived from the retained run artifacts")
        if receipt.get("selected_packs") != selected_packs:
            raise ExperimentError("receipt installed packs do not match host readback")


def validate_receipt(receipt: Mapping[str, object], *, manifest: Mapping[str, object]) -> None:
    scenario_id = receipt.get("scenario_id")
    if receipt.get("candidate_id") != manifest.get("candidate_id") or receipt.get("cohort_id") != manifest.get("cohort_id"):
        raise ExperimentError("receipt identity does not match the cohort manifest")
    if scenario_id not in manifest.get("scenario_ids", []):
        raise ExperimentError("receipt scenario is not part of the frozen cohort")
    attempt = receipt.get("attempt")
    if not isinstance(attempt, int) or attempt < 1:
        raise ExperimentError("receipt attempt must be positive")
    expected_run_id = f"{manifest['cohort_id']}/{scenario_id}/attempt-{attempt:02d}"
    if receipt.get("run_id") != expected_run_id:
        raise ExperimentError("receipt run identity is invalid")
    expected_outcomes = outcome_for_terminal(str(receipt.get("terminal_state")))
    actual_outcomes = (
        receipt.get("validity"),
        receipt.get("product_outcome"),
        receipt.get("harness_outcome"),
    )
    if actual_outcomes != expected_outcomes:
        raise ExperimentError("receipt terminal outcomes are inconsistent")
    checks = receipt.get("checks")
    hashes = receipt.get("hashes")
    if not isinstance(checks, Mapping) or not all(isinstance(value, bool) for value in checks.values()):
        raise ExperimentError("receipt checks must be boolean")
    if not isinstance(hashes, Mapping) or not all(
        isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) for value in hashes.values()
    ):
        raise ExperimentError("receipt hashes must be SHA-256 values")
    if receipt.get("terminal_state") == "COMPLETED":
        missing_checks = REQUIRED_PASS_CHECKS - set(checks)
        failed_checks = sorted(key for key in REQUIRED_PASS_CHECKS if not checks.get(key))
        missing_hashes = REQUIRED_PASS_HASHES - set(hashes)
        if missing_checks or failed_checks or missing_hashes:
            raise ExperimentError(
                "completed receipt lacks proof: "
                f"missing checks={sorted(missing_checks)}, failed checks={failed_checks}, "
                f"missing hashes={sorted(missing_hashes)}"
            )
        if not receipt.get("selected_packs"):
            raise ExperimentError("completed receipt must record installed packs")
    selected_packs = receipt.get("selected_packs")
    if not isinstance(selected_packs, list) or not all(
        isinstance(item, Mapping)
        and set(item) == {"id", "version"}
        and isinstance(item["id"], str)
        and re.fullmatch(r"[a-z0-9-]+", item["id"])
        and isinstance(item["version"], str)
        and bool(item["version"])
        for item in selected_packs
    ):
        raise ExperimentError("receipt selected packs are invalid")


def validate_supersession(receipts: Sequence[Mapping[str, object]]) -> None:
    by_run = {str(item["run_id"]): item for item in receipts}
    for receipt in receipts:
        supersedes = receipt.get("supersedes_run_id")
        if not supersedes:
            continue
        previous = by_run.get(str(supersedes))
        if previous is None:
            raise ExperimentError(f"superseded run is missing: {supersedes}")
        if previous.get("terminal_state") != "INFRA_INVALID":
            raise ExperimentError("only infrastructure-invalid attempts may be superseded")
        if receipt.get("candidate_id") != previous.get("candidate_id") or receipt.get("scenario_id") != previous.get("scenario_id"):
            raise ExperimentError("supersession changed candidate or scenario")


def cohort_should_stop(
    receipts: Sequence[Mapping[str, object]],
    *,
    journal_terminal_states: Sequence[str] = (),
) -> bool:
    return any(item.get("terminal_state") == "SAFETY_FAIL" for item in receipts) or "SAFETY_FAIL" in journal_terminal_states


def cohort_journal_terminal_states(
    cohort_root: Path,
    *,
    manifest: Mapping[str, object] | None = None,
) -> list[str]:
    cohort_manifest = manifest or read_json(cohort_root / "manifest.json")
    states = []
    for path in sorted((cohort_root / "runs").glob("*/attempt-*/events.jsonl")):
        relative = path.relative_to(cohort_root)
        scenario_id = relative.parts[1]
        attempt = int(relative.parts[2].removeprefix("attempt-"))
        run_id = f"{cohort_manifest['cohort_id']}/{scenario_id}/attempt-{attempt:02d}"
        events = EventJournal(path, run_id).verify()
        if events and events[-1]["next_state"] in TERMINAL_STATES:
            states.append(str(events[-1]["next_state"]))
    return states


def cohort_has_safety_failure(
    cohort_root: Path,
    *,
    manifest: Mapping[str, object] | None = None,
) -> bool:
    return "SAFETY_FAIL" in cohort_journal_terminal_states(cohort_root, manifest=manifest)


def resume_inventory(manifest: Mapping[str, object], cohort_root: Path) -> list[dict]:
    rows = []
    for scenario_id in manifest["scenario_ids"]:
        attempts = sorted((cohort_root / "runs" / str(scenario_id)).glob("attempt-*"))
        if not attempts:
            rows.append({"scenario_id": scenario_id, "attempt": 1, "state": "PENDING", "action": "START"})
            continue
        latest = attempts[-1]
        try:
            attempt = int(latest.name.removeprefix("attempt-"))
        except ValueError as exc:
            raise ExperimentError(f"invalid attempt directory: {latest.name}") from exc
        run_id = f"{manifest['cohort_id']}/{scenario_id}/attempt-{attempt:02d}"
        events = EventJournal(latest / "events.jsonl", run_id).verify()
        if not events:
            raise ExperimentError(f"attempt has no events: {scenario_id}/{latest.name}")
        state = str(events[-1]["next_state"])
        receipt_path = latest / "receipt.json"
        if state in TERMINAL_STATES:
            if not receipt_path.is_file():
                action = "FINISH"
            else:
                receipt = read_json(receipt_path)
                validate_receipt_artifacts(receipt, latest, manifest=manifest)
                action = "RETRY" if state == "INFRA_INVALID" else "DONE"
        else:
            if receipt_path.exists():
                raise ExperimentError("non-terminal attempt has a receipt")
            action = "RESUME"
        rows.append({"scenario_id": scenario_id, "attempt": attempt, "state": state, "action": action})
    return rows


def summarize_cohort(
    manifest: Mapping[str, object],
    receipts: Sequence[Mapping[str, object]],
    *,
    cohort_root: Path | None = None,
) -> dict:
    verify_manifest_identity(manifest)
    for receipt in receipts:
        validate_receipt(receipt, manifest=manifest)
    validate_supersession(receipts)
    journal_terminal_states: list[str] = []
    evidence_verified = cohort_root is not None
    if cohort_root is not None:
        journal_terminal_states = cohort_journal_terminal_states(cohort_root, manifest=manifest)
        for receipt in receipts:
            run_root = (
                cohort_root
                / "runs"
                / str(receipt["scenario_id"])
                / f"attempt-{int(receipt['attempt']):02d}"
            )
            validate_receipt_artifacts(receipt, run_root, manifest=manifest)
    valid = [item for item in receipts if item.get("validity") == "VALID"]
    primary_by_scenario: dict[str, Mapping[str, object]] = {}
    for receipt in sorted(valid, key=lambda item: int(item["attempt"])):
        scenario = str(receipt["scenario_id"])
        if scenario in primary_by_scenario:
            raise ExperimentError(f"multiple valid primary results for scenario {scenario}")
        primary_by_scenario[scenario] = receipt
    expected_ids = list(manifest["scenario_ids"])
    passes = sum(item.get("product_outcome") == "PASS" for item in primary_by_scenario.values())
    failures = sum(item.get("product_outcome") == "FAIL" for item in primary_by_scenario.values())
    unresolved = sum(bool(item.get("warnings")) or item.get("adjudication_status") == "PENDING" for item in receipts)
    gate_pass = (
        set(primary_by_scenario) == set(expected_ids)
        and len(primary_by_scenario) == 10
        and passes == 10
        and failures == 0
        and unresolved == 0
        and evidence_verified
        and not cohort_should_stop(receipts, journal_terminal_states=journal_terminal_states)
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": manifest["candidate_id"],
        "cohort_id": manifest["cohort_id"],
        "expected_scenarios": 10,
        "valid_primary_scenarios": len(primary_by_scenario),
        "product_passes": passes,
        "product_failures": failures,
        "invalid_attempts": len(receipts) - len(valid),
        "safety_stop": cohort_should_stop(receipts, journal_terminal_states=journal_terminal_states),
        "evidence_verified": evidence_verified,
        "unresolved_items": unresolved,
        "gate_pass": gate_pass,
    }


def artifact_index(
    cohort_root: Path,
    *,
    exclude: Sequence[str] = ("artifact-index.json",),
    exclude_prefixes: Sequence[str] = ("runtime/",),
) -> dict:
    root = cohort_root.resolve()
    if stat.S_IMODE(root.stat().st_mode) != 0o700:
        raise ExperimentError("cohort root must use mode 0700")
    rows = []
    for path in sorted(cohort_root.rglob("*")):
        relative_lexical = path.relative_to(cohort_root).as_posix()
        relative_parts = Path(relative_lexical).parts
        run_runtime = (
            len(relative_parts) >= 4
            and relative_parts[0] == "runs"
            and relative_parts[2].startswith("attempt-")
            and relative_parts[3] == "runtime"
        )
        if run_runtime or any(relative_lexical.startswith(prefix) for prefix in exclude_prefixes):
            continue
        if path.is_symlink():
            raise ExperimentError(f"artifact symlink is forbidden: {path.name}")
        if not path.is_file():
            continue
        resolved = path.resolve()
        if not is_relative_to(resolved, root):
            raise ExperimentError("artifact path escapes cohort root")
        relative = resolved.relative_to(root).as_posix()
        if relative in exclude:
            continue
        if stat.S_IMODE(path.stat().st_mode) != 0o600:
            raise ExperimentError(f"artifact must use mode 0600: {relative}")
        if path.suffix == ".json":
            assert_sanitized(read_json(path), location=relative)
        elif path.suffix in {".jsonl", ".md", ".txt"}:
            assert_sanitized(path.read_text(encoding="utf-8"), location=relative)
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "sha256": file_sha256(path),
            }
        )
    return {"schema_version": SCHEMA_VERSION, "artifacts": rows, "artifact_count": len(rows)}


def verify_review_binding(review: Mapping[str, object], manifest: Mapping[str, object], index: Mapping[str, object]) -> None:
    if review.get("candidate_id") != manifest.get("candidate_id"):
        raise ExperimentError("review candidate binding mismatch")
    if review.get("artifact_index_sha256") != object_sha256(index):
        raise ExperimentError("review artifact-index binding mismatch")
    if review.get("reviewer") != "Tim":
        raise ExperimentError("first-cohort reviewer must be Tim")
    checks = review.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != REQUIRED_REVIEW_CHECKS or not all(
        isinstance(value, bool) for value in checks.values()
    ):
        raise ExperimentError("review checklist is incomplete or invalid")
    if review.get("decision") == "ACCEPT" and not all(checks.values()):
        raise ExperimentError("accepted review contains an unchecked requirement")


def parse_codex_jsonl(text: str) -> list[dict]:
    events = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExperimentError(f"Codex JSONL line {line_number} is malformed") from exc
        if not isinstance(value, dict) or not isinstance(value.get("type"), str):
            raise ExperimentError(f"Codex JSONL line {line_number} has no event type")
        events.append(value)
    if not events:
        raise ExperimentError("Codex JSONL stream is empty")
    return events


def final_agent_message(events: Sequence[Mapping[str, object]]) -> str:
    messages = []
    for event in events:
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, Mapping) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                messages.append(text)
    if not messages:
        raise ExperimentError("Codex stream has no final agent message")
    return messages[-1]


def command_execution_items(events: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
    items = []
    for event in events:
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, Mapping) and item.get("type") == "command_execution":
            items.append(item)
    return items


def verify_probe_execution(
    events: Sequence[Mapping[str, object]],
    *,
    installed_plugin_root: Path,
) -> tuple[str, Mapping[str, object]]:
    root = installed_plugin_root.resolve()
    pattern = re.compile(r"(?P<path>/(?:[^\s\"']+/)*format_bibtex\.py)")
    for item in command_execution_items(events):
        command = item.get("command")
        if (
            not isinstance(command, str)
            or "--rekey" not in command
            or "--deduplicate" not in command
            or "--sort key" not in command
            or item.get("exit_code") != 0
            or item.get("status") != "completed"
        ):
            continue
        for match in pattern.finditer(command):
            candidate = Path(match.group("path")).resolve()
            if is_relative_to(candidate, root) and candidate.name == "format_bibtex.py":
                return candidate.relative_to(root).as_posix(), item
    raise ExperimentError("new-task probe did not execute installed format_bibtex.py")


def verify_probe_command(events: Sequence[Mapping[str, object]], *, installed_plugin_root: Path) -> str:
    relative, _ = verify_probe_execution(events, installed_plugin_root=installed_plugin_root)
    return relative
