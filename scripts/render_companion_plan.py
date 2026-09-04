#!/usr/bin/env python3
"""Render the audited Codex companion-plugin diff for onboarding."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COPY_ROOT = ROOT / "packs" / "core" / "evidence-lab-core" / "onboarding"


def load_copy(locale: str) -> dict:
    suffix = ".ru.json" if locale == "ru" else ".json"
    return json.loads((COPY_ROOT / f"companion-plugin-copy{suffix}").read_text(encoding="utf-8"))


def render(plan: dict, inventory: dict, locale: str) -> str:
    copy = load_copy(locale)
    lines = [f"## {copy['heading']}", "", copy["intro"], ""]
    for action in plan.get("actions", []):
        state = copy["states"].get(action["action"])
        if state is None:
            raise ValueError(f"missing companion-plugin copy for {action['action']}")
        lines.extend([f"- **{action['display_name']}** — {state}"])
    if not plan.get("actions"):
        lines.append("- —")
    lines.extend([
        "",
        copy["audit"].format(plugins=len(inventory.get("plugins", [])), skills=len(inventory.get("skills", []))),
        "",
        f"**{copy['pending']}**",
        "",
    ])
    return "\n".join(lines)
