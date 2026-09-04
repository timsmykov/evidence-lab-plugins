#!/usr/bin/env python3
"""Build the onboarding-free all-in-one Evidence Lab research plugin."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
BUNDLE = PACKS / "core" / "evidence-lab-research"
CONFIG = BUNDLE / "bundle.json"
PACK = BUNDLE / "pack.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_skills(config: dict) -> list[tuple[Path, dict]]:
    excluded_skills = set(config["exclude_skills"])
    excluded_quality = set(config["exclude_quality_statuses"])
    excluded_statuses = set(config["exclude_pack_statuses"])
    result: list[tuple[Path, dict]] = []
    seen: set[str] = set()
    for meta_path in sorted(PACKS.glob("*/*/meta.json")):
        pack_root = meta_path.parent
        if pack_root == BUNDLE:
            continue
        meta = load(meta_path)
        if meta["status"] in excluded_statuses:
            continue
        for item in meta.get("skills", []):
            name = item["name"]
            if name in excluded_skills or item["quality_status"] in excluded_quality:
                continue
            source = pack_root / "skills" / name
            if not (source / "SKILL.md").is_file():
                raise ValueError(f"missing canonical skill source: {source.relative_to(ROOT)}")
            if name in seen:
                raise ValueError(f"duplicate bundled skill name: {name}")
            seen.add(name)
            result.append((source, item))
    return result


def definition_errors(config: dict, skills: list[tuple[Path, dict]]) -> list[str]:
    pack = load(PACK)
    errors: list[str] = []
    if pack.get("id") != "evidence-lab-research" or pack.get("distribution_bundle") is not True:
        errors.append("research bundle must remain a distribution-only plugin")
    if pack.get("dependencies") != []:
        errors.append("research bundle must install without plugin dependencies")
    if "evidence-lab-onboarding" not in config.get("exclude_skills", []):
        errors.append("onboarding must remain excluded from the research bundle")
    if any(item[1]["name"] == "evidence-lab-onboarding" for item in skills):
        errors.append("onboarding leaked into the research bundle")
    if (BUNDLE / "onboarding").exists():
        errors.append("onboarding support files must live outside the research bundle")
    return errors


def expected_meta(skills: list[tuple[Path, dict]]) -> dict:
    return {
        "status": "draft",
        "category": "research",
        "risk_level": "team_safe",
        "owner": "Tim",
        "reviewer": "Tim",
        "provenance": {
            "origin": "Distribution-only bundle of canonical Evidence Lab research skills; onboarding remains in the separate evidence-lab-core plugin.",
            "evidence": ["packs/core/evidence-lab-research/bundle.json", "docs/skill-pack-readiness.md"],
            "added_at": "2026-09-04"
        },
        "skills": [item for _, item in skills],
        "portable_to": ["claude", "codex"]
    }


def expected_copies(config: dict, skills: list[tuple[Path, dict]]) -> dict[Path, Path]:
    copies = {BUNDLE / "skills" / source.name: source for source, _ in skills}
    for name, relative in config["license_sources"].items():
        copies[BUNDLE / "LICENSES" / name] = ROOT / relative
    return copies


def tree_state(path: Path) -> dict[str, tuple[str, bool, str]]:
    """Describe a file tree without following links outside the selected root."""
    if path.is_symlink():
        return {".": ("symlink", False, path.readlink().as_posix())}
    if path.is_file():
        return {".": ("file", bool(path.stat().st_mode & 0o111), hashlib.sha256(path.read_bytes()).hexdigest())}
    if not path.is_dir():
        return {}
    state: dict[str, tuple[str, bool, str]] = {".": ("directory", False, "")}
    for item in sorted(path.rglob("*")):
        relative = item.relative_to(path).as_posix()
        if "__pycache__" in item.relative_to(path).parts or item.suffix == ".pyc" or item.name == ".DS_Store":
            continue
        if item.is_symlink():
            state[relative] = ("symlink", False, item.readlink().as_posix())
        elif item.is_dir():
            state[relative] = ("directory", False, "")
        elif item.is_file():
            state[relative] = (
                "file",
                bool(item.stat().st_mode & 0o111),
                hashlib.sha256(item.read_bytes()).hexdigest(),
            )
    return state


def check(config: dict, skills: list[tuple[Path, dict]]) -> list[str]:
    errors = definition_errors(config, skills)
    expected = expected_copies(config, skills)
    for path, target in expected.items():
        if path.is_symlink() or tree_state(path) != tree_state(target):
            errors.append(f"stale bundle copy: {path.relative_to(ROOT)}")
    for directory in (BUNDLE / "skills", BUNDLE / "LICENSES"):
        actual = set(directory.iterdir()) if directory.is_dir() else set()
        wanted = {path for path in expected if path.parent == directory}
        for extra in sorted(actual - wanted):
            errors.append(f"unexpected bundle entry: {extra.relative_to(ROOT)}")
    meta_path = BUNDLE / "meta.json"
    if not meta_path.is_file() or load(meta_path) != expected_meta(skills):
        errors.append(f"stale generated metadata: {meta_path.relative_to(ROOT)}")
    return errors


def build(config: dict, skills: list[tuple[Path, dict]]) -> None:
    expected = expected_copies(config, skills)
    for directory in (BUNDLE / "skills", BUNDLE / "LICENSES"):
        directory.mkdir(parents=True, exist_ok=True)
        wanted = {path for path in expected if path.parent == directory}
        for extra in set(directory.iterdir()) - wanted:
            if extra.is_symlink() or extra.is_file():
                extra.unlink()
            else:
                shutil.rmtree(extra)
    for path, target in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() or path.is_symlink():
            if path.is_symlink() or path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
        if target.is_dir():
            shutil.copytree(target, path, symlinks=False)
        else:
            shutil.copy2(target, path)
    (BUNDLE / "meta.json").write_text(
        json.dumps(expected_meta(skills), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    config = load(CONFIG)
    skills = source_skills(config)
    if args.check:
        errors = check(config, skills)
        if errors:
            print("\n".join(f"FAIL: {item}" for item in errors), file=sys.stderr)
            return 1
        print(f"verified onboarding-free research bundle with {len(skills)} skills")
        return 0
    errors = definition_errors(config, skills)
    if errors:
        print("\n".join(f"FAIL: {item}" for item in errors), file=sys.stderr)
        return 1
    build(config, skills)
    print(f"built onboarding-free research bundle with {len(skills)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
