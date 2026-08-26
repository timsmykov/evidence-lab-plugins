#!/usr/bin/env python3
"""Repository entrypoint for the Evidence Lab bootstrap lifecycle."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


TARGET = Path(__file__).resolve().parent.parent / "packs" / "core" / "evidence-lab-core" / "skills" / "evidence-lab-onboarding" / "scripts" / "bootstrap.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(TARGET.parent))
runpy.run_path(str(TARGET), run_name="__main__")
