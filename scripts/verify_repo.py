#!/usr/bin/env python3
"""Repository gate: structure, schemas, routing evals, privacy, version discipline.

Run locally before opening a pull request:

    python3 scripts/verify_repo.py

CI runs the same command. If a rule is too broad, narrow the rule here in a
reviewed change — do not delete the check.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - CI installs it
    print("FAIL: jsonschema is required (pip install jsonschema)")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
SCHEMAS = ROOT / "schemas"

REQUIRED_REPO_FILES = [
    "README.md",
    "START.md",
    "START.ru.md",
    "BOOTSTRAP.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSING.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
    "TRADEMARKS.md",
    "requirements-ci.txt",
    ".gitleaks.toml",
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    "docs/architecture.md",
    "docs/authoring.md",
    "docs/review-checklist.md",
    "docs/sanitization-policy.md",
    "docs/release-process.md",
    "docs/pack-boundary-report.md",
    "docs/skill-pack-readiness.md",
    "docs/openai-plugin-audit.md",
    "docs/external-plugin-verification.md",
    "catalog/scenarios.json",
    "catalog/pack-boundary-decisions.json",
    "catalog/external-plugin-candidates.json",
    "catalog/openai-plugin-audit.json",
    "schemas/plugin.schema.json",
    "schemas/codex-plugin.schema.json",
    "schemas/codex-marketplace.schema.json",
    "schemas/pack.schema.json",
    "schemas/profile.schema.json",
    "schemas/selection-plan.schema.json",
    "schemas/selection-policy.schema.json",
    "schemas/installation-plan.schema.json",
    "schemas/installation-state.schema.json",
    "schemas/reconcile-plan.schema.json",
    "schemas/reconcile-state.schema.json",
    "schemas/release-lock.schema.json",
    "schemas/onboarding-questions.schema.json",
    "schemas/onboarding-plan-copy.schema.json",
    "schemas/onboarding-answers.schema.json",
    "schemas/normalization-candidate.schema.json",
    "schemas/normalization-result.schema.json",
    "schemas/scenario-matrix.schema.json",
    "schemas/pack-boundary-decisions.schema.json",
    "schemas/external-plugin-candidates.schema.json",
    "schemas/external-plugin-plan.schema.json",
    "schemas/meta.schema.json",
    "schemas/eval.schema.json",
    "schemas/marketplace.schema.json",
]

REQUIRED_PACK_FILES = ["README.md", "CHANGELOG.md", "pack.json", "meta.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]
ALLOWED_PACK_LICENSES = {"MIT", "MIT AND Apache-2.0"}
PROPRIETARY_LICENSE_MARKER = "LicenseRef-Evidence-Lab-" + "Proprietary"
MIT_LICENSE_MARKERS = (
    "MIT License",
    "Permission is hereby granted, free of charge",
    'THE SOFTWARE IS PROVIDED "AS IS"',
)

# Anything matching these must never reach a shared plugin.
PRIVATE_PATTERNS = {
    "private_host_path": re.compile(r"/root/(?:\.hermes|hermes-workspace|\.ssh|\.config|\.claude)", re.I),
    "ip_address": re.compile(r"\b(?!(?:127\.0\.0\.1|0\.0\.0\.0)\b)(?:\d{1,3}\.){3}\d{1,3}\b"),
    "token": re.compile(
        r"\b(?:ghp_[A-Za-z0-9_]{20,}|gho_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}"
        r"|sk-[A-Za-z0-9_\-]{20,}|xox[baprs]-[A-Za-z0-9_\-]{20,})\b"
    ),
    "notion_id": re.compile(r"(?:notion\.so|notion\.com)/[A-Za-z0-9_-]*[0-9a-f]{32}", re.I),
    "bare_uuid": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
}
# Files where a contact address is legitimate.
EMAIL_ALLOWED = {"LICENSE", "SECURITY.md"}

# Scaffolded plugins must be filled in before they can be merged.
PLACEHOLDER_PATTERN = re.compile(r"REPLACE ME|__PLUGIN__|__SKILL__|__OWNER__|__REVIEWER__")

# English-first, everywhere. A skill is read by a routing agent and the registry
# has to port across runtimes, so the repository carries no Russian prose. If a
# skill ever needs a localized companion, it goes in an explicitly named
# `*.ru.md` / `*.ru.json` file next to the English original — never inline.
CYRILLIC_PATTERN = re.compile(r"[А-Яа-яЁё]")
LOCALIZED_SUFFIXES = (".ru.md", ".ru.json")
SELF = Path(__file__).resolve()

SCANNED_SUFFIXES = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".txt", ".csv", ".bib", ".mplstyle"}
BANNED_NAMES = {"__pycache__", ".pytest_cache", ".DS_Store", ".env"}
BANNED_SUFFIXES = {".pyc", ".pyo"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None


def validate(instance, schema_name: str, label: str) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    for err in sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: e.path):
        location = "/".join(str(p) for p in err.path) or "<root>"
        fail(f"{label}: {location}: {err.message}")


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML frontmatter reader: top-level scalars, folded block scalars."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip().strip("\"'")
        elif key and line.strip():
            fields[key] += " " + line.strip().strip("\"'")
    return fields


# --------------------------------------------------------------------------- repo


def check_repo_files() -> None:
    for rel in REQUIRED_REPO_FILES:
        if not (ROOT / rel).exists():
            fail(f"missing required file: {rel}")

    license_path = ROOT / "LICENSE"
    if license_path.exists():
        license_text = license_path.read_text(encoding="utf-8")
        for marker in MIT_LICENSE_MARKERS:
            if marker not in license_text:
                fail(f"LICENSE: missing canonical MIT text marker {marker!r}")

    template_pack = ROOT / "templates" / "pack" / "pack.json"
    if template_pack.exists():
        template = load_json(template_pack)
        if template is not None and template.get("license") != "MIT":
            fail("templates/pack/pack.json: new Evidence Lab packs must default to MIT")


def check_marketplaces() -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    if not path.exists():
        return
    data = load_json(path)
    if data is None:
        return
    validate(data, "marketplace.schema.json", "marketplace.json")
    for entry in data.get("plugins", []):
        source = Path(entry.get("source", "").lstrip("./"))
        if not (ROOT / source).is_dir():
            fail(f"marketplace.json: entry {entry.get('name')} points at missing {source}")

    codex_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    if not codex_path.exists():
        return
    codex = load_json(codex_path)
    if codex is None:
        return
    validate(codex, "codex-marketplace.schema.json", "Codex marketplace.json")
    for entry in codex.get("plugins", []):
        source = Path(entry.get("source", {}).get("path", "").lstrip("./"))
        if not (ROOT / source).is_dir():
            fail(f"Codex marketplace.json: entry {entry.get('name')} points at missing {source}")


def check_external_plugin_registry() -> None:
    path = ROOT / "catalog" / "external-plugin-candidates.json"
    if not path.exists():
        return
    data = load_json(path)
    if data is None:
        return
    validate(data, "external-plugin-candidates.schema.json", "external-plugin-candidates.json")
    ids = [plugin.get("id") for plugin in data.get("plugins", [])]
    if len(ids) != len(set(ids)):
        fail("external-plugin-candidates.json: plugin IDs must be unique")
    audit_path = ROOT / "catalog" / "openai-plugin-audit.json"
    audit = load_json(audit_path) if audit_path.exists() else None
    if audit is not None:
        if data.get("observed_at") != audit.get("fetched_at"):
            fail("external-plugin-candidates.json: observed_at does not match the audited snapshot")
        if data.get("source", {}).get("snapshot_sha256") != audit.get("snapshot_sha256"):
            fail("external-plugin-candidates.json: snapshot hash does not match the catalog audit")
        observed = {row.get("id"): row for row in audit.get("reviewed_candidates", [])}
        for plugin in data.get("plugins", []):
            row = observed.get(plugin.get("id"))
            if row is None:
                fail(f"external-plugin-candidates.json: {plugin.get('display_name')} is absent from audited candidates")
                continue
            if row.get("display_name") != plugin.get("display_name") or row.get("version") != plugin.get("observed_version"):
                fail(f"external-plugin-candidates.json: {plugin.get('display_name')} identity/version differs from the audit")
    for plugin in data.get("plugins", []):
        if plugin.get("component_type") in {"directory-app", "hybrid"} and plugin.get("selection", {}).get("automatic"):
            fail(f"external-plugin-candidates.json: {plugin.get('display_name')} cannot silently select an app connection")
        if plugin.get("policy") != "approved-baseline" and plugin.get("selection", {}).get("automatic"):
            fail(f"external-plugin-candidates.json: {plugin.get('display_name')} cannot be automatic before baseline approval")


def check_generated_reports() -> None:
    for command, label in (
        ([sys.executable, "scripts/audit_skill_packs.py", "--check"], "skill-pack readiness report"),
        ([sys.executable, "scripts/audit_openai_plugins.py", "--check"], "OpenAI plugin audit report"),
        ([sys.executable, "scripts/test_openai_plugin_audit.py"], "OpenAI plugin audit regression tests"),
    ):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            fail(result.stderr.strip() or result.stdout.strip() or f"{label} is stale")


# ------------------------------------------------------------------------- plugin


def check_skill(plugin: str, skill_dir: Path, declared: dict) -> None:
    label = f"{plugin}/{skill_dir.name}"
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        fail(f"{label}: missing SKILL.md")
        return

    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm.get("name") != skill_dir.name:
        fail(f"{label}: SKILL.md name '{fm.get('name')}' does not match directory")
    description = fm.get("description", "")
    if len(description) < 80:
        fail(f"{label}: description is {len(description)} chars; needs >= 80 with explicit triggers")
    if not re.search(r"\b(use|activates?|trigger|when)\b", description, re.I):
        warn(f"{label}: description does not say when to load the skill")

    if skill_dir.name not in declared:
        fail(f"{label}: skill is on disk but absent from meta.json")
    else:
        for rel in declared[skill_dir.name].get("deterministic_parts", []):
            target = skill_dir / rel
            if not target.is_file():
                fail(f"{label}: deterministic part does not exist: {rel}")

    evals = skill_dir / "evals" / "trigger_eval.json"
    if not evals.exists():
        fail(f"{label}: missing evals/trigger_eval.json — routing is untested")
        return
    cases = load_json(evals)
    if cases is None:
        return
    validate(cases, "eval.schema.json", f"{label}/evals")
    negatives = sum(1 for c in cases if isinstance(c, dict) and c.get("should_trigger") is False)
    if negatives < 3:
        fail(f"{label}: only {negatives} negative eval case(s); need >= 3 near-misses")

    for script in (skill_dir / "scripts").glob("*"):
        is_entrypoint = script.suffix == ".sh" or (script.suffix == ".py" and not script.name.startswith("_"))
        if is_entrypoint and not script.stat().st_mode & 0o111:
            warn(f"{label}: {script.name} is not executable")


def check_markdown_agents(plugin_dir: Path, plugin: str) -> None:
    for command in (plugin_dir / "commands").glob("*.md"):
        fm = parse_frontmatter(command.read_text(encoding="utf-8"))
        if not fm.get("description"):
            fail(f"{plugin}/commands/{command.name}: missing description in frontmatter")
    for agent in (plugin_dir / "agents").glob("*.md"):
        fm = parse_frontmatter(agent.read_text(encoding="utf-8"))
        if not fm.get("name") or not fm.get("description"):
            fail(f"{plugin}/agents/{agent.name}: frontmatter needs name and description")


def check_pack(pack_dir: Path) -> None:
    plugin = pack_dir.name
    for rel in REQUIRED_PACK_FILES:
        if not (pack_dir / rel).exists():
            fail(f"{plugin}: missing {rel}")
    pack_path = pack_dir / "pack.json"
    manifest_path = pack_dir / ".claude-plugin" / "plugin.json"
    codex_manifest_path = pack_dir / ".codex-plugin" / "plugin.json"
    meta_path = pack_dir / "meta.json"
    if not all(path.exists() for path in (pack_path, manifest_path, codex_manifest_path, meta_path)):
        return

    pack, manifest, codex_manifest, meta = load_json(pack_path), load_json(manifest_path), load_json(codex_manifest_path), load_json(meta_path)
    if any(value is None for value in (pack, manifest, codex_manifest, meta)):
        return
    validate(pack, "pack.schema.json", f"{plugin}/pack.json")
    validate(manifest, "plugin.schema.json", f"{plugin}/plugin.json")
    validate(codex_manifest, "codex-plugin.schema.json", f"{plugin}/Codex plugin.json")
    validate(meta, "meta.schema.json", f"{plugin}/meta.json")

    declared_license = pack.get("license")
    if declared_license not in ALLOWED_PACK_LICENSES:
        fail(
            f"{plugin}: unsupported pack license {declared_license!r}; "
            f"allowed expressions are {sorted(ALLOWED_PACK_LICENSES)}"
        )

    if pack.get("id") != plugin:
        fail(f"{plugin}: pack.json id '{pack.get('id')}' does not match directory")
    expected_layer = {"core": "core", "workflows": "workflow", "domains": "domain", "local": "local"}.get(pack_dir.parent.name)
    if pack.get("layer") != expected_layer:
        fail(f"{plugin}: layer '{pack.get('layer')}' does not match {pack_dir.parent.name}/")
    for host, host_manifest in (("Claude", manifest), ("Codex", codex_manifest)):
        if host_manifest.get("name") != plugin:
            fail(f"{plugin}: {host} manifest name '{host_manifest.get('name')}' does not match directory")
        if host_manifest.get("version") != pack.get("version"):
            fail(f"{plugin}: {host} manifest version does not match pack.json")
        if host_manifest.get("license") != pack.get("license"):
            fail(f"{plugin}: {host} manifest license does not match pack.json")
    if meta.get("status") == "production":
        if meta.get("owner") == meta.get("reviewer"):
            fail(f"{plugin}: production plugin needs a reviewer different from the owner")
        if not meta.get("provenance", {}).get("reviewed_at"):
            fail(f"{plugin}: production plugin needs provenance.reviewed_at")

    declared = {s["name"]: s for s in meta.get("skills", []) if isinstance(s, dict)}
    skills_dir = pack_dir / "skills"
    on_disk = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.is_dir() else set()
    if not on_disk:
        fail(f"{plugin}: a plugin must ship at least one skill")
    for missing in sorted(set(declared) - on_disk):
        fail(f"{plugin}: meta.json declares skill '{missing}' with no directory")
    for name in sorted(on_disk):
        check_skill(plugin, skills_dir / name, declared)

    skill_texts = [
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(skills_dir.glob("*/SKILL.md"))
    ]
    has_k_dense_content = any("K-Dense" in text for text in skill_texts)
    has_apache_content = any(
        parse_frontmatter(text).get("license") == "Apache-2.0"
        for text in skill_texts
    )
    if has_k_dense_content:
        for rel in ("THIRD_PARTY_NOTICES.md", "LICENSES/K-Dense-MIT.txt"):
            if not (pack_dir / rel).is_file():
                fail(f"{plugin}: K-Dense-derived content requires {rel}")
    if has_apache_content:
        if declared_license != "MIT AND Apache-2.0":
            fail(f"{plugin}: Apache-2.0 skill is shipped but pack license omits it")
        if not (pack_dir / "LICENSES" / "Apache-2.0.txt").is_file():
            fail(f"{plugin}: Apache-2.0 skill requires LICENSES/Apache-2.0.txt")
    elif declared_license == "MIT AND Apache-2.0":
        fail(f"{plugin}: pack declares Apache-2.0 but ships no Apache-licensed skill")

    check_markdown_agents(pack_dir, plugin)


# ------------------------------------------------------------------- hygiene/git


def check_markdown_links(path: Path, text: str) -> None:
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for raw_target in MARKDOWN_LINK.findall(line):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                fail(f"{path.relative_to(ROOT)}:{line_number}: broken relative link ({raw_target})")


def check_hygiene() -> None:
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".git", "dist"}:
            continue  # dist/ is disposable build output
        if path.name in BANNED_NAMES or path.suffix in BANNED_SUFFIXES:
            fail(f"remove generated/private artefact: {rel}")
            continue
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if rel.parts and rel.parts[0] == "templates":
            continue  # placeholders are not real content
        text = path.read_text(encoding="utf-8", errors="replace")
        if PROPRIETARY_LICENSE_MARKER in text:
            fail(f"{rel}: obsolete proprietary license marker remains")
        if path.suffix == ".md":
            check_markdown_links(path, text)
        if rel.parts and rel.parts[0] == "packs":
            placeholder = PLACEHOLDER_PATTERN.search(text)
            if placeholder:
                fail(f"{rel}: unfilled scaffold placeholder '{placeholder.group(0)}'")
        if path.resolve() != SELF and not path.name.endswith(LOCALIZED_SUFFIXES):
            cyrillic = CYRILLIC_PATTERN.search(text)
            if cyrillic:
                line = text[: cyrillic.start()].count("\n") + 1
                fail(
                    f"{rel}:{line}: non-English content (the registry is English-only; "
                    "put translations in a separate *.ru.md / *.ru.json file)"
                )
        for label, pattern in PRIVATE_PATTERNS.items():
            if label == "email" and path.name in EMAIL_ALLOWED:
                continue
            if label == "bare_uuid" and rel.parts[0] == "scripts":
                continue
            match = pattern.search(text)
            if match:
                fail(f"{rel}: {label} leaked ({match.group(0)[:40]})")


def changed_packs() -> set[tuple[str, str]]:
    """Packs touched relative to origin/main, when that ref exists."""
    for base in ("origin/main", "main"):
        try:
            out = subprocess.run(
                ["git", "diff", "--name-only", f"{base}...HEAD"],
                cwd=ROOT, capture_output=True, text=True, check=True,
            ).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        return {
            (Path(line).parts[1], Path(line).parts[2])
            for line in out.splitlines()
            if line.startswith("packs/") and len(Path(line).parts) > 2
        }
    return set()


def check_version_bump() -> None:
    touched = changed_packs()
    if not touched:
        return
    for layer, name in sorted(touched):
        pack_dir = PACKS / layer / name
        pack_path = pack_dir / "pack.json"
        if not pack_path.exists():
            continue
        try:
            previous = subprocess.run(
                ["git", "show", f"origin/main:packs/{layer}/{name}/pack.json"],
                cwd=ROOT, capture_output=True, text=True, check=True,
            ).stdout
        except subprocess.CalledProcessError:
            continue  # new plugin
        old = json.loads(previous).get("version")
        new = load_json(pack_path).get("version")
        try:
            old_parts = tuple(int(part) for part in old.split("."))
            new_parts = tuple(int(part) for part in new.split("."))
        except (AttributeError, ValueError):
            fail(f"{name}: cannot compare invalid SemVer values {old!r} and {new!r}")
            continue
        if new_parts <= old_parts:
            fail(f"{name}: content changed but version did not increase ({old} -> {new})")
        changelog = (pack_dir / "CHANGELOG.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## \[([^]]+)\]", changelog, flags=re.MULTILINE)
        if not headings or headings[0] != new:
            fail(f"{name}: current version {new} must be the newest CHANGELOG.md entry")


def main() -> int:
    check_repo_files()
    check_marketplaces()
    check_external_plugin_registry()
    check_generated_reports()
    if PACKS.is_dir():
        for pack_dir in sorted(path.parent for path in PACKS.glob("*/*/pack.json")):
            check_pack(pack_dir)
    check_hygiene()
    check_version_bump()

    for message in warnings:
        print(f"WARN: {message}")
    for message in errors:
        print(f"FAIL: {message}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: repository verified ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
