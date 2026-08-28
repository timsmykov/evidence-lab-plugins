#!/usr/bin/env python3
"""Linux/Bubblewrap adapter for real Codex experiment turns.

The adapter keeps resumable Codex runtime state in a protected local directory
and emits a separate sanitized observation stream for experiment evidence.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from onboarding_experiment import (
    ExperimentError,
    assert_sanitized,
    canonical_bytes,
    final_agent_message,
    object_sha256,
    parse_codex_jsonl,
    write_secure_bytes,
    write_secure_json,
)


@dataclass(frozen=True)
class SandboxSpec:
    codex_binary: Path
    auth_file: Path
    codex_home: Path
    workspace: Path
    release_checkout: Path | None = None


def _existing_system_mounts() -> list[str]:
    args: list[str] = []
    for path in ("/usr", "/bin", "/lib", "/lib64", "/etc"):
        if Path(path).exists():
            args.extend(("--ro-bind", path, path))
    return args


def validate_spec(spec: SandboxSpec) -> None:
    if not spec.codex_binary.is_file() or not os.access(spec.codex_binary, os.X_OK):
        raise ExperimentError("Codex binary is missing or not executable")
    if not spec.auth_file.is_file() or spec.auth_file.is_symlink():
        raise ExperimentError("Codex auth file must be a regular non-symlink file")
    if spec.release_checkout is not None and not spec.release_checkout.is_dir():
        raise ExperimentError("release checkout does not exist")
    for directory in (spec.codex_home, spec.workspace):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)


def bwrap_prefix(spec: SandboxSpec, *, expose_release: bool) -> list[str]:
    validate_spec(spec)
    args = [
        "bwrap",
        "--unshare-all",
        "--share-net",
        "--die-with-parent",
        "--new-session",
        "--tmpfs",
        "/",
        *_existing_system_mounts(),
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--dir",
        "/home",
        "--dir",
        "/home/researcher",
        "--dir",
        "/opt",
        "--ro-bind",
        str(spec.codex_binary.resolve()),
        "/opt/codex",
        "--bind",
        str(spec.codex_home.resolve()),
        "/home/researcher/.codex",
        "--ro-bind",
        str(spec.auth_file.resolve()),
        "/home/researcher/.codex/auth.json",
        "--bind",
        str(spec.workspace.resolve()),
        "/workspace",
    ]
    if expose_release:
        if spec.release_checkout is None:
            raise ExperimentError("release checkout is required for onboarding turns")
        args.extend(("--ro-bind", str(spec.release_checkout.resolve()), "/opt/evidence-lab-release"))
    args.extend(
        (
            "--clearenv",
            "--setenv",
            "HOME",
            "/home/researcher",
            "--setenv",
            "CODEX_HOME",
            "/home/researcher/.codex",
            "--setenv",
            "PATH",
            "/opt:/usr/local/bin:/usr/bin",
            "--setenv",
            "LANG",
            "C.UTF-8",
            "--chdir",
            "/workspace",
        )
    )
    return args


def codex_exec_args(*, prompt: str, thread_id: str | None) -> list[str]:
    common = [
        "--json",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "-m",
        "gpt-5.6-terra",
        "-c",
        'model_reasoning_effort="medium"',
    ]
    if thread_id:
        return ["/opt/codex", "exec", "resume", thread_id, prompt, *common]
    return ["/opt/codex", "exec", prompt, *common, "-C", "/workspace"]


def thread_id_from_events(events: Sequence[dict]) -> str:
    for event in events:
        if event.get("type") == "thread.started" and isinstance(event.get("thread_id"), str):
            return event["thread_id"]
    raise ExperimentError("Codex stream has no thread.started event")


def sanitized_observation(events: Sequence[dict]) -> dict:
    def normalize(text: str) -> str:
        return (
            text.replace("/home/researcher/.codex", "$CODEX_HOME")
            .replace("/opt/evidence-lab-release", "$RELEASE")
            .replace("/workspace", "$WORKSPACE")
        )

    messages = []
    commands = []
    for event in events:
        item = event.get("item")
        if event.get("type") != "item.completed" or not isinstance(item, dict):
            continue
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            messages.append(normalize(item["text"]))
        if item.get("type") == "command_execution":
            command = item.get("command", "")
            output = item.get("aggregated_output", "")
            commands.append(
                {
                    "command": normalize(command),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                    "output_sha256": object_sha256(output),
                }
            )
    observation = {
        "schema_version": 1,
        "final_message": normalize(final_agent_message(events)),
        "messages": messages,
        "commands": commands,
    }
    assert_sanitized(observation)
    return observation


def run_turn(
    spec: SandboxSpec,
    *,
    prompt: str,
    runtime_root: Path,
    evidence_path: Path,
    timeout_seconds: int,
    thread_id: str | None = None,
    expose_release: bool = True,
) -> tuple[str, dict]:
    if shutil.which("bwrap") is None:
        raise ExperimentError("bubblewrap is not installed")
    command = [
        *bwrap_prefix(spec, expose_release=expose_release),
        *codex_exec_args(prompt=prompt, thread_id=thread_id),
    ]
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ExperimentError(f"Codex turn timed out after {timeout_seconds} seconds") from exc
    runtime_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(runtime_root, 0o700)
    write_secure_bytes(runtime_root / "codex.stdout.jsonl", result.stdout.encode("utf-8"))
    write_secure_bytes(runtime_root / "codex.stderr.txt", result.stderr.encode("utf-8"))
    if result.returncode:
        raise ExperimentError(f"Codex process failed with exit code {result.returncode}")
    events = parse_codex_jsonl(result.stdout)
    current_thread = thread_id_from_events(events)
    write_secure_json(runtime_root / "resume.json", {"session_id": current_thread})
    observation = sanitized_observation(events)
    write_secure_json(evidence_path, observation)
    return current_thread, observation
