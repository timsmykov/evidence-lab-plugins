---
description: Route a research task to the smallest relevant set of research-core skills and preserve evidence, decisions, and intermediate artefacts.
argument-hint: Research question, source set, data path, draft path, or requested artefact
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill", "AskUserQuestion"]
---

# /research-core

Use this command when a task spans the research lifecycle or when the operator is unsure which core skill should handle it.

1. Classify the requested job by its intended artefact: source set, citation library, study plan, data profile, hypothesis plan, analysis, review, figure, or written text.
2. Select the smallest sufficient set of `research-core` skills. Do not load the entire plugin into context.
3. Before work continues, obtain researcher confirmation for any material choice of search boundary, inclusion criteria, study design, hypothesis selection, analysis plan, or writing thesis that the request did not already settle.
4. Run deterministic scripts for repeatable transformations and retain their inputs, outputs, versions, and limitations.
5. Return the requested artefact plus a compact record of sources, researcher decisions, verification performed, and unresolved gaps.

If the task requires a domain method, clinical or regulatory judgment, laboratory control, or an unsupported external service, stop at a scoped handoff instead of improvising.
