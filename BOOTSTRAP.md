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
3. Accept a number, several numbers, or a free-text answer. Normalize only to IDs declared by the question catalog. Preserve a useful specialization as text.
4. Save the normalized profile outside the repository, normally under the research project at `.evidence-lab/profile.json`.
5. Build an installation plan with `python3 scripts/bootstrap.py plan`. Pass the current host and the exact Git ref supplied at entry.
6. Explain the selected capabilities and reasons in plain language. Do not display commands unless the user asks for technical details.
7. Ask one confirmation for the whole plan. A reply such as “yes, add these capabilities” is sufficient; silence or an unrelated answer is not.
8. After confirmation, run `python3 scripts/bootstrap.py apply` with `--confirmed-by-user` and save state to `.evidence-lab/installation-state.json`.
9. Read the resulting state. Say the workspace is ready only when `status` is `ready` and every desired pack and version appears in `installed_after`.
10. Ask the user to open a new task so the host loads the newly installed skills. Start that task with the user's actual research goal, not another setup questionnaire.

## Failure behavior

The installer rolls back only packs added during the current attempt. It never removes a pre-existing plugin. If state is `failed` or `partial`, explain which capability was not confirmed and offer a safe retry. Never convert a failed command into a successful user-facing message.

## Example entry request

> Install and configure Evidence Lab from `timsmykov/evidence-lab-plugins` at the release tag provided with this link. Follow `BOOTSTRAP.md`, show me the recommended pack plan, and install nothing until I confirm it.
