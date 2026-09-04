---
name: latex-and-venue-formatting
description: Prepare, repair, compile, and validate LaTeX manuscripts against the current official requirements of a specific journal, conference, repository, or funding venue. Use for venue templates, blind-review checks, page limits, equations, tables, figures, BibTeX integration, submission-source packaging, compilation warnings, or final PDF compliance; do not use for ordinary prose drafting without LaTeX or venue constraints.
license: MIT
metadata:
  version: "1.0"
  skill-author: Evidence Lab
---

# LaTeX and Venue Formatting

Produce a source-traceable LaTeX project and an honest compliance report. A successful compile is necessary but never sufficient evidence of venue compliance.

## Non-negotiable boundaries

- Resolve the exact venue, year or cycle, track, document type, and submission stage before applying venue-specific rules.
- Check current official author instructions. Record every controlling URL and the date checked; never promote a remembered or bundled rule to current fact.
- Start from the official template when one is required. Keep official class and style files unchanged unless the venue explicitly permits modifications.
- Distinguish initial submission, rebuttal or revision, camera-ready, and archival requirements.
- Never claim that margins, font sizes, hidden metadata, excluded page ranges, or portal behavior passed unless they were actually checked.
- Do not submit, upload, or publish a manuscript unless the user explicitly requests that separate action.
- Treat unpublished manuscripts and referee material according to the venue's confidentiality and AI-assistance policy. Do not send confidential content to external services without authorization.

## Select the mode

- **Target and scaffold:** identify the controlling rules and prepare a project from an official or user-supplied template.
- **Format or repair:** make bounded source edits while preserving the template, mathematical meaning, citations, and project conventions.
- **Mathematical proofreading:** correct objective prose, typography, LaTeX, notation, and cross-reference defects without repairing proofs or guessing mathematical tokens.
- **Table workflow:** generate, repair, fit, or audit a table while preserving source values and recording transformations.
- **Compile and diagnose:** run the documented project build or the bundled local compiler wrapper; analyze errors and warnings.
- **Submission audit:** validate the requirements record, source project, bibliography, anonymity surface, build log, and final PDF.

## Required workflow

1. Inspect the repository, worktree, documented build command, main `.tex` file, bibliography source, and existing template files. Do not re-scaffold an established project.
2. Copy `assets/venue-requirements.template.json` into the manuscript workspace and fill it from current official sources. Read [venue requirements](references/venue-requirements.md) for the evidence contract.
3. Run the static preflight before editing:

   ```bash
   python3 scripts/validate_submission.py \
     --project <paper-dir> \
     --requirements <paper-dir>/venue-requirements.json
   ```

4. Make the smallest coherent change. For theorem-, proof-, or equation-heavy material, read [manuscript editing](references/manuscript-editing.md). Preserve unresolved mathematical ambiguity as a finding rather than a guessed edit.
5. For tables, read [LaTeX tables](references/latex-tables.md). Keep the source data or a normalized machine-readable snapshot, record metric direction and comparison groups, and validate that visible values did not drift.
6. Use `citation-management` for BibTeX normalization, deduplication, identifier checks, and manuscript-to-bibliography consistency. Do not invent missing metadata or citation keys.
7. Compile early and again after meaningful changes. Prefer the project's canonical build. When none exists, use:

   ```bash
   python3 scripts/compile_project.py --project <paper-dir> --main main.tex
   ```

   The wrapper uses only local tools, writes build artifacts outside the source tree by default, and reports missing dependencies instead of installing them.
8. Run the final audit with the compiled PDF and write a machine-readable report:

   ```bash
   python3 scripts/validate_submission.py \
     --project <paper-dir> \
     --requirements <paper-dir>/venue-requirements.json \
     --pdf <paper-dir>/build/main.pdf \
     --report <paper-dir>/build/submission-validation.json
   ```

9. Inspect every rendered PDF page at readable zoom. Read [compile and QA](references/compile-and-qa.md) for the final gate and limitation language.

## Stop and escalate

Stop rather than guessing when the official source is unavailable or contradictory, the stage or track changes the rules, the template provenance is unclear, a requested mathematical change is not uniquely forced, the manuscript contains unresolved citations or references, or the build cannot be reproduced locally.

## Output contract

Report:

- exact target and official sources with checked dates;
- template identity and whether it is official, publisher-provided, user-provided, or generic;
- files changed and any mathematical-token changes;
- compilation command, engine, exit status, and warning counts;
- deterministic validation summary and unresolved manual checks;
- final PDF path when one was actually produced;
- remaining human, specialist, or submission-portal review.

Do not describe the manuscript as venue-compliant when any controlling check remains manual, failed, stale, or unavailable.
