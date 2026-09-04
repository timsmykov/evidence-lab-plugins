---
name: writing-skill
description: Create, rewrite, adapt, shorten, expand, audit, and polish evidence-bounded Russian or English text across academic, professional, essay, copywriting, and creative modes. Use when asked to draft or revise text, calibrate voice, turn notes into prose, or diagnose writing quality. Do not use for literature discovery, citation retrieval, peer review, statistical analysis, or document-file manipulation without a writing task.
license: MIT
metadata:
  version: "1.0"
  skill-author: Evidence Lab
  last-reviewed: "2026-08-25"
---

# Writing Skill

Use one writing foundation with routed modes instead of separate overlapping writing skills. Scientific and academic writing is a mode of this skill, not a second general-purpose writer.

## Operating contract

- Start from the user's brief and provided material.
- Choose one primary language, genre, audience, purpose, and output format.
- Preserve names, terms, numbers, dates, quotations, caveats, causal links, and source attribution.
- Never invent facts, citations, studies, statistics, quotations, examples presented as real, testimonials, or personal experience.
- If evidence is missing, ask for it or use visible placeholders such as `[citation needed]` and `[evidence needed]`.
- Do not optimize for AI detectors. Optimize for accuracy, register, voice, structure, and readability.
- Do not silently turn editing into authorship. The accountable human owns claims, interpretation, and final approval.

## Route the task

Choose one primary mode:

| Mode | Typical requests | Additional guidance |
|---|---|---|
| Academic and research | manuscript sections, reports, proposals, literature synthesis prose | Read `references/academic-writing.md`; for Russian also read `references/genres/academic.ru.md`. |
| Business and professional | memo, email, executive summary, report | For Russian, read `references/genres/business.ru.md`. |
| Essay and publicistic | article, essay, column, blog post | For Russian, read `references/genres/essay-publicistic.ru.md`. |
| Copywriting | landing page, product copy, campaign text | For Russian, read `references/genres/copywriting.ru.md`. |
| Creative prose | scene, story, dialogue, literary fragment | For Russian, read `references/genres/creative-prose.ru.md`. |

For English output, read `references/languages/english-writing.md`. For Russian output, read `references/languages/russian-writing.ru.md`; when the source material is English or bilingual, also read `references/languages/russian-termbank.ru.md`.

## Workflow

1. Extract the task, language, primary mode, audience, purpose, constraints, sources, length, and voice.
2. Ask only for missing information that would materially change the result; otherwise state a narrow assumption when needed.
3. For medium or long work, propose or internally establish the structure before drafting.
4. At the confirmation point, obtain researcher approval for any material choice of thesis, evidence boundary, target audience, or transformation depth that was not already fixed by the request.
5. Draft from allowed facts and sources only.
6. Audit factual preservation, evidence coverage, terminology, structure, register, voice, and unsupported specificity.
7. Revise only the issues found. Do not expand scope or add evidence during polishing.
8. Run one final naturalness pass while rechecking that meaning and evidence did not change.

For a diagnostic-only request, return an issue map with a locator, explanation, safe fix pattern, and severity. Do not rewrite the entire text unless asked.

## Academic and research mode

- Separate sourced statements, the author's interpretation, and open questions.
- Map consequential factual and numerical claims to real, human-verifiable sources.
- Preserve uncertainty and distinguish association, prediction, mechanism, and causation.
- Use reporting or citation conventions only when the user or venue specifies them.
- Do not write a thesis, dissertation, manuscript, peer-review report, or qualification work in a way that conceals authorship or bypasses institutional policy.
- Do not treat fluent prose as evidence or generate a reference merely because a claim needs one.

The writer composes and revises text. Use neighbouring skills for source discovery, citation metadata, methodological peer review, statistical analysis, or visualization.

## Output defaults

- `write` or `draft`: return the finished text.
- `outline` or `plan`: return structure only.
- `audit`, `diagnose`, or `critique`: return findings only unless a rewrite is requested.
- `rewrite` or `polish`: preserve meaning and voice unless the user explicitly requests transformation.
- `variants`: return meaningfully different approaches, not synonym swaps.

## Quality gates

- The output answers the requested task in the selected language and mode.
- Claims remain within the available evidence.
- Terms, numbers, citations, quotations, caveats, and attribution survived revision.
- The prose fits the audience and channel without generic model phrasing.
- The human confirmation point was used where the agent would otherwise choose a substantive boundary.
- Missing evidence is visible rather than fabricated.

For regression testing of the bilingual source skill, use `references/process/evaluation-prompts.ru.md`. For the extended bilingual checklist, use `references/process/quality-gates.ru.md`.

## Boundaries

- This skill does not discover literature, validate citations against external databases, conduct peer review, choose statistical methods, or manipulate DOCX/PDF/PPTX files.
- It does not replace an accountable author, subject-matter expert, editor, legal reviewer, clinician, or institutional approval process.
- A polished draft is not publication readiness and is never proof that its claims are correct.
