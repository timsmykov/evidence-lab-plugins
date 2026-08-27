#!/usr/bin/env python3
"""Behavior checks for mandatory Core personal skill authoring."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "packs/core/evidence-lab-core/skills/personal-skill-authoring"
SCAFFOLD = SKILL / "scripts/scaffold_personal_skill.py"
VALIDATE = SKILL / "scripts/validate_personal_skill.py"


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode != expect:
        raise AssertionError(result.stderr or result.stdout)
    return result


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp)
        command = [
            str(SCAFFOLD),
            "--name", "weekly-table-check",
            "--description", "Checks a recurring collaborator table and activates when a reusable validation workflow is requested.",
            "--output-dir", str(output),
        ]
        for index in range(5):
            command.extend(["--positive", f"Create reusable table check case {index}"])
        for index in range(3):
            command.extend(["--negative", f"Perform one-off unrelated task {index}"])
        run(*command)
        target = output / "weekly-table-check"
        run(str(VALIDATE), str(target))
        cases = json.loads((target / "evals/trigger_eval.json").read_text(encoding="utf-8"))
        assert len(cases) == 8
        assert (target / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: weekly-table-check")
        run(*command, expect=2)

        invalid = command.copy()
        invalid[invalid.index("weekly-table-check")] = "Unsafe_Name"
        invalid[invalid.index(str(output))] = str(output / "other")
        run(*invalid, expect=2)

    print("PASS: personal skill scaffolding, validation, no-overwrite, and unsafe-name checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
