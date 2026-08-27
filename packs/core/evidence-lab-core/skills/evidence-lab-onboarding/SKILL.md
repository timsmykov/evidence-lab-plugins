---
name: evidence-lab-onboarding
description: Runs the fast Evidence Lab setup when a researcher asks to configure, personalize, install, or choose research capabilities; do not trigger for ordinary research questions after setup.
---

# Evidence Lab onboarding

Set up a useful research workspace through a short, non-technical chat. Ask one question at a time and accept a number, several numbers, or the researcher's own wording.

## Choose the conversation language

Before any research question, show the English prompt and instruction from
`onboarding/language.json` exactly once. Render option 1 as `English` and option
2 with the native Russian label from `onboarding/language.ru.json` so either
audience can recognize it without technical wording.

Resolve the answer deterministically with `scripts/select_language.py`. Only
English and Russian are supported for now. If the answer is not recognized,
repeat only the language choice. Do not use an LLM to infer another language.
After selection, continue entirely in that language and save its `en` or `ru`
identifier as `locale` in the onboarding answers.

## Questions

Read `onboarding/questions.json` at the pack root, or its Russian companion when
`locale` is `ru`, and collect only what is still unknown:

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
python3 scripts/bootstrap.py plan profile.json --host <codex|claude-code> \
  --ref <release-tag> --release-lock release-lock.json \
  --output installation-plan.json
```

The selector is authoritative for package membership, rule evaluation, dependencies, and order. Do not add a pack by improvising from the conversation. It must include every pack marked `foundation: true`, which together expose the canonical 20-skill foundation indexed in `catalog/foundation-core.json`; profile rules may explain relevance or add optional packs but may not subtract foundation packs. Never present an entry in that index's `planned_capabilities` as installed. The resulting installation plan is deterministic for the same profile, host, source, and ref and includes the stable rule IDs that caused each selection.

For Codex, build the separate companion-plugin plan from the same normalized
profile. For Claude Code this command returns no actions by design:

```bash
python3 packs/core/evidence-lab-core/skills/evidence-lab-onboarding/scripts/select_external_plugins.py \
  profile.json --host <codex|claude-code> --output companion-plugin-plan.json
```

Do not turn a `candidate`, `explicit-opt-in`, app, or hybrid into a silent
installation. Omit explicit opt-ins unless the researcher named them. Present
`offer-connection` as a separate Codex Plugins step and verify that Codex can
use the component afterward. The reviewed registry is version-observed rather
than vendored; never copy external plugin contents into Evidence Lab state.

## Confirm

Render the locked installation plan in the conversation language:

```bash
python3 scripts/render_plan.py installation-plan.json --locale <en|ru> \
  --output .evidence-lab/recommendation.md
```

Show that rendered recommendation verbatim. It contains the complete
plain-language capability list, the stable reason for every selection, the
application, and the locked release. Do not show pack IDs, raw JSON, or commands
unless the user asks for technical details. Obtain one explicit confirmation.
Only then run:

```bash
python3 scripts/bootstrap.py apply installation-plan.json \
  --release-lock release-lock.json \
  --state .evidence-lab/installation-state.json \
  --confirmed-by-user
```

Read the state after the command. Say the workspace is ready only when its status is `ready` and every desired ID and version appears in `installed_after`. Then ask the user to start a new task so the host loads the installed skills.

The apply command already performs live host readback. When it returns a
`ready` state, do not add a redundant host-list command. If independent Codex
diagnostics are needed after a non-ready result, the supported command is
`codex plugin list --json` (singular `plugin`), never `codex plugins list`.

The installer may add or update the configured Evidence Lab marketplace and install the approved packs. On failure it rolls back only packs added during the current attempt; it never removes a pre-existing plugin. It does not silently install packages, generate unreviewed skills, or claim that a host accepted an installation without readback evidence.

## Reconfigure an existing workspace

After a profile or release changes, build a reconciliation plan against the live host readback:

```bash
python3 scripts/bootstrap.py reconcile profile.json --host <codex|claude-code> \
  --ref <release-tag> --release-lock release-lock.json \
  --previous-release-lock previous-release-lock.json \
  --previous-state .evidence-lab/installation-state.json \
  --previous-plan installation-plan.json --output reconcile-plan.json
```

Always pass the saved plan that produced the previous state. Reject the pair unless their plan IDs, marketplace identity, and previous release identity match.

For both clean installation and reconciliation, the release lock is authoritative for the stable tag, source commit, catalog hash, selected pack versions, and canonical lock digest. Never substitute a floating branch or a lock from another repository.

Explain its four groups in plain language: capabilities to add, capabilities to update, capabilities already correct, and installed Evidence Lab extras that will be kept. Obtain one confirmation before applying additions and updates:

```bash
python3 scripts/bootstrap.py apply-reconcile reconcile-plan.json \
  --profile profile.json --release-lock release-lock.json \
  --previous-release-lock previous-release-lock.json \
  --state .evidence-lab/reconcile-state.json \
  --confirmed-by-user
```

Never remove an extra during that apply. If the user also wants the listed extras removed, ask a second, separate confirmation and only then run `remove-extras` with the same `--profile profile.json`, both release locks, and `--confirmed-by-user`. Recheck the profile, release locks, release catalog, and live installation immediately before removal; any change makes the plan stale and requires a new reconciliation plan. Refuse removal when the previous lock cannot reproduce the exact extra version for a later restore.

If a run was interrupted, run `recover` with both the current and previous release locks before retrying. If state is still `interrupted` or `partial`, offer `restore` with both locks and explicit confirmation. Report a successful restore only when readback exactly matches `pre_change_snapshot`; some host/version combinations cannot downgrade an existing plugin, in which case preserve `partial` and explain the exact remaining versions.
