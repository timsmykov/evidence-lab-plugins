#!/usr/bin/env python3
"""Operate the local-only Evidence Lab onboarding experiment.

This command deliberately manages evidence and phase gates. It does not hide
the live Codex invocation behind a retry loop: an operator records the observed
state transitions and terminal result for every immutable attempt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from onboarding_experiment import (
    DEFAULT_TIMEOUTS,
    EventJournal,
    ExperimentError,
    ExperimentTimeout,
    artifact_index,
    build_receipt_from_run,
    cohort_has_safety_failure,
    default_artifact_root,
    file_sha256,
    final_agent_message,
    files_sha256,
    object_sha256,
    parse_codex_jsonl,
    prepare_artifact_root,
    read_json,
    resume_inventory,
    seal_manifest,
    summarize_cohort,
    utc_now,
    validate_json_schema,
    validate_scenario_bundle,
    verify_manifest_identity,
    verify_probe_execution,
    verify_review_binding,
    write_secure_bytes,
    write_secure_json,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCENARIOS = ROOT / "tests" / "acceptance" / "onboarding-terra-10.scenarios.ru.json"
EXPERIMENT_SCHEMAS = tuple(sorted((ROOT / "schemas").glob("experiment-*.schema.json")))
PROBE_INPUT = ROOT / "tests/fixtures/experiment/citation-probe-input.bib"
PROBE_EXPECTED = ROOT / "tests/fixtures/experiment/citation-probe-expected.bib"
PROBE_PROMPT = ROOT / "tests/fixtures/experiment/new-task-probe-prompt.txt"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ExperimentError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_at(checkout: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=checkout, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ExperimentError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def command_output(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode:
        raise ExperimentError(result.stderr.strip() or f"command failed: {command[0]}")
    output = result.stdout.strip()
    if not output:
        raise ExperimentError(f"command returned no output: {command[0]}")
    return output


def validate_release_candidate(
    *,
    release_tag: str,
    release_lock: Path,
    release_checkout: Path,
) -> tuple[dict, Path]:
    checkout = release_checkout.resolve()
    lock_path = release_lock.resolve()
    if not checkout.is_dir() or not (checkout / "scripts/release_snapshot.py").is_file():
        raise ExperimentError("release checkout is missing release verification code")
    lock = read_json(lock_path)
    if lock.get("release_tag") != release_tag:
        raise ExperimentError("release lock tag does not match the requested release")
    tag_commit = git("rev-list", "-n", "1", release_tag)
    if not tag_commit or lock.get("source", {}).get("commit") != tag_commit:
        raise ExperimentError("release lock source commit does not match the release tag")
    if git_at(checkout, "rev-parse", "HEAD") != tag_commit:
        raise ExperimentError("release checkout does not match the locked commit")
    if git_at(checkout, "status", "--porcelain"):
        raise ExperimentError("release checkout must be clean")
    result = subprocess.run(
        [sys.executable, str(checkout / "scripts/release_snapshot.py"), "verify", str(lock_path)],
        cwd=checkout,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ExperimentError(result.stderr.strip() or "release lock verification failed")
    catalog = checkout / "packs/core/evidence-lab-core/catalog/packs.json"
    if not catalog.is_file() or lock.get("catalog_sha256") != file_sha256(catalog):
        raise ExperimentError("release lock catalog digest does not match the release checkout")
    return lock, catalog


def verify_model_preflight(
    *,
    root: Path,
    codex_binary: Path,
    auth_file: Path,
) -> str:
    from onboarding_experiment_adapter import SandboxSpec, run_turn

    if shutil.which("bwrap") is None:
        raise ExperimentError("bubblewrap is not installed")
    with tempfile.TemporaryDirectory(prefix="preflight-", dir=root) as directory:
        temp = Path(directory)
        spec = SandboxSpec(
            codex_binary=codex_binary,
            auth_file=auth_file,
            codex_home=temp / "codex-home",
            workspace=temp / "workspace",
        )
        _, observation = run_turn(
            spec,
            prompt="Reply with exactly EVIDENCE_LAB_PREFLIGHT_OK and nothing else.",
            runtime_root=temp / "runtime",
            evidence_path=temp / "observation.json",
            timeout_seconds=DEFAULT_TIMEOUTS["verify"],
            stage="verify",
            expose_release=False,
        )
        if observation.get("final_message", "").strip() != "EVIDENCE_LAB_PREFLIGHT_OK":
            raise ExperimentError("Terra medium preflight returned an unexpected response")
    return "terra-medium-response-v1"


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
    verify_harness_candidate(manifest, path)
    return manifest


def verify_harness_candidate(manifest: dict, cohort_path: Path) -> None:
    if git("status", "--porcelain"):
        raise ExperimentError("harness worktree must be clean before starting or resuming a cohort")
    if git("rev-parse", "HEAD") != manifest["harness"]["commit"]:
        raise ExperimentError("harness commit drifted after cohort preparation")
    if files_sha256(EXPERIMENT_SCHEMAS, root=ROOT) != manifest["harness"]["schema_bundle_sha256"]:
        raise ExperimentError("experiment schema bundle drifted after cohort preparation")
    scenario_bundle = cohort_path / "scenario-bundle.json"
    if not scenario_bundle.is_file() or file_sha256(scenario_bundle) != manifest["harness"]["scenario_bundle_sha256"]:
        raise ExperimentError("stored scenario bundle drifted after cohort preparation")
    if (
        file_sha256(PROBE_INPUT) != manifest["harness"]["probe_input_sha256"]
        or file_sha256(PROBE_EXPECTED) != manifest["harness"]["probe_expected_sha256"]
        or file_sha256(PROBE_PROMPT) != manifest["harness"]["probe_prompt_sha256"]
    ):
        raise ExperimentError("probe fixtures drifted after cohort preparation")


def cmd_validate_scenarios(args: argparse.Namespace) -> None:
    scenarios = validate_scenario_bundle(read_json(args.scenarios))
    print(json.dumps({"valid": True, "scenario_count": len(scenarios)}, sort_keys=True))


def cmd_prepare(args: argparse.Namespace) -> None:
    scenarios_path = args.scenarios.resolve()
    scenarios = validate_scenario_bundle(read_json(scenarios_path))
    root = artifact_root(args.artifact_root)
    if git("status", "--porcelain"):
        raise ExperimentError("harness worktree must be clean before preparing an immutable candidate")
    lock, catalog = validate_release_candidate(
        release_tag=args.release_tag,
        release_lock=args.release_lock,
        release_checkout=args.release_checkout,
    )
    codex_version = command_output([str(args.codex_binary.resolve()), "--version"])
    preflight_probe = verify_model_preflight(
        root=root,
        codex_binary=args.codex_binary.resolve(),
        auth_file=args.auth_file.resolve(),
    )
    manifest = seal_manifest(
        product={
            "commit": lock["source"]["commit"],
            "release_tag": args.release_tag,
            "release_lock_sha256": file_sha256(args.release_lock),
            "catalog_sha256": file_sha256(catalog),
        },
        harness={
            "commit": git("rev-parse", "HEAD"),
            "schema_bundle_sha256": files_sha256(EXPERIMENT_SCHEMAS, root=ROOT),
            "scenario_bundle_sha256": object_sha256(read_json(scenarios_path)),
            "probe_input_sha256": file_sha256(PROBE_INPUT),
            "probe_expected_sha256": file_sha256(PROBE_EXPECTED),
            "probe_prompt_sha256": file_sha256(PROBE_PROMPT),
        },
        runtime={
            "codex_version": codex_version,
            "model": "gpt-5.6-terra",
            "reasoning_effort": "medium",
            "isolation": "bubblewrap-linux-v1",
            "timeouts_seconds": DEFAULT_TIMEOUTS,
            "model_preflight": {"status": "passed", "probe": preflight_probe},
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
    if cohort_has_safety_failure(root, manifest=manifest):
        raise ExperimentError("cohort is stopped after a safety failure")
    if args.scenario_id not in manifest["scenario_ids"]:
        raise ExperimentError("scenario is not part of the frozen cohort")
    inventory = resume_inventory(manifest, root)
    unfinished = [item for item in inventory if item["action"] in {"RESUME", "FINISH"}]
    if unfinished:
        current = unfinished[0]
        raise ExperimentError(
            f"finish or resume the active attempt first: {current['scenario_id']} attempt {current['attempt']}"
        )
    eligible = [item for item in inventory if item["action"] in {"START", "RETRY"}]
    if not eligible:
        raise ExperimentError("cohort has no pending scenario")
    expected = eligible[0]
    expected_attempt = int(expected["attempt"]) + 1 if expected["action"] == "RETRY" else 1
    if args.scenario_id != expected["scenario_id"] or args.attempt != expected_attempt:
        raise ExperimentError(
            f"next deterministic attempt is {expected['scenario_id']} attempt {expected_attempt}"
        )
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
    receipt = build_receipt_from_run(
        manifest=manifest,
        scenario_id=args.scenario_id,
        attempt=args.attempt,
        terminal_state=args.terminal_state,
        run_root=run_root,
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
    if command_output([str(args.codex_binary.resolve()), "--version"]) != manifest["runtime"]["codex_version"]:
        raise ExperimentError("Codex version drifted after cohort preparation")
    if not args.new_task:
        if args.release_checkout is None:
            raise ExperimentError("release checkout is required for onboarding turns")
        if git_at(args.release_checkout.resolve(), "rev-parse", "HEAD") != manifest["product"]["commit"]:
            raise ExperimentError("release checkout drifted after cohort preparation")
        if git_at(args.release_checkout.resolve(), "status", "--porcelain"):
            raise ExperimentError("release checkout must remain clean")
    run_root, _ = run_paths(root, args.scenario_id, args.attempt)
    if not (run_root / "events.jsonl").is_file():
        raise ExperimentError("start the run before executing a Codex turn")
    if not args.turn_label or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in args.turn_label):
        raise ExperimentError("invalid turn label")
    if args.new_task:
        if args.turn_label != "new-task-probe" or args.prompt_file is not None:
            raise ExperimentError("new-task probe uses the frozen prompt and turn label")
        prompt = PROBE_PROMPT.read_text(encoding="utf-8")
    else:
        if args.prompt_file is None:
            raise ExperimentError("onboarding turns require a prompt file")
        prompt = args.prompt_file.read_text(encoding="utf-8")
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
    fixture = PROBE_INPUT if args.new_task else args.fixture
    if args.new_task and args.fixture is not None:
        raise ExperimentError("new-task probe uses only the frozen citation fixture")
    if fixture:
        write_secure_bytes(workspace / fixture.name, fixture.read_bytes())
    spec = SandboxSpec(
        codex_binary=args.codex_binary,
        auth_file=args.auth_file,
        codex_home=runtime / "codex-home",
        workspace=workspace,
        release_checkout=None if args.new_task else args.release_checkout,
    )
    stage_timeout = int(manifest["runtime"]["timeouts_seconds"][args.stage])
    if args.new_task != (args.stage == "new_task"):
        raise ExperimentError("new-task turns must use the frozen new_task stage timeout")
    try:
        current_thread, observation = run_turn(
            spec,
            prompt=prompt,
            runtime_root=turn_runtime,
            evidence_path=evidence_path,
            timeout_seconds=stage_timeout,
            stage=args.stage,
            thread_id=None if args.new_task else thread_id,
            expose_release=not args.new_task,
        )
    except ExperimentTimeout as exc:
        journal = EventJournal(
            run_root / "events.jsonl",
            f"{manifest['cohort_id']}/{args.scenario_id}/attempt-{args.attempt:02d}",
        )
        journal.append(
            "INFRA_INVALID",
            "STAGE_TIMEOUT",
            {"stage": exc.stage, "timeout_seconds": exc.timeout_seconds},
        )
        receipt = build_receipt_from_run(
            manifest=manifest,
            scenario_id=args.scenario_id,
            attempt=args.attempt,
            terminal_state="INFRA_INVALID",
            run_root=run_root,
            failure_class=f"TIMEOUT_{exc.stage.upper()}",
        )
        write_secure_json(run_root / "receipt.json", receipt)
        raise
    if not args.new_task:
        write_secure_json(resume_path, {"session_id": current_thread})
    print(observation["final_message"])


def cmd_capture_artifacts(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    run_root, _ = run_paths(root, args.scenario_id, args.attempt)
    workspace_state = run_root / "runtime" / "workspace" / ".evidence-lab"
    plan_source = workspace_state / "installation-plan.json"
    state_source = workspace_state / "installation-state.json"
    for source in (plan_source, state_source):
        if not source.is_file() or source.is_symlink():
            raise ExperimentError(f"fixed Bootstrap artifact is missing: {source.name}")
    plan = read_json(plan_source)
    state = read_json(state_source)
    validate_json_schema(plan, "installation-plan.schema.json")
    validate_json_schema(state, "installation-state.schema.json")
    expected_release = {
        "tag": manifest["product"]["release_tag"],
        "channel": "stable",
        "source_commit": manifest["product"]["commit"],
        "lock_digest": manifest["product"]["release_lock_sha256"],
    }
    if plan.get("release") != expected_release or state.get("release") != expected_release:
        raise ExperimentError("captured Bootstrap artifacts do not match the cohort release")
    if state.get("plan_id") != plan.get("plan_id"):
        raise ExperimentError("captured installation state does not match the plan")
    destinations = {
        plan_source: run_root / "observations" / "plan.json",
        state_source: run_root / "observations" / "installation-state.json",
    }
    for source, destination in destinations.items():
        if destination.exists():
            raise ExperimentError(f"captured artifact is immutable: {destination.name}")
        write_secure_bytes(destination, source.read_bytes())
    print(json.dumps({"captured": True, "plan_id": plan.get("plan_id")}, sort_keys=True))


def cmd_verify_probe(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    run_root, relative_run_id = run_paths(root, args.scenario_id, args.attempt)
    evidence_path = run_root / "observations" / "new-task-probe.json"
    if evidence_path.exists():
        raise ExperimentError("new-task probe evidence already exists")
    raw_jsonl = run_root / "runtime" / "turns" / "new-task-probe" / "codex.stdout.jsonl"
    if not raw_jsonl.is_file():
        raise ExperimentError("new-task probe raw event stream is missing")
    events = parse_codex_jsonl(raw_jsonl.read_text(encoding="utf-8"))
    sandbox_codex_home = Path("/home/researcher/.codex")
    relative_script, command_item = verify_probe_execution(
        events,
        installed_plugin_root=sandbox_codex_home,
    )
    host_script = run_root / "runtime" / "codex-home" / relative_script
    if not host_script.is_file() or host_script.is_symlink():
        raise ExperimentError("new-task probe command is not backed by the run-specific installed cache")
    output = command_item.get("aggregated_output")
    if not isinstance(output, str):
        raise ExperimentError("new-task probe command has no captured output")
    if file_sha256(PROBE_INPUT) != manifest["harness"]["probe_input_sha256"] or file_sha256(PROBE_EXPECTED) != manifest["harness"]["probe_expected_sha256"]:
        raise ExperimentError("frozen probe fixtures drifted after the cohort was prepared")
    actual_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
    expected_hash = file_sha256(PROBE_EXPECTED)
    if actual_hash != expected_hash:
        raise ExperimentError("new-task probe output does not match the frozen fixture")
    evidence = {
        "schema_version": 1,
        "installed_script": relative_script,
        "actual_output_sha256": actual_hash,
        "expected_output_sha256": expected_hash,
        "command_event_sha256": object_sha256(command_item),
        "final_response_sha256": object_sha256(final_agent_message(events)),
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
    summary = summarize_cohort(manifest, rows, cohort_root=root)
    summary["phase"] = "STOPPED_SAFETY" if summary["safety_stop"] else (
        "READY_FOR_REVIEW" if summary["valid_primary_scenarios"] == 10 else "RUNNING"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def cmd_resume(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    rows = resume_inventory(manifest, root)
    print(json.dumps({"cohort_id": manifest["cohort_id"], "runs": rows}, ensure_ascii=False, sort_keys=True))


def cmd_validate(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    manifest = load_manifest(root)
    scenarios = validate_scenario_bundle(read_json(root / "scenario-bundle.json"))
    if [item["id"] for item in scenarios] != manifest["scenario_ids"]:
        raise ExperimentError("stored scenario bundle does not match the cohort manifest")
    if file_sha256(root / "scenario-bundle.json") != manifest["harness"]["scenario_bundle_sha256"]:
        raise ExperimentError("stored scenario bundle hash drifted after preparation")
    runs = resume_inventory(manifest, root)
    rows = receipts(root)
    summary = summarize_cohort(manifest, rows, cohort_root=root)
    index = artifact_index(root)
    print(json.dumps({
        "valid": True,
        "cohort_id": manifest["cohort_id"],
        "run_count": len([item for item in runs if item["state"] != "PENDING"]),
        "receipt_count": len(rows),
        "artifact_count": index["artifact_count"],
        "gate_pass": summary["gate_pass"],
    }, sort_keys=True))


def cmd_seal(args: argparse.Namespace) -> None:
    root = cohort_root(args)
    if (root / "artifact-index.json").exists():
        raise ExperimentError("cohort is already sealed")
    manifest = load_manifest(root)
    summary = summarize_cohort(manifest, receipts(root), cohort_root=root)
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
    prepare.add_argument("--release-checkout", type=Path, required=True)
    prepare.add_argument("--codex-binary", type=Path, required=True)
    prepare.add_argument("--auth-file", type=Path, required=True)
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
    turn.add_argument("--prompt-file", type=Path)
    turn.add_argument("--codex-binary", type=Path, required=True)
    turn.add_argument("--auth-file", type=Path, required=True)
    turn.add_argument("--release-checkout", type=Path)
    turn.add_argument("--fixture", type=Path)
    turn.add_argument("--new-task", action="store_true")
    turn.add_argument("--stage", choices=("turn", "plan", "apply", "new_task"), required=True)
    turn.set_defaults(func=cmd_codex_turn)

    capture = commands.add_parser("capture-artifacts", parents=[common])
    capture.add_argument("--scenario-id", required=True)
    capture.add_argument("--attempt", type=int, default=1)
    capture.set_defaults(func=cmd_capture_artifacts)

    probe = commands.add_parser("verify-probe", parents=[common])
    probe.add_argument("--scenario-id", required=True)
    probe.add_argument("--attempt", type=int, default=1)
    probe.set_defaults(func=cmd_verify_probe)

    for name, function in (
        ("status", cmd_status),
        ("summarize", cmd_status),
        ("resume", cmd_resume),
        ("validate", cmd_validate),
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
