# Compilation and submission QA

Use this reference for build diagnosis and the final gate.

## Compile safely

Prefer the repository's documented canonical build. Otherwise use `scripts/compile_project.py`, which selects a local `latexmk`, Tectonic, or TeX engine and never installs dependencies. Keep generated `.aux`, `.log`, `.bbl`, and PDF files in a build directory rather than mixing them with authoritative source.

Compile early after choosing the template, after bibliography or package changes, and after meaningful layout changes. A missing local compiler is a blocked compile check, not evidence that source is valid.

## Log gate

Treat these as blocking until resolved or explicitly waived with venue-aware reasoning:

- compilation errors or non-zero exit status;
- undefined citations or references;
- multiply defined labels;
- missing files, fonts, or glyphs;
- overfull boxes that clip or cross the allowed column/page area;
- bibliography tool failures;
- unresolved placeholders in submission content.

Underfull boxes and benign package warnings require review, not automatic failure. Record warning counts and inspect the affected pages.

## PDF gate

Use Poppler or equivalent local tools to inspect page count, page size, embedded fonts, and common metadata. These checks do not prove margin, font-size, line-spacing, excluded-section, or hidden-object compliance.

Render every page and inspect at readable zoom for clipping, overlaps, broken equations, missing glyphs, unreadable tables, float displacement, incorrect headers/footers, blank pages, and poor figure resolution. Check grayscale and accessibility where the venue requires them.

For blind review, inspect both source and PDF surfaces: author blocks, acknowledgments, self-identifying prose, affiliations, email addresses, repository links, PDF title/author metadata, filenames, supplements, and embedded attachments. Automated matching produces candidates for human review; it cannot establish anonymity by itself.

## Page limits

Record a manually determined `content_pages` count according to the current official rule. Total PDF pages are not a substitute when references, appendices, checklists, or supplements are excluded. Never infer the content boundary from headings alone unless the venue explicitly defines that method.

## Final status language

- **PASS:** every deterministic check passed and all controlling manual checks were completed.
- **PARTIAL:** deterministic checks passed but one or more manual or environment-dependent checks remain.
- **FAIL:** at least one controlling requirement failed.
- **BLOCKED:** required source, template, compiler, PDF, or authorization was unavailable.

Do not collapse `PARTIAL` or `BLOCKED` into compliance.
