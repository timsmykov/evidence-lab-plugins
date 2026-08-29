---
name: evidence-lab-onboarding
description: Runs the fast Evidence Lab setup when a researcher asks to configure, personalize, install, or choose research capabilities; do not trigger for ordinary research questions after setup.
---

# Evidence Lab onboarding

Set up a useful research workspace through a short, non-technical chat. Ask one question at a time and accept a number, several numbers, or the researcher's own wording.

## Use the stateful driver

Use only `scripts/onboarding_driver.py` for first-run onboarding. Start one
saved session with the detected host, verified release tag, and release lock.
For every subsequent turn, follow its `next_action` and show only
`user_message`. Never expose its JSON envelope, diagnostic code, command, path,
or stack trace.

The driver owns language selection, the four questions, numeric answer parsing,
normalization state, deterministic pack selection, plan rendering,
confirmation, installation, readback, and timing. It always asks for English or
Russian before collecting research details. An unsupported language repeats
only the language choice.

## Questions

The driver renders one reviewed question per turn. Never invent another
profile quiz. It collects only:

1. Research domains or disciplines.
2. The first workflow, including a full research cycle.
3. Frequent materials and methods.
4. The current research stage.

Keep the visible language about research work. Do not mention manifests, runtimes, schemas, or terminal commands.

## Normalize

The driver saves answers in the reviewed schema and runs deterministic option
normalization first. If `next_action` is `submit-normalization-candidate`, read
`references/normalization-contract.md`, produce only a
`normalization-candidate.schema.json` object, and submit it through the same
driver.

Proceed only when the validated result is `ready`. If it is `needs-follow-up`, ask its single plain-language question and normalize the new answer through the same boundary. Preserve useful free text as specialization context. It must never become a command or a package identifier.

Read `onboarding/selection-policy.json` before normalizing free text. It is the
only allowed vocabulary. Treat your classification as an untrusted suggestion:
never invent an ID, never silently use a low-confidence mapping, and retain an
unknown useful phrase only as specialization context. Pack selection rules live
in reviewed `pack.json` files and are evaluated by the selector, not by the LLM.

If a regulated or safety-critical specialization remains ambiguous, keep the safe general classification and ask the validated focused follow-up only when it changes the pack plan.

## Build the plan

Before installation, work from the checked-out, pinned Evidence Lab release.
The driver invokes the authoritative selector and locked renderer itself. Only
`evidence-lab-core` is mandatory for everyone; the remaining packs that contain
the 20-skill research library are conditional. Never add a pack by improvising
from the conversation or present a planned capability as installed.

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

Show the driver's locked recommendation verbatim. It contains the complete
plain-language capability list, the stable reason for every selection, the
application, and the locked release. Do not show pack IDs, raw JSON, or commands
unless the user asks for technical details. Do not request confirmation unless
the rendered file starts with the locale's canonical recommendation heading; a
raw ID/version list is not an acceptable substitute. Obtain
one explicit confirmation. Submit it through the driver. Only an explicit yes
moves the session to `apply`. Say the workspace is ready only when the driver
returns stage `ready`; this requires exact host readback.

## Verify the installed profile

In the new task requested by the completion message, run the profile-aware
post-install probe runner against the saved plan and installed pack roots.
Every conditional pack has an observable probe and Core has three different
capability probes. Report success only when the runner returns `status: pass`.
A missing skill, manifest entry, or executable probe must fail closed.

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
