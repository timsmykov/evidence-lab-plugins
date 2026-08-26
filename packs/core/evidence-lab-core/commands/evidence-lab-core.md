---
description: Route setup and universal evidence tasks through Evidence Lab Core while preserving sources, decisions, and intermediate artefacts.
argument-hint: Research question, source set, data path, draft path, or requested artefact
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill", "AskUserQuestion"]
---

# /evidence-lab-core

Use this command when a task spans the research lifecycle or when the operator is unsure which core skill should handle it.

1. Classify the requested job by its intended artefact: source set, citation library, study plan, data profile, hypothesis plan, analysis, review, figure, or written text.
2. If the workspace is not configured, run `evidence-lab-onboarding`; otherwise select the smallest sufficient Core skill.
3. Before work continues, obtain researcher confirmation for any material choice of search boundary, inclusion criteria, study design, hypothesis selection, analysis plan, or writing thesis that the request did not already settle.
4. Run deterministic scripts for repeatable transformations and retain their inputs, outputs, versions, and limitations.
5. Return the requested artefact plus a compact record of sources, researcher decisions, verification performed, and unresolved gaps.

If the task requires a domain method, clinical or regulatory judgment, laboratory control, or an unsupported external service, stop at a scoped handoff instead of improvising.
