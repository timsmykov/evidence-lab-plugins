#!/usr/bin/env python3
"""Compile a LaTeX project with local tools and report reproducible diagnostics.

Prefer a project's canonical build command when one exists. This wrapper is a
portable fallback: it installs nothing, avoids shell execution, and writes
generated files outside the source directory by default.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TOOLS = ("latexmk", "tectonic", "pdflatex", "xelatex", "lualatex", "bibtex", "biber")


def tool_paths() -> dict[str, str | None]:
    return {name: shutil.which(name) for name in TOOLS}


def run(command: list[str], cwd: Path, env: dict[str, str]) -> dict:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "command": command,
            "returncode": 124,
            "stdout": error.stdout or "",
            "stderr": error.stderr or "compilation timed out after 600 seconds",
        }
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def choose_route(engine: str, tools: dict[str, str | None]) -> tuple[str, str] | None:
    if engine == "latexmk":
        return ("latexmk", tools["latexmk"]) if tools["latexmk"] else None
    if engine == "tectonic":
        return ("tectonic", tools["tectonic"]) if tools["tectonic"] else None
    if engine in {"pdflatex", "xelatex", "lualatex"}:
        return (engine, tools[engine]) if tools[engine] else None
    if tools["latexmk"]:
        return "latexmk", tools["latexmk"]
    if tools["tectonic"]:
        return "tectonic", tools["tectonic"]
    for name in ("pdflatex", "xelatex", "lualatex"):
        if tools[name]:
            return name, tools[name]
    return None


def latexmk_command(executable: str, engine: str, main_rel: Path, build_dir: Path) -> list[str]:
    command = [
        executable,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-outdir={build_dir}",
    ]
    if engine == "xelatex":
        command.append("-xelatex")
    elif engine == "lualatex":
        command.append("-lualatex")
    else:
        command.append("-pdf")
    command.append(str(main_rel))
    return command


def raw_engine_command(executable: str, main_rel: Path, build_dir: Path) -> list[str]:
    return [
        executable,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={build_dir}",
        str(main_rel),
    ]


def parse_log(log_path: Path) -> dict:
    if not log_path.is_file():
        return {"available": False}
    text = log_path.read_text(encoding="utf-8", errors="replace")
    page_match = re.search(r"Output written on .*?\((\d+)\s+pages?", text)
    return {
        "available": True,
        "undefined_citations": len(re.findall(r"Citation .*? undefined|undefined citations", text, re.I)),
        "undefined_references": len(re.findall(r"Reference .*? undefined|undefined references", text, re.I)),
        "multiply_defined_labels": len(re.findall(r"multiply defined", text, re.I)),
        "overfull_hboxes": len(re.findall(r"Overfull \\hbox", text)),
        "overfull_vboxes": len(re.findall(r"Overfull \\vbox", text)),
        "underfull_boxes": len(re.findall(r"Underfull \\[hv]box", text)),
        "pages": int(page_match.group(1)) if page_match else None,
    }


def compile_raw(
    executable: str,
    route: str,
    main_rel: Path,
    project: Path,
    build_dir: Path,
    env: dict[str, str],
    tools: dict[str, str | None],
) -> list[dict]:
    steps = [run(raw_engine_command(executable, main_rel, build_dir), project, env)]
    if steps[-1]["returncode"]:
        return steps

    stem = main_rel.stem
    bcf = build_dir / f"{stem}.bcf"
    aux = build_dir / f"{stem}.aux"
    if bcf.is_file() and tools["biber"]:
        steps.append(run([tools["biber"], stem], build_dir, env))
    elif aux.is_file() and re.search(r"\\(?:bibdata|citation)\b", aux.read_text(encoding="utf-8", errors="replace")):
        if tools["bibtex"]:
            steps.append(run([tools["bibtex"], stem], build_dir, env))
        else:
            steps.append(
                {
                    "command": ["bibtex", stem],
                    "returncode": 127,
                    "stdout": "",
                    "stderr": "bibliography detected but bibtex is unavailable",
                }
            )
    if any(step["returncode"] for step in steps):
        return steps

    command = raw_engine_command(executable, main_rel, build_dir)
    steps.append(run(command, project, env))
    if steps[-1]["returncode"] == 0:
        steps.append(run(command, project, env))
    return steps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="LaTeX project directory")
    parser.add_argument("--main", default="main.tex", help="Main TeX path relative to project")
    parser.add_argument(
        "--build-dir",
        help="Generated-file directory; default is a sibling named <project>-latex-build",
    )
    parser.add_argument(
        "--engine",
        choices=["auto", "latexmk", "tectonic", "pdflatex", "xelatex", "lualatex"],
        default="auto",
    )
    parser.add_argument(
        "--latexmk-engine",
        choices=["pdflatex", "xelatex", "lualatex"],
        default="pdflatex",
        help="Engine used by latexmk in auto or latexmk mode",
    )
    parser.add_argument("--report", help="Write JSON report to this path")
    parser.add_argument("--check-deps", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tools = tool_paths()
    if args.check_deps:
        engines = ("latexmk", "tectonic", "pdflatex", "xelatex", "lualatex")
        available = any(tools[name] for name in engines)
        print(json.dumps({"dependencies": tools, "compile_engine_available": available}, indent=2, ensure_ascii=False))
        return 0 if available else 1
    if not args.project:
        print("error: --project is required unless --check-deps is used", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"error: project directory not found: {project}", file=sys.stderr)
        return 2
    main_path = (project / args.main).resolve()
    try:
        main_rel = main_path.relative_to(project)
    except ValueError:
        print("error: --main must resolve inside --project", file=sys.stderr)
        return 2
    if not main_path.is_file():
        print(f"error: main TeX file not found: {main_path}", file=sys.stderr)
        return 2

    build_dir = (
        Path(args.build_dir).expanduser().resolve()
        if args.build_dir
        else project.parent / f"{project.name}-latex-build"
    )
    if build_dir == project or project in build_dir.parents:
        print("error: build directory must be outside the source project", file=sys.stderr)
        return 2
    build_dir.mkdir(parents=True, exist_ok=True)

    route = choose_route(args.engine, tools)
    if route is None:
        report = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "blocked",
            "reason": f"requested engine is unavailable: {args.engine}",
            "dependencies": tools,
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1
    route_name, executable = route

    env = os.environ.copy()
    separator = os.pathsep
    env["TEXINPUTS"] = f"{project}{os.sep}{os.sep}{separator}{env.get('TEXINPUTS', '')}"
    env["BIBINPUTS"] = f"{project}{os.sep}{os.sep}{separator}{env.get('BIBINPUTS', '')}"
    env["BSTINPUTS"] = f"{project}{os.sep}{os.sep}{separator}{env.get('BSTINPUTS', '')}"

    if route_name == "latexmk":
        steps = [run(latexmk_command(executable, args.latexmk_engine, main_rel, build_dir), project, env)]
    elif route_name == "tectonic":
        steps = [run([executable, "--keep-logs", "--keep-intermediates", "--outdir", str(build_dir), str(main_rel)], project, env)]
    else:
        steps = compile_raw(executable, route_name, main_rel, project, build_dir, env, tools)

    transcript = []
    for index, step in enumerate(steps, 1):
        transcript.extend(
            [
                f"STEP {index}: {' '.join(step['command'])}",
                f"RETURN CODE: {step['returncode']}",
                "STDOUT:",
                step["stdout"],
                "STDERR:",
                step["stderr"],
                "",
            ]
        )
    transcript_path = build_dir / "evidence-lab-compile.log"
    transcript_path.write_text("\n".join(transcript), encoding="utf-8")

    engine_log = build_dir / f"{main_rel.stem}.log"
    pdf_path = build_dir / f"{main_rel.stem}.pdf"
    successful = bool(steps) and all(step["returncode"] == 0 for step in steps) and pdf_path.is_file()
    log_summary = parse_log(engine_log)
    blocking_warnings = sum(
        int(log_summary.get(key, 0) or 0)
        for key in ("undefined_citations", "undefined_references", "multiply_defined_labels")
    )
    status = "pass" if successful and not blocking_warnings else "fail"
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "project": str(project),
        "main": str(main_rel),
        "build_dir": str(build_dir),
        "route": route_name,
        "executable": executable,
        "dependencies": tools,
        "steps": [{"command": step["command"], "returncode": step["returncode"]} for step in steps],
        "log_summary": log_summary,
        "pdf": str(pdf_path) if pdf_path.is_file() else None,
        "transcript": str(transcript_path),
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
