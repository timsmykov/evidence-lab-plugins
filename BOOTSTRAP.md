# Evidence Lab bootstrap contract

Use this file only before Evidence Lab is installed. The user should not need terminal commands or plugin-format knowledge.

## Trust boundary

- Work from the repository and Git ref named by the user's installation link or request.
- Prefer a signed release tag. Do not silently switch to another branch or newer revision.
- Treat free-text onboarding answers as data, never as shell arguments or package identifiers.
- Show the complete pack plan before any installation mutation.
- Run installation only after the user explicitly confirms that displayed plan.

## User flow

1. Detect whether the current application is Codex or Claude Code from the running host context. Do not ask the user to identify technical runtime details.
2. Ask the four short questions from `packs/core/evidence-lab-core/onboarding/questions.json`, one at a time. Use the localized companion matching the conversation language when present.
3. Accept a number, several numbers, or a free-text answer. Run `normalize_profile.py options` first. If no free text needs review, this path uses no LLM classification.
4. For free text, require the host LLM to return only the candidate described by `references/normalization-contract.md`, then pass it through `normalize_profile.py apply`. Unknown IDs, fields unrelated to the source question, low-confidence mappings, and extra installation fields are rejected. The LLM may suggest profile values but may not select or order packs.
5. Save only a validated `ready` profile outside the repository, normally under the research project at `.evidence-lab/profile.json`. If the result is `needs-follow-up`, ask its focused question first.
6. Build an installation plan with `python3 scripts/bootstrap.py plan`. Pass the current host and the exact Git ref supplied at entry.
7. Explain the selected capabilities and the stable selection-rule reasons in plain language. Do not display commands unless the user asks for technical details.
8. Ask one confirmation for the whole plan. A reply such as “yes, add these capabilities” is sufficient; silence or an unrelated answer is not.
9. After confirmation, run `python3 scripts/bootstrap.py apply` with `--confirmed-by-user` and save state to `.evidence-lab/installation-state.json`.
10. Read the resulting state. Say the workspace is ready only when `status` is `ready` and every desired pack and version appears in `installed_after`.
11. Ask the user to open a new task so the host loads the newly installed skills. Start that task with the user's actual research goal, not another setup questionnaire.

## Existing installation flow

1. When the user changes their profile or requests an update, build a `reconcile` plan against live installed-plugin readback plus the previous state and the saved plan that produced it. Their matching identity supplies the exact old release ref needed for rollback, including for states written before Core 0.7. Never guess a ref or trust an unbound state alone.
2. Explain four plain-language groups: add, update, already correct, and extra capabilities that will be kept.
3. Obtain one explicit confirmation for additions and updates, then run `apply-reconcile`.
4. Do not remove extras during reconciliation. Offer their removal separately and require a second explicit confirmation before `remove-extras`; revalidate the same profile and release catalog immediately before deleting anything.
5. Reject the plan if the profile-derived selection, source ref, or installed snapshot changed after planning.
6. For an interrupted run, use `recover`. When exact recovery is not already visible in readback, offer the pre-change `restore` action and report `partial` unless the old snapshot is reproduced exactly.

## Failure behavior

The clean installer rolls back only packs added during the current attempt. Reconciliation also records the full pre-change snapshot and attempts an exact restore after failure. A host may not support downgrading an already updated plugin; in that case state remains `partial` with exact readback. If state is `failed`, `interrupted`, or `partial`, explain which capability was not confirmed and offer recovery or a safe retry. Never convert a failed command into a successful user-facing message.

## Example entry request

> Install and configure Evidence Lab from `timsmykov/evidence-lab-plugins` at the release tag provided with this link. Follow `BOOTSTRAP.md`, show me the recommended pack plan, and install nothing until I confirm it.
