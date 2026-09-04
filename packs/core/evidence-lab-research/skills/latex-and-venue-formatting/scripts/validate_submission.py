#!/usr/bin/env python3
"""Validate a LaTeX project against a source-backed venue requirements record.

The validator is deliberately conservative. It checks reproducible source,
bibliography, log, PDF, and metadata signals, but it never claims to prove
margin, font-size, excluded-section, anonymity, or portal compliance.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


IGNORED_DIRS = {".git", ".hg", ".svn", "build", "dist", "out", "output", "__pycache__"}
MAX_FILES = 500
MAX_FILE_BYTES = 5_000_000
CITE_COMMAND = re.compile(
    r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|autocite|parencite|textcite|footcite|nocite)\*?"
    r"(?:\[[^\]]*\]){0,2}\{([^{}]+)\}"
)
REF_COMMAND = re.compile(r"\\(?:ref|eqref|autoref|pageref|cref|Cref)\*?\{([^{}]+)\}")
LABEL_COMMAND = re.compile(r"\\label\{([^{}]+)\}")
SECTION_COMMAND = re.compile(r"\\(?:part|chapter|section|subsection|subsubsection)\*?\{([^{}]+)\}")
PACKAGE_COMMAND = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^{}]+)\}")
ENV_COMMAND = re.compile(r"\\(begin|end)\{([^{}]+)\}")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME|XX+|CITATION NEEDED|INSERT (?:TEXT|FIGURE|TABLE))\b", re.I)


def add(results: list[dict], code: str, status: str, message: str, **details: object) -> None:
    row = {"code": code, "status": status, "message": message}
    if details:
        row["details"] = details
    results.append(row)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def strip_comments(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        cut = len(line)
        for index, char in enumerate(line):
            if char == "%":
                backslashes = 0
                cursor = index - 1
                while cursor >= 0 and line[cursor] == "\\":
                    backslashes += 1
                    cursor -= 1
                if backslashes % 2 == 0:
                    cut = index
                    break
        cleaned.append(line[:cut])
    return "\n".join(cleaned)


def tex_files(project: Path) -> list[Path]:
    paths = []
    for path in project.rglob("*.tex"):
        if any(part in IGNORED_DIRS for part in path.relative_to(project).parts):
            continue
        if path.is_file():
            paths.append(path)
            if len(paths) > MAX_FILES:
                raise ValueError(f"more than {MAX_FILES} .tex files; narrow the project scope")
    return sorted(paths)


def read_tex(path: Path) -> str:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"LaTeX source exceeds {MAX_FILE_BYTES} bytes: {path}")
    return strip_comments(path.read_text(encoding="utf-8", errors="replace"))


def balanced_braces(text: str) -> tuple[bool, int | None]:
    depth = 0
    for index, char in enumerate(text):
        if char not in "{}":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            continue
        depth += 1 if char == "{" else -1
        if depth < 0:
            return False, index
    return depth == 0, None if depth == 0 else len(text)


def environment_errors(text: str) -> list[str]:
    stack: list[str] = []
    errors = []
    for kind, name in ENV_COMMAND.findall(text):
        if kind == "begin":
            stack.append(name)
        elif not stack:
            errors.append(f"unexpected \\end{{{name}}}")
        elif stack[-1] != name:
            errors.append(f"expected \\end{{{stack[-1]}}}, found \\end{{{name}}}")
            stack.pop()
        else:
            stack.pop()
    errors.extend(f"unclosed \\begin{{{name}}}" for name in reversed(stack))
    return errors


def normalize_heading(value: str) -> str:
    value = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", "", value)
    value = re.sub(r"[^A-Za-z0-9]+", " ", value)
    return " ".join(value.lower().split())


def bibliography_keys(paths: list[Path]) -> tuple[set[str], list[str]]:
    keys: set[str] = set()
    duplicates = []
    entry = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.I)
    for path in paths:
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            continue
        for key in entry.findall(path.read_text(encoding="utf-8", errors="replace")):
            if key in keys:
                duplicates.append(key)
            keys.add(key)
    return keys, sorted(set(duplicates))


def discover_bibliographies(project: Path, source: str) -> list[Path]:
    found: set[Path] = set()
    for pattern in (
        re.compile(r"\\bibliography\{([^{}]+)\}"),
        re.compile(r"\\addbibresource(?:\[[^\]]*\])?\{([^{}]+)\}"),
    ):
        for group in pattern.findall(source):
            for raw in group.split(","):
                raw = raw.strip()
                if not raw:
                    continue
                candidate = project / raw
                if candidate.suffix.lower() != ".bib":
                    candidate = candidate.with_suffix(".bib")
                found.add(candidate.resolve())
    if not found:
        found.update(path.resolve() for path in project.glob("*.bib"))
    return sorted(found)


def command_output(command: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def parse_pdfinfo(pdf: Path) -> dict[str, str] | None:
    result = command_output(["pdfinfo", str(pdf)])
    if result is None or result.returncode:
        return None
    info = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    return info


def parse_pdffonts(pdf: Path) -> list[dict] | None:
    result = command_output(["pdffonts", str(pdf)])
    if result is None or result.returncode:
        return None
    fonts = []
    for line in result.stdout.splitlines()[2:]:
        fields = line.split()
        if len(fields) >= 6:
            fonts.append({"name": fields[0], "type": fields[1], "embedded": fields[3], "subset": fields[4]})
    return fonts


def validate_requirements(data: dict, results: list[dict], max_source_age_days: int) -> None:
    if data.get("schema_version") != 1:
        add(results, "requirements.schema", "fail", "schema_version must be 1")

    target = data.get("target")
    required_target = ("venue", "year_or_cycle", "track", "document_type", "stage", "authoring_format")
    if not isinstance(target, dict):
        add(results, "requirements.target", "fail", "target must be an object")
    else:
        missing = [key for key in required_target if not str(target.get(key, "")).strip()]
        if missing:
            add(results, "requirements.target", "fail", "target fields are incomplete", missing=missing)
        else:
            add(results, "requirements.target", "pass", "exact venue target is recorded")

    sources = data.get("official_sources")
    if not isinstance(sources, list) or not sources:
        add(results, "requirements.sources", "fail", "at least one official source is required")
    else:
        today = date.today()
        for index, source in enumerate(sources):
            prefix = f"requirements.sources[{index}]"
            if not isinstance(source, dict) or not valid_url(source.get("url")):
                add(results, prefix, "fail", "source requires an http(s) URL")
                continue
            checked = parse_iso_date(source.get("checked_at"))
            if checked is None:
                add(results, prefix, "fail", "checked_at must be an ISO date")
            elif checked > today:
                add(results, prefix, "fail", "checked_at cannot be in the future")
            elif (today - checked).days > max_source_age_days:
                add(
                    results,
                    prefix,
                    "manual",
                    "official source is older than the configured freshness window",
                    checked_at=checked.isoformat(),
                    age_days=(today - checked).days,
                )
            else:
                add(results, prefix, "pass", "official source URL and checked date are recorded")

    template = data.get("template")
    allowed_status = {"official", "publisher-provided", "user-provided", "generic", "none"}
    if not isinstance(template, dict) or template.get("status") not in allowed_status:
        add(results, "requirements.template", "fail", "template status is missing or unsupported")
    else:
        status = template["status"]
        if status in {"official", "publisher-provided"} and not valid_url(template.get("source_url")):
            add(results, "requirements.template", "fail", "official templates require a source URL")
        elif status == "generic":
            add(results, "requirements.template", "manual", "generic scaffold must be replaced if the venue requires an official template")
        else:
            add(results, "requirements.template", "pass", f"template status recorded as {status}")
        if not template.get("license_or_terms_checked"):
            add(results, "requirements.template-license", "manual", "template license or use terms are not confirmed")
        if template.get("modified"):
            add(results, "requirements.template-integrity", "manual", "template is marked modified; verify that modifications are permitted")

    constraints = data.get("constraints")
    if not isinstance(constraints, dict):
        add(results, "requirements.constraints", "fail", "constraints must be an object")
    else:
        maximum = constraints.get("max_content_pages")
        counted = constraints.get("content_pages")
        if maximum is not None and (not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1):
            add(results, "requirements.page-limit", "fail", "max_content_pages must be null or a positive integer")
        elif counted is not None and (not isinstance(counted, int) or isinstance(counted, bool) or counted < 0):
            add(results, "requirements.page-limit", "fail", "content_pages must be null or a non-negative integer")
        elif maximum is not None and counted is not None and counted > maximum:
            add(results, "requirements.page-limit", "fail", "content page limit is exceeded", content_pages=counted, maximum=maximum)
        elif maximum is not None and counted is None:
            add(results, "requirements.page-limit", "manual", "content_pages must be counted according to the official rule")
        elif maximum is not None:
            add(results, "requirements.page-limit", "pass", "reported content pages are within the recorded limit", content_pages=counted, maximum=maximum)

    manual = data.get("manual_checks")
    if not isinstance(manual, dict):
        add(results, "requirements.manual", "fail", "manual_checks must be an object")
    else:
        incomplete = sorted(key for key, value in manual.items() if value is not True)
        if incomplete:
            add(results, "requirements.manual", "manual", "manual compliance checks remain incomplete", incomplete=incomplete)
        else:
            add(results, "requirements.manual", "pass", "all declared manual checks are marked complete")


def validate_source(project: Path, main_path: Path, data: dict, results: list[dict]) -> tuple[str, list[Path]]:
    paths = tex_files(project)
    if not paths:
        add(results, "source.tex-files", "fail", "no .tex files were found")
        return "", []
    if main_path not in paths and main_path.is_file():
        paths.insert(0, main_path)
    if not main_path.is_file():
        add(results, "source.main", "fail", f"main file does not exist: {main_path}")
        return "", paths

    combined_parts = []
    for path in paths:
        try:
            text = read_tex(path)
        except (OSError, ValueError) as error:
            add(results, "source.read", "fail", str(error), file=str(path.relative_to(project)))
            continue
        combined_parts.append(text)
        balanced, offset = balanced_braces(text)
        if not balanced:
            add(results, "source.braces", "fail", "unbalanced braces", file=str(path.relative_to(project)), offset=offset)
        env_errors = environment_errors(text)
        if env_errors:
            add(results, "source.environments", "fail", "environment nesting errors", file=str(path.relative_to(project)), errors=env_errors[:20])
    combined = "\n".join(combined_parts)

    main_text = read_tex(main_path)
    if not re.search(r"\\documentclass(?:\[[^\]]*\])?\{[^{}]+\}", main_text):
        add(results, "source.documentclass", "fail", "main file has no documentclass")
    else:
        add(results, "source.documentclass", "pass", "documentclass found")
    if "\\begin{document}" not in main_text or "\\end{document}" not in main_text:
        add(results, "source.document", "fail", "main file must contain begin and end document")

    labels = LABEL_COMMAND.findall(combined)
    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})
    if duplicate_labels:
        add(results, "source.duplicate-labels", "fail", "duplicate labels found", labels=duplicate_labels)
    refs = {item.strip() for group in REF_COMMAND.findall(combined) for item in group.split(",") if item.strip()}
    undefined_refs = sorted(refs - set(labels))
    if undefined_refs:
        add(results, "source.undefined-references", "fail", "references have no matching label", labels=undefined_refs)
    else:
        add(results, "source.references", "pass", "no statically undefined references found")

    bib_paths = discover_bibliographies(project, combined)
    missing_bib = [str(path) for path in bib_paths if not path.is_file()]
    if missing_bib:
        add(results, "source.bibliography-files", "fail", "bibliography files are missing", files=missing_bib)
    bib_keys, duplicate_bib = bibliography_keys(bib_paths)
    if duplicate_bib:
        add(results, "source.duplicate-bibkeys", "fail", "duplicate bibliography keys found", keys=duplicate_bib)
    citations = {
        key.strip()
        for group in CITE_COMMAND.findall(combined)
        for key in group.split(",")
        if key.strip() and key.strip() != "*"
    }
    undefined_citations = sorted(citations - bib_keys)
    if undefined_citations:
        add(results, "source.undefined-citations", "fail", "citation keys are absent from the bibliography", keys=undefined_citations)
    elif citations:
        add(results, "source.citations", "pass", "all statically detected citation keys exist in a bibliography")
    else:
        add(results, "source.citations", "info", "no citation commands were detected")

    constraints = data.get("constraints") if isinstance(data.get("constraints"), dict) else {}
    required_sections = constraints.get("required_sections") or []
    headings = {normalize_heading(value) for value in SECTION_COMMAND.findall(combined)}
    missing_sections = [section for section in required_sections if normalize_heading(str(section)) not in headings]
    if missing_sections:
        add(results, "source.required-sections", "fail", "required sections are missing", sections=missing_sections)
    elif required_sections:
        add(results, "source.required-sections", "pass", "recorded required sections were found")

    packages = {item.strip() for group in PACKAGE_COMMAND.findall(combined) for item in group.split(",") if item.strip()}
    forbidden = sorted(packages & set(constraints.get("forbidden_packages") or []))
    if forbidden:
        add(results, "source.forbidden-packages", "fail", "forbidden packages are used", packages=forbidden)

    required_files = constraints.get("required_files") or []
    missing_required = [value for value in required_files if not (project / str(value)).is_file()]
    if missing_required:
        add(results, "source.required-files", "fail", "required submission files are missing", files=missing_required)

    placeholders = len(PLACEHOLDER.findall(combined))
    if placeholders:
        add(results, "source.placeholders", "manual", "submission source contains unresolved placeholder markers", count=placeholders)

    if constraints.get("anonymity_required"):
        author_blocks = re.findall(r"\\author(?:\[[^\]]*\])?\{([^{}]*)\}", combined, flags=re.S)
        exposed_authors = [value.strip() for value in author_blocks if value.strip() and not re.search(r"anonymous|blind", value, re.I)]
        identity_hits = len(EMAIL.findall(combined)) + len(re.findall(r"\\thanks\{", combined))
        if exposed_authors or identity_hits:
            add(results, "source.anonymity", "fail", "possible identity-bearing author, email, or thanks content detected", author_blocks=len(exposed_authors), other_hits=identity_hits)
        else:
            add(results, "source.anonymity", "pass", "no obvious source-level author, email, or thanks exposure detected")

    if "\\resizebox" in combined or re.search(r"\\(?:tiny|scriptsize)\b", combined):
        add(results, "source.layout-shortcuts", "manual", "resizebox or very small type is used; inspect table and figure readability")

    if not any(row["code"] in {"source.braces", "source.environments"} for row in results):
        add(results, "source.structure", "pass", "basic brace and environment checks passed")
    return combined, bib_paths


def validate_log(log_path: Path | None, strict_layout: bool, results: list[dict]) -> None:
    if log_path is None or not log_path.is_file():
        add(results, "build.log", "manual", "build log was not supplied or found")
        return
    text = log_path.read_text(encoding="utf-8", errors="replace")
    counts = {
        "undefined_citations": len(re.findall(r"Citation .*? undefined|undefined citations", text, re.I)),
        "undefined_references": len(re.findall(r"Reference .*? undefined|undefined references", text, re.I)),
        "multiply_defined_labels": len(re.findall(r"multiply defined", text, re.I)),
        "overfull_hboxes": len(re.findall(r"Overfull \\hbox", text)),
        "overfull_vboxes": len(re.findall(r"Overfull \\vbox", text)),
    }
    blocking = counts["undefined_citations"] + counts["undefined_references"] + counts["multiply_defined_labels"]
    layout = counts["overfull_hboxes"] + counts["overfull_vboxes"]
    if blocking or (strict_layout and layout):
        add(results, "build.log", "fail", "build log contains blocking warnings", **counts)
    elif layout:
        add(results, "build.log", "manual", "build log contains overfull boxes requiring rendered review", **counts)
    else:
        add(results, "build.log", "pass", "no undefined references, citations, duplicate labels, or overfull boxes detected", **counts)


def validate_pdf(pdf: Path | None, data: dict, results: list[dict]) -> None:
    constraints = data.get("constraints") if isinstance(data.get("constraints"), dict) else {}
    if pdf is None:
        status = "manual" if constraints.get("pdf_required", True) else "skip"
        add(results, "pdf.file", status, "compiled PDF was not supplied")
        return
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        add(results, "pdf.file", "fail", f"PDF file does not exist or is not a .pdf: {pdf}")
        return
    info = parse_pdfinfo(pdf)
    if info is None:
        add(results, "pdf.info", "manual", "pdfinfo is unavailable or failed")
    else:
        pages = int(info["Pages"]) if info.get("Pages", "").isdigit() else None
        add(results, "pdf.info", "pass", "PDF metadata was read", total_pages=pages, page_size=info.get("Page size"))
        content_pages = constraints.get("content_pages")
        if isinstance(content_pages, int) and pages is not None and content_pages > pages:
            add(results, "pdf.page-count", "fail", "recorded content_pages exceed total PDF pages", content_pages=content_pages, total_pages=pages)
        if constraints.get("anonymity_required"):
            identity = {key: info.get(key) for key in ("Title", "Author", "Subject", "Keywords") if info.get(key)}
            author = identity.get("Author", "")
            if author and not re.search(r"anonymous|blind", author, re.I):
                add(results, "pdf.anonymity", "fail", "PDF Author metadata may expose identity", metadata=identity)
            elif identity:
                add(results, "pdf.anonymity", "manual", "review remaining PDF metadata for identity leakage", metadata=identity)
            else:
                add(results, "pdf.anonymity", "pass", "common identity metadata fields are empty")
    fonts = parse_pdffonts(pdf)
    if fonts is None:
        add(results, "pdf.fonts", "manual", "pdffonts is unavailable or failed")
    elif not fonts:
        add(results, "pdf.fonts", "manual", "no fonts were reported; inspect the PDF manually")
    else:
        unembedded = sorted({font["name"] for font in fonts if font["embedded"].lower() != "yes"})
        if unembedded:
            add(results, "pdf.fonts", "fail", "PDF contains unembedded fonts", fonts=unembedded)
        else:
            add(results, "pdf.fonts", "pass", "all fonts reported by pdffonts are embedded", count=len(fonts))


def dependency_report() -> dict:
    names = ("latexmk", "tectonic", "pdflatex", "xelatex", "lualatex", "bibtex", "biber", "pdfinfo", "pdffonts", "pdftoppm")
    return {name: shutil.which(name) for name in names}


def find_log(project: Path, main_path: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser().resolve()
    candidates = [main_path.with_suffix(".log"), project / "build" / main_path.with_suffix(".log").name]
    return next((path for path in candidates if path.is_file()), None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="LaTeX project directory")
    parser.add_argument("--main", default="main.tex", help="Main TeX path relative to project")
    parser.add_argument("--requirements", help="Venue requirements JSON")
    parser.add_argument("--pdf", help="Compiled PDF to inspect")
    parser.add_argument("--log", help="Build log to inspect")
    parser.add_argument("--report", help="Write the JSON report to this path")
    parser.add_argument("--max-source-age-days", type=int, default=180)
    parser.add_argument("--check-deps", action="store_true", help="Report local tool availability and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check_deps:
        dependencies = dependency_report()
        engines = ("latexmk", "tectonic", "pdflatex", "xelatex", "lualatex")
        available = any(dependencies[name] for name in engines)
        print(json.dumps({"dependencies": dependencies, "compile_engine_available": available}, indent=2, ensure_ascii=False))
        return 0 if available else 1
    if not args.project or not args.requirements:
        print("error: --project and --requirements are required unless --check-deps is used", file=sys.stderr)
        return 2
    if args.max_source_age_days < 1:
        print("error: --max-source-age-days must be positive", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser().resolve()
    requirements_path = Path(args.requirements).expanduser().resolve()
    if not project.is_dir():
        print(f"error: project directory not found: {project}", file=sys.stderr)
        return 2
    try:
        data = load_json(requirements_path)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    main_path = (project / args.main).resolve()
    try:
        main_path.relative_to(project)
    except ValueError:
        print("error: --main must resolve inside --project", file=sys.stderr)
        return 2

    results: list[dict] = []
    validate_requirements(data, results, args.max_source_age_days)
    try:
        validate_source(project, main_path, data, results)
    except (OSError, ValueError) as error:
        add(results, "source.scan", "fail", str(error))
    constraints = data.get("constraints") if isinstance(data.get("constraints"), dict) else {}
    validate_log(find_log(project, main_path, args.log), bool(constraints.get("strict_layout_warnings", True)), results)
    validate_pdf(Path(args.pdf).expanduser().resolve() if args.pdf else None, data, results)

    counts = {status: sum(row["status"] == status for row in results) for status in ("pass", "fail", "manual", "warn", "info", "skip")}
    if counts["fail"]:
        overall = "fail"
    elif counts["manual"]:
        overall = "partial"
    else:
        overall = "pass"
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": str(project),
        "requirements": str(requirements_path),
        "overall_status": overall,
        "counts": counts,
        "dependencies": dependency_report(),
        "results": results,
        "limitations": [
            "Static checks do not prove mathematical correctness.",
            "PDF checks do not prove margins, font sizes, line spacing, excluded page scope, hidden metadata, or portal compliance.",
            "Anonymity checks find common signals only and require human review.",
        ],
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
