---
name: evidence-lab-onboarding
description: Runs the fast Evidence Lab setup when a researcher asks to configure, personalize, install, or choose research capabilities; do not trigger for ordinary research questions after setup.
---

# Evidence Lab onboarding

Set up a useful research workspace through a short, non-technical chat. Ask one question at a time and accept a number, several numbers, or the researcher's own wording.

## Questions

Collect only what is still unknown:

1. Research domains or disciplines.
2. The first workflow, including a full research cycle.
3. Frequent materials and methods.
4. The current research stage.

Keep the visible language about research work. Do not mention manifests, runtimes, schemas, or terminal commands.

## Normalize

Translate the answers into the controlled fields in `profile.schema.json`: `domains`, `workflows`, `materials`, `stages`, and `methods`. Preserve a useful free-text specialization separately. Free text may improve classification, but it must never become a command or a package identifier.

If a regulated or safety-critical specialization remains ambiguous, keep the safe general classification and ask a focused follow-up only when it changes the pack plan.

## Build the plan

Save the normalized profile as JSON, then run:

```bash
python3 scripts/select_packs.py profile.json --output selection-plan.json
```

The selector is authoritative for package membership and dependencies. Do not add a pack by improvising from the conversation.

## Confirm

Explain the selected capabilities and the reason for each in plain language. Show changes before installation and let the researcher confirm using the host's normal plugin flow. After installation, verify the actual pack IDs and versions before saying the workspace is ready.

This skill creates a selection plan. It does not silently install packages, generate unreviewed skills, or claim that a host accepted an installation without readback evidence.
