#!/usr/bin/env python3
"""Operate the local-only Evidence Lab onboarding experiment.

This command deliberately manages evidence and phase gates. It does not hide
the live Codex invocation behind a retry loop: an operator records the observed
state transitions and terminal result for every immutable attempt.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from onboarding_experiment import (
    DEFAULT_TIMEOUTS,
    EventJournal,
    ExperimentError,
    artifact_index,
    cohort_should_stop,
    default_artifact_root,
    file_sha256,
    files_sha256,
    make_receipt,
    object_sha256,
    parse_codex_jsonl,
    prepare_artifact_root,
    read_json,
    seal_manifest,
    summarize_cohort,
    utc_now,
    validate_scenario_bundle,
    verify_manifest_identity,
    verify_probe_command,
    verify_review_binding,
    write_secure_bytes,
    write_secure_json,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCENARIOS = ROOT / "tests" / "acceptance" / "onboarding-terra-10.scenarios.ru.json"
EXPERIMENT_SCHEMAS = tuple(sorted((ROOT / "schemas").glob("experiment-*.schema.json")))


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ExperimentError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def artifact_root(value: str | None) -> Path:
    return prepare_artifact_root(
        Path(value).expanduser() if value else default_artifact_root(),
        repository_root=ROOT,
    )


def cohort_root(args: argparse.Namespace) -> Path:
    root = artifact_root(args.artifact_root)
    path = (root / args.cohort_id).resolve()
    if path.parent != root.resolve():
        raise ExperimentError("invalid cohort id")
    if not path.is_dir():
        raise ExperimentError(f"cohort does not exist: {args.cohort_id}")
    return path


def load_manifest(path: Path) -> dict:
    manifest = read_json(path / "manifest.json")
    verify_manifest_identity(manifest)
    return manifest


def cmd_validate_scenarios(args: argparse.Namespace) -> None:
    scenarios = validate_scenario_bundle(read_json(args.scenarios))
    print(json.dumps({"valid": True, "scenario_count": len(scenarios)}, sort_keys=True))


def cmd_prepare(args: argparse.Namespace) -> None:
    scenarios_path = args.scenarios.resolve()
    scenarios = validate_scenario_bundle(read_json(scenarios_path))
    root = artifact_root(args.artifact_root)
    product_commit = args.product_commit or git("rev-list", "-n", "1", args.release_tag)
    harness_commit = args.harness_commit or git("rev-parse", "HEAD")
    manifest = seal_manifest(
        product={
            "commit": product_commit,
            "release_tag": args.release_tag,
            "release_lock_sha256": file_sha256(args.release_lock),
            "catalog_sha256": file_sha256(args.catalog),
        },
        harness={
            "commit": harness_commit,
            "schema_bundle_sha256": files_sha256(EXPERIMENT_SCHEMAS, root=ROOT),
            "scenario_bundle_sha256": file_sha256(scenarios_path),
        },
        runtime={
            "codex_version": args.codex_version,
            "model": "gpt-5.6-terra",
            "reasoning_effort": "medium",
            "isolation": "bubblewrap-linux-v1",
            "timeouts_seconds": DEFAULT_TIMEOUTS,
        },
        scenario_ids=[item["id"] for item in scenarios],
    )
    path = root / manifest["cohort_id"]
    if path.exists():
        raise ExperimentError("cohort already exists; immutable candidates cannot be overwritten")
    path.mkdir(mode=0o700)
    write_secure_json(path / "manifest.json", manifest)
    write_secure_json(path / "scenario-bundle.json", read_json(scenarios_path))
    print(json.dumps({"cohort_id": manifest["cohort_id"], "phase": "PREPARED"}, sort_keys=True))


def run_paths(root: Path, scenario_id: str, attempt: int) -> tuple[Path, str]:
    if not scenario_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in scenario_id):
        raise ExperimentError("invalid scenario id")
    if attempt < 1:
        raise ExperimentError("attempt must be positive")
    run_id = f"{scenario_id}/attempt-{attempt:02d}"
    return root / "runs" / scenario_id / f"attempt-{attempt:02d}", run_id


def cmd_start_run(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    if cohort_should_stop(receipts(root)):
        raise ExperimentError("cohort is stopped after a safety failure")
    if args.scenario_id not in manifest["scenario_ids"]:
        raise ExperimentError("scenario is not part of the frozen cohort")
    run_root, relative_run_id = run_paths(root, args.scenario_id, args.attempt)
    if run_root.exists():
        raise ExperimentError("attempt already exists; journals are append-only")
    run_root.mkdir(parents=True, mode=0o700)
    journal = EventJournal(run_root / "events.jsonl", f"{manifest['cohort_id']}/{relative_run_id}")
    journal.append("SANDBOX_READY", "SANDBOX_READY", {"isolation": "bubblewrap-linux-v1"})
    print(json.dumps({"run_id": journal.run_id, "state": "SANDBOX_READY"}, sort_keys=True))


def cmd_event(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    run_root, relative_run_id = run_paths(root, args.scenario_id, args.attempt)
    if (run_root / "receipt.json").exists():
        raise ExperimentError("receipt already exists; completed attempts are immutable")
    payload = read_json(args.payload) if args.payload else {}
    event = EventJournal(
        run_root / "events.jsonl", f"{manifest['cohort_id']}/{relative_run_id}"
    ).append(args.next_state, args.event_type, payload)
    print(json.dumps({"sequence": event["sequence"], "state": event["next_state"]}, sort_keys=True))


def cmd_finish_run(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    run_root, relative_run_id = run_paths(root, args.scenario_id, args.attempt)
    if (run_root / "receipt.json").exists():
        raise ExperimentError("receipt already exists; completed attempts are immutable")
    journal = EventJournal(run_root / "events.jsonl", f"{manifest['cohort_id']}/{relative_run_id}")
    events = journal.verify()
    if not events:
        raise ExperimentError("run has no journal")
    if events[-1]["next_state"] != args.terminal_state:
        journal.append(
            args.terminal_state,
            "RUN_TERMINATED",
            {"failure_class": args.failure_class} if args.failure_class else {},
        )
        events = journal.verify()
    checks = read_json(args.checks) if args.checks else {}
    hashes = read_json(args.hashes) if args.hashes else {"journal": file_sha256(journal.path)}
    selected_packs = read_json(args.selected_packs) if args.selected_packs else []
    receipt = make_receipt(
        manifest=manifest,
        scenario_id=args.scenario_id,
        attempt=args.attempt,
        terminal_state=args.terminal_state,
        checks=checks,
        hashes=hashes,
        selected_packs=selected_packs,
        failure_class=args.failure_class,
        supersedes_run_id=args.supersedes,
        adjudication_status=args.adjudication_status,
    )
    write_secure_json(run_root / "receipt.json", receipt)
    print(json.dumps({"run_id": receipt["run_id"], "terminal_state": args.terminal_state}, sort_keys=True))


def cmd_codex_turn(args: argparse.Namespace) -> None:
    from onboarding_experiment_adapter import SandboxSpec, run_turn

    root = cohort_root(args)
    manifest = load_manifest(root)
    if args.scenario_id not in manifest["scenario_ids"]:
        raise ExperimentError("scenario is not part of the frozen cohort")
    run_root, _ = run_paths(root, args.scenario_id, args.attempt)
    if not (run_root / "events.jsonl").is_file():
        raise ExperimentError("start the run before executing a Codex turn")
    if not args.turn_label or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in args.turn_label):
        raise ExperimentError("invalid turn label")
    runtime = run_root / "runtime"
    turn_runtime = runtime / "turns" / args.turn_label
    evidence_path = run_root / "observations" / f"{args.turn_label}.json"
    if turn_runtime.exists() or evidence_path.exists():
        raise ExperimentError("turn label already exists; observations are immutable")
    resume_path = runtime / "onboarding-thread.json"
    thread_id = None
    if not args.new_task and resume_path.exists():
        thread_id = read_json(resume_path).get("session_id")
        if not isinstance(thread_id, str) or not thread_id:
            raise ExperimentError("stored onboarding thread identity is invalid")
    workspace = runtime / "workspace"
    if args.fixture:
        write_secure_bytes(workspace / args.fixture.name, args.fixture.read_bytes())
    spec = SandboxSpec(
        codex_binary=args.codex_binary,
        auth_file=args.auth_file,
        codex_home=runtime / "codex-home",
        workspace=workspace,
        release_checkout=None if args.new_task else args.release_checkout,
    )
    current_thread, observation = run_turn(
        spec,
        prompt=args.prompt_file.read_text(encoding="utf-8"),
        runtime_root=turn_runtime,
        evidence_path=evidence_path,
        timeout_seconds=args.timeout,
        thread_id=None if args.new_task else thread_id,
        expose_release=not args.new_task,
    )
    if not args.new_task:
        write_secure_json(resume_path, {"session_id": current_thread})
    print(observation["final_message"])


def cmd_verify_probe(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    run_root, relative_run_id = run_paths(root, args.scenario_id, args.attempt)
    evidence_path = run_root / "observations" / "new-task-probe.json"
    if evidence_path.exists():
        raise ExperimentError("new-task probe evidence already exists")
    events = parse_codex_jsonl(args.raw_jsonl.read_text(encoding="utf-8"))
    relative_script = verify_probe_command(events, installed_plugin_root=args.installed_plugin_root)
    actual_hash = file_sha256(args.actual_output)
    expected_hash = file_sha256(args.expected_output)
    if actual_hash != expected_hash:
        raise ExperimentError("new-task probe output does not match the frozen fixture")
    evidence = {
        "schema_version": 1,
        "installed_script": relative_script,
        "actual_output_sha256": actual_hash,
        "expected_output_sha256": expected_hash,
        "match": True,
    }
    write_secure_json(evidence_path, evidence)
    EventJournal(
        run_root / "events.jsonl", f"{manifest['cohort_id']}/{relative_run_id}"
    ).append("NEW_TASK_VERIFIED", "NEW_TASK_PROBE_VERIFIED", evidence)
    print(json.dumps(evidence, sort_keys=True))


def receipts(root: Path) -> list[dict]:
    return [read_json(path) for path in sorted((root / "runs").glob("*/attempt-*/receipt.json"))]


def cmd_status(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    rows = receipts(root)
    summary = summarize_cohort(manifest, rows)
    summary["phase"] = "STOPPED_SAFETY" if summary["safety_stop"] else (
        "READY_FOR_REVIEW" if summary["valid_primary_scenarios"] == 10 else "RUNNING"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def cmd_seal(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    if (root / "artifact-index.json").exists():
        raise ExperimentError("cohort is already sealed")
    manifest = load_manifest(root)
    summary = summarize_cohort(manifest, receipts(root))
    if summary["valid_primary_scenarios"] != 10 and not summary["safety_stop"]:
        raise ExperimentError("cohort cannot be sealed before ten valid primary scenarios")
    write_secure_json(root / "summary.json", summary)
    index = artifact_index(root)
    write_secure_json(root / "artifact-index.json", index)
    print(json.dumps({"sealed": True, "artifact_index_sha256": object_sha256(index)}, sort_keys=True))


def cmd_review_template(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    index = read_json(root / "artifact-index.json")
    review = {
        "schema_version": 1,
        "candidate_id": manifest["candidate_id"],
        "artifact_index_sha256": object_sha256(index),
        "reviewer": "Tim",
        "reviewed_at": utc_now(),
        "decision": "REJECT",
        "checks": {
            "manifest": False,
            "all_primary_receipts": False,
            "abnormal_attempts": False,
            "two_language_examples": False,
            "artifact_hashes": False,
            "repository_gate": False,
            "claim_scope": False,
        },
        "reservations": ["Complete the independent review before acceptance."],
    }
    write_secure_json(root / "review.template.json", review)
    print(json.dumps({"created": "review.template.json"}, sort_keys=True))


def cmd_verify_review(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    index = read_json(root / "artifact-index.json")
    review = read_json(args.review)
    verify_review_binding(review, manifest, index)
    print(json.dumps({"valid": True, "decision": review["decision"]}, sort_keys=True))


def cmd_distill_template(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    summary = read_json(root / "summary.json")
    template = {
        "schema_version": 1,
        "candidate_id": manifest["candidate_id"],
        "cohort_id": manifest["cohort_id"],
        "scope": {
            "valid_scenarios": summary["valid_primary_scenarios"],
            "synthetic": True,
            "claims_exclude": ["real-researcher usability", "production readiness"],
        },
        "findings": [],
        "finding_fields": [
            "problem",
            "observed_in_valid_scenarios",
            "user_impact",
            "cause_status",
            "improvement_opportunity",
            "confidence",
            "evidence_receipt_ids",
        ],
    }
    write_secure_json(root / "product-findings.template.json", template)
    print(json.dumps({"created": "product-findings.template.json"}, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--artifact-root")
    common.add_argument("--cohort-id", required=True)
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate-scenarios")
    validate.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    validate.set_defaults(func=cmd_validate_scenarios)

    prepare = commands.add_parser("prepare")
    prepare.add_argument("--artifact-root")
    prepare.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    prepare.add_argument("--release-tag", required=True)
    prepare.add_argument("--release-lock", type=Path, required=True)
    prepare.add_argument("--catalog", type=Path, required=True)
    prepare.add_argument("--product-commit")
    prepare.add_argument("--harness-commit")
    prepare.add_argument("--codex-version", required=True)
    prepare.set_defaults(func=cmd_prepare)

    start = commands.add_parser("start-run", parents=[common])
    start.add_argument("--scenario-id", required=True)
    start.add_argument("--attempt", type=int, default=1)
    start.set_defaults(func=cmd_start_run)

    event = commands.add_parser("event", parents=[common])
    event.add_argument("--scenario-id", required=True)
    event.add_argument("--attempt", type=int, default=1)
    event.add_argument("--next-state", required=True)
    event.add_argument("--event-type", required=True)
    event.add_argument("--payload", type=Path)
    event.set_defaults(func=cmd_event)

    finish = commands.add_parser("finish-run", parents=[common])
    finish.add_argument("--scenario-id", required=True)
    finish.add_argument("--attempt", type=int, default=1)
    finish.add_argument("--terminal-state", required=True)
    finish.add_argument("--failure-class")
    finish.add_argument("--checks", type=Path)
    finish.add_argument("--hashes", type=Path)
    finish.add_argument("--selected-packs", type=Path)
    finish.add_argument("--supersedes")
    finish.add_argument(
        "--adjudication-status",
        choices=("NOT_REQUIRED", "PENDING", "RESOLVED"),
        default="NOT_REQUIRED",
    )
    finish.set_defaults(func=cmd_finish_run)

    turn = commands.add_parser("codex-turn", parents=[common])
    turn.add_argument("--scenario-id", required=True)
    turn.add_argument("--attempt", type=int, default=1)
    turn.add_argument("--turn-label", required=True)
    turn.add_argument("--prompt-file", type=Path, required=True)
    turn.add_argument("--codex-binary", type=Path, required=True)
    turn.add_argument("--auth-file", type=Path, required=True)
    turn.add_argument("--release-checkout", type=Path)
    turn.add_argument("--fixture", type=Path)
    turn.add_argument("--new-task", action="store_true")
    turn.add_argument("--timeout", type=int, required=True)
    turn.set_defaults(func=cmd_codex_turn)

    probe = commands.add_parser("verify-probe", parents=[common])
    probe.add_argument("--scenario-id", required=True)
    probe.add_argument("--attempt", type=int, default=1)
    probe.add_argument("--raw-jsonl", type=Path, required=True)
    probe.add_argument("--installed-plugin-root", type=Path, required=True)
    probe.add_argument("--actual-output", type=Path, required=True)
    probe.add_argument("--expected-output", type=Path, required=True)
    probe.set_defaults(func=cmd_verify_probe)

    for name, function in (
        ("status", cmd_status),
        ("seal", cmd_seal),
        ("review-template", cmd_review_template),
        ("distill-template", cmd_distill_template),
    ):
        command = commands.add_parser(name, parents=[common])
        command.set_defaults(func=function)

    review = commands.add_parser("verify-review", parents=[common])
    review.add_argument("--review", type=Path, required=True)
    review.set_defaults(func=cmd_verify_review)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        args.func(args)
    except ExperimentError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
