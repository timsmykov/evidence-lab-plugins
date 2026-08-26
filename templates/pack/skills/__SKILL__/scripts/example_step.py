#!/usr/bin/env python3
"""REPLACE ME: the deterministic part of __SKILL__.

Anything that must give the same answer on a rerun lives here, not in the
prompt: deduplication, table rendering, citation formatting, template filling.
Keep it dependency-light and runnable standalone — the skill calls it, and a
human can call it too when checking the result.
"""
from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="path to the intermediate artefact")
    ap.add_argument("--out", default="-", help="output path, '-' for stdout")
    args = ap.parse_args()

    # REPLACE ME with the real transformation.
    result = {"input": args.input, "status": "not implemented"}

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out == "-":
        print(rendered)
    else:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
