---
name: evidence-lab-onboarding
description: Runs the fast Evidence Lab setup when a researcher asks to configure, personalize, install, or choose research capabilities; do not trigger for ordinary research questions after setup.
---

# Evidence Lab onboarding

Set up a useful research workspace through a short, non-technical chat. Ask one question at a time and accept a number, several numbers, or the researcher's own wording.

## Questions

Read `onboarding/questions.json` at the pack root and collect only what is still unknown:

1. Research domains or disciplines.
2. The first workflow, including a full research cycle.
3. Frequent materials and methods.
4. The current research stage.

Keep the visible language about research work. Do not mention manifests, runtimes, schemas, or terminal commands.

## Normalize

Save the answers in the shape defined by `onboarding-answers.schema.json`. First run the deterministic option path:

```bash
python3 skills/evidence-lab-onboarding/scripts/normalize_profile.py options onboarding-answers.json --output profile-result.json
```

If the result is `ready`, use its profile without an LLM classification step. If it is `needs-review`, read `references/normalization-contract.md`, produce only a `normalization-candidate.schema.json` object, and validate it:

```bash
python3 skills/evidence-lab-onboarding/scripts/normalize_profile.py apply onboarding-answers.json normalization-candidate.json --output profile-result.json
```

Proceed only when the validated result is `ready`. If it is `needs-follow-up`, ask its single plain-language question and normalize the new answer through the same boundary. Preserve useful free text as specialization context. It must never become a command or a package identifier.

Read `onboarding/selection-policy.json` before normalizing free text. It is the
only allowed vocabulary. Treat your classification as an untrusted suggestion:
never invent an ID, never silently use a low-confidence mapping, and retain an
unknown useful phrase only as specialization context. Pack selection rules live
in reviewed `pack.json` files and are evaluated by the selector, not by the LLM.

If a regulated or safety-critical specialization remains ambiguous, keep the safe general classification and ask the validated focused follow-up only when it changes the pack plan.

## Build the plan

Before installation, work from the checked-out, pinned Evidence Lab repository and save the normalized profile outside that checkout. Then run:

```bash
python3 scripts/bootstrap.py plan profile.json --host <codex|claude-code> --ref <release-tag> --output installation-plan.json
```

The selector is authoritative for package membership, rule evaluation, dependencies, and order. Do not add a pack by improvising from the conversation. The resulting installation plan is deterministic for the same profile, host, source, and ref and includes the stable rule IDs that caused each selection.

## Confirm

Explain the selected capabilities and the reason for each in plain language. Show the complete plan and obtain one explicit confirmation. Only then run:

```bash
python3 scripts/bootstrap.py apply installation-plan.json \
  --state .evidence-lab/installation-state.json \
  --confirmed-by-user
```

Read the state after the command. Say the workspace is ready only when its status is `ready` and every desired ID and version appears in `installed_after`. Then ask the user to start a new task so the host loads the installed skills.

The installer may add or update the configured Evidence Lab marketplace and install the approved packs. On failure it rolls back only packs added during the current attempt; it never removes a pre-existing plugin. It does not silently install packages, generate unreviewed skills, or claim that a host accepted an installation without readback evidence.
