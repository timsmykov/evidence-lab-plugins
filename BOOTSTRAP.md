# Evidence Lab bootstrap contract

Use this file only before Evidence Lab is installed. The user should not need terminal commands or plugin-format knowledge.

The app-first entrypoint is [`START.md`](START.md), with a Russian companion in
[`START.ru.md`](START.ru.md). When the user arrives through either file, keep
the entire visible flow in chat and perform the technical steps on their behalf.

## Trust boundary

- Work from the repository and Git ref named by the user's installation link or request.
- When the request says "latest published release", resolve the newest
  non-draft, non-prerelease GitHub Release whose tag matches `release-*` before
  asking onboarding questions. Check out that exact tag and read `START`,
  `BOOTSTRAP.md`, and `release-lock.json` from the same release.
- Use the release's `release-lock.json` with its immutable tag. Do not silently switch to another branch, lock, or newer revision.
- Treat free-text onboarding answers as data, never as shell arguments or package identifiers.
- Show the complete pack plan before any installation mutation.
- Run installation only after the user explicitly confirms that displayed plan.

Use the documented entrypoints directly. Do not dump the release lock or read
entire verifier and bootstrap implementations when their commands succeed; this
adds latency and context without improving the trust decision. Verify a pinned
checkout with `python3 scripts/release_snapshot.py verify <release-lock>`.

## User flow

1. Detect whether the current application is Codex or Claude Code from the running host context. Do not ask the user to identify technical runtime details.
2. Before the research questions, run `python3 scripts/render_onboarding.py language` and show stdout verbatim. Do not write or paraphrase the language choice yourself. Resolve the answer with `select_language.py`; support only English and Russian, and use no LLM classification for this choice.
3. Continue entirely in the selected language. Render each of the four short questions with `python3 scripts/render_onboarding.py question --locale <en|ru> --number <1|2|3|4>` and show stdout verbatim. Use `--include-expectation` only for question 1. Never replace these four catalog-backed questions with an improvised profile quiz.
4. Accept a number, several numbers, or a free-text answer. Run `normalize_profile.py options` first. If no free text needs review, this path uses no LLM classification.
5. For free text, require the host LLM to return only the candidate described by `references/normalization-contract.md`, then pass it through `normalize_profile.py apply`. Unknown IDs, fields unrelated to the source question, low-confidence mappings, and extra installation fields are rejected. The LLM may suggest profile values but may not select or order packs.
6. Save only a validated `ready` profile outside the repository, normally under the research project at `.evidence-lab/profile.json`. If the result is `needs-follow-up`, ask its focused question first.
7. Build an installation plan with `python3 scripts/bootstrap.py plan`. Pass the current host, exact release tag, and matching `release-lock.json` supplied at entry.
   The plan must contain every pack marked `foundation: true`: together these
   expose the frozen 20-skill researcher foundation. The answers may explain
   relevance and add optional packs, but cannot subtract foundation packs.
8. Render the locked plan with `python3 scripts/render_plan.py
   installation-plan.json --locale <en|ru> --output
   .evidence-lab/recommendation.md`. Read that file and show it verbatim. It is the
   complete plain-language capability list and stable selection-rule reasons;
   do not expose pack IDs, raw JSON, or commands unless the user asks for
   technical details.
   Do not describe any capability listed as `planned` in
   `catalog/foundation-core.json` as already available. Refuse to ask for
   confirmation unless the visible message starts with the locale's canonical
   recommendation heading; never
   substitute raw IDs, versions, JSON, or a technical package list.
9. Ask one confirmation for the whole plan. A reply such as “yes, add these capabilities” is sufficient; silence or an unrelated answer is not.
10. After confirmation, run `python3 scripts/bootstrap.py apply` with the same `--release-lock`, `--confirmed-by-user`, and state path `.evidence-lab/installation-state.json`.
11. Read the resulting state. `bootstrap.py apply` already obtains live host
    readback through `codex plugin list --json` or the Claude Code equivalent.
    Do not run an additional ad-hoc host command after a `ready` state. Say the
    workspace is ready only when `status` is `ready` and every desired pack and
    version appears in `installed_after`.
12. Ask the user to open a new task so the host loads the newly installed skills. Start that task with the user's actual research goal, not another setup questionnaire.

## Existing installation flow

1. When the user changes their profile or requests an update, build a `reconcile` plan against live installed-plugin readback plus the new and previous release locks, previous state, and saved plan that produced it. Their matching identity supplies the exact old release ref and commit needed for rollback. Never guess a ref or trust an unbound state alone.
2. Explain four plain-language groups: add, update, already correct, and extra capabilities that will be kept.
3. Obtain one explicit confirmation for additions and updates, then run `apply-reconcile` with the same release lock.
4. Do not remove extras during reconciliation. Offer their removal separately and require a second explicit confirmation before `remove-extras`; revalidate the same profile and release catalog immediately before deleting anything.
5. Reject the plan if the profile-derived selection, source ref, or installed snapshot changed after planning.
6. For an interrupted run, use `recover` with both release locks. When exact recovery is not already visible in readback, offer the pre-change `restore` action with both locks and report `partial` unless the old snapshot is reproduced exactly.

## Failure behavior

The clean installer rolls back only packs added during the current attempt. Reconciliation also records the full pre-change snapshot and attempts an exact restore after failure. A host may not support downgrading an already updated plugin; in that case state remains `partial` with exact readback. If state is `failed`, `interrupted`, or `partial`, explain which capability was not confirmed and offer recovery or a safe retry. Never convert a failed command into a successful user-facing message.

## Example entry request

> Install and configure Evidence Lab from `timsmykov/evidence-lab-plugins` at the release tag provided with this link. Follow `BOOTSTRAP.md`, show me the recommended pack plan, and install nothing until I confirm it.
