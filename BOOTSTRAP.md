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
2. Start one `.evidence-lab/onboarding-session.json` through
   `python3 scripts/onboarding_driver.py start` with the detected host, exact
   release tag, catalog, and matching release lock.
3. On every turn, call the same driver action named by `next_action` and show
   only `user_message`. Never show its JSON envelope, paths, commands, or
   diagnostic codes.
4. The driver asks for language first, then exactly four reviewed questions one
   at a time. It parses numeric choices without an LLM. Free text may be mapped
   only through a schema-valid normalization candidate; it cannot choose packs.
5. The driver builds one locked plan containing the mandatory Core plus only
   the conditional packs selected by reviewed rules from the 20-skill library.
6. Show the complete recommendation verbatim and obtain one confirmation. Only
   an explicit yes moves the saved state to `confirmed`; no other action may
   install anything.
7. Run the driver's `apply` action. It performs installation and exact host
   readback. Say the workspace is ready only when the returned stage is
   `ready`. Each completed step records status and duration; the response
   includes p50, p95, and total elapsed command time.
8. Ask the user to open a new task. In that task, run
   `scripts/run_post_install_probes.py` against the saved plan and installed
   roots. Every selected conditional pack and three Core capabilities must
   pass before reporting profile verification.

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
