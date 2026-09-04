#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SKILL = Path(__file__).resolve().parent.parent
VALIDATOR = SKILL / "scripts" / "validate_submission.py"
COMPILER = SKILL / "scripts" / "compile_project.py"


def requirements(anonymity: bool = False) -> dict:
    return {
        "schema_version": 1,
        "target": {
            "venue": "Example Conference",
            "year_or_cycle": "2026",
            "track": "main",
            "document_type": "full paper",
            "stage": "initial-submission",
            "authoring_format": "latex",
        },
        "official_sources": [
            {
                "title": "Author instructions",
                "url": "https://example.org/authors",
                "checked_at": date.today().isoformat(),
                "supports": ["template", "anonymity"],
            }
        ],
        "template": {
            "status": "user-provided",
            "source_url": "",
            "version_or_checksum": "fixture",
            "license_or_terms_checked": True,
            "modified": False,
        },
        "constraints": {
            "max_content_pages": None,
            "content_pages": None,
            "anonymity_required": anonymity,
            "strict_layout_warnings": True,
            "required_sections": ["Introduction"],
            "forbidden_packages": ["fullpage"],
            "required_files": ["main.tex", "refs.bib"],
            "bibliography_system": "bibtex",
            "source_package_required": False,
            "pdf_required": False,
        },
        "manual_checks": {
            "page_scope_confirmed": True,
            "template_integrity_confirmed": True,
            "anonymity_reviewed": True,
            "all_pdf_pages_inspected": True,
            "submission_portal_previewed": True,
        },
        "notes": [],
    }


class ScriptTests(unittest.TestCase):
    def make_project(self, root: Path, cite_key: str = "known", author: str = "Anonymous Authors") -> None:
        (root / "main.tex").write_text(
            "\\documentclass{article}\n"
            f"\\author{{{author}}}\n"
            "\\begin{document}\n"
            "\\section{Introduction}\n"
            f"Evidence~\\cite{{{cite_key}}}.\\label{{sec:intro}}\n"
            "See Section~\\ref{sec:intro}.\n"
            "\\bibliography{refs}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        (root / "refs.bib").write_text(
            "@article{known, title={Known}, author={Author, A}, year={2026}}\n",
            encoding="utf-8",
        )

    def run_validator(self, root: Path, data: dict) -> subprocess.CompletedProcess[str]:
        req = root / "venue-requirements.json"
        req.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--project", str(root), "--requirements", str(req)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_static_project_has_no_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root)
            result = self.run_validator(root, requirements())
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["counts"]["fail"], 0)
            self.assertIn(report["overall_status"], {"pass", "partial"})

    def test_undefined_citation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root, cite_key="missing")
            result = self.run_validator(root, requirements())
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            codes = {row["code"] for row in report["results"] if row["status"] == "fail"}
            self.assertIn("source.undefined-citations", codes)

    def test_blind_source_identity_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root, author="Named Researcher")
            result = self.run_validator(root, requirements(anonymity=True))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            codes = {row["code"] for row in report["results"] if row["status"] == "fail"}
            self.assertIn("source.anonymity", codes)

    def test_dependency_probes_are_machine_readable(self) -> None:
        for script in (VALIDATOR, COMPILER):
            result = subprocess.run(
                [sys.executable, str(script), "--check-deps"],
                text=True,
                capture_output=True,
                check=False,
            )
            report = json.loads(result.stdout)
            self.assertIn("dependencies", report)
            self.assertEqual(result.returncode == 0, report["compile_engine_available"])


if __name__ == "__main__":
    unittest.main()
