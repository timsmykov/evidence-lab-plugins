# Immutable Codex onboarding experiment protocol

This protocol governs the reusable harness for a local ten-scenario Evidence Lab onboarding experiment. It does not contain results from a real cohort.

## Purpose

The harness tests one immutable Evidence Lab candidate on five English and five Russian synthetic researcher profiles. It preserves enough local evidence to distinguish product defects, safety violations, harness defects, invalid infrastructure attempts, and rejected artifacts.

The primary output is a reviewed local evidence bundle. A later product report may summarize observed problems and improvement opportunities, but technical run artifacts never enter Git, GitHub Releases, Actions artifacts, or pull-request attachments.

## Candidate boundary

The candidate identity binds all inputs that can change the observation:

- product commit, release tag, release lock, and pack catalog;
- harness commit and schema bundle;
- the exact ten-scenario bundle;
- Codex version, model, reasoning effort, isolation adapter, and timeout policy.

Changing any bound input creates a new candidate and cohort. A product failure cannot be repaired and replaced inside the same cohort.

`prepare` resolves the Codex version from the executable, verifies the release
lock inside a clean checkout of the tagged commit, checks the catalog digest,
and runs a Terra medium capability probe inside Bubblewrap. The manifest is
written only after these checks pass. Versions, commits, catalogs, and
preflight results cannot be supplied as operator assertions.

## Cohort rules

- Run exactly ten valid primary scenarios: five English and five Russian.
- Use five regression scenarios and five previously unexecuted holdouts.
- Continue the remaining scenarios after an ordinary product failure.
- Stop the cohort immediately after a safety failure.
- Preserve every attempt. An infrastructure-invalid attempt may be superseded only by another attempt with byte-identical candidate inputs.
- A harness, matcher, schema, fixture, timeout, isolation, or product change starts a new cohort.

## Evidence boundary

Real artifacts live under `${XDG_STATE_HOME:-~/.local/state}/evidence-lab/experiments` or an explicit `--artifact-root` outside every Git worktree. Cohort directories use mode `0700`; files use `0600`.

Receipts contain hashes, normalized outcomes, selected pack IDs and versions, checks, and durations. They exclude credentials, tokens, session IDs, raw environment dumps, account identifiers, and absolute private paths. Runtime material required to resume a Codex thread remains protected and is not part of the reviewable receipt or product report.

For a completed run, `finish-run` derives every pass check from the verified
event chain. It derives hashes from the fixed plan, installation-state,
new-task-probe, and journal paths, then derives pack IDs and versions from host
readback. The CLI does not accept separate checks, hashes, or selected-pack
files. `status`, `validate`, `summarize`, and `seal` recompute these bindings
before they can report a passing gate.

`capture-artifacts` copies only
`.evidence-lab/installation-plan.json` and
`.evidence-lab/installation-state.json` from the isolated run workspace. It
does not accept alternate source paths.

## Observable new-task check

After installation, a new Codex task runs without access to the source or release checkout. It must invoke the installed `citation-management/scripts/format_bibtex.py` with `--rekey --deduplicate --sort key` on the bundled synthetic fixture.

The check passes only when a `command_execution` event resolves to the run-specific installed plugin cache and stdout matches the frozen expected SHA-256. A model statement that it used the skill is not evidence.

The probe reads its JSONL stream from the run-specific runtime directory and
uses the frozen BibTeX input and expected output bound into `candidate_id`. It
also uses a frozen prompt and turn label. It does not accept an
operator-selected plugin root, prompt, or output file.

## Outcomes

- `COMPLETED`: all product and evidence checks passed.
- `PRODUCT_FAIL`: Evidence Lab violated a user-flow or installation contract under healthy infrastructure.
- `SAFETY_FAIL`: installation began before confirmation or an unauthorized external connection was attempted.
- `HARNESS_FAIL`: runner, parser, matcher, or assertion logic failed.
- `INFRA_INVALID`: authentication, provider, model, disk, or host conditions prevented a valid observation.
- `ARTIFACT_REJECTED`: evidence is incomplete, unsafe, or fails schema, path, permission, or hash validation.
- `OPERATOR_ABORTED`: a human stopped the run and recorded a reason.

## Human review

Tim reviews the sealed manifest, all ten primary receipts, every abnormal or superseded attempt, complete sanitized artifacts for at least one Russian and one English run, the artifact index, repository gate evidence, and the final claim wording. Acceptance is stored locally in a `review.json` bound to the candidate and artifact-index hashes.

## Product distillation

After review, a separate product-facing report records only:

- the observed problem;
- how many valid scenarios showed it;
- the user-visible impact;
- the evidence-backed or explicitly inferred cause;
- the improvement opportunity;
- confidence and known limits.

Synthetic simulations do not prove real-researcher usability or production readiness.

## Execution phases

### Phase 1 — Freeze the candidate

Validate the ten profiles, pin the published product release, release lock,
catalog, harness revision, schemas, Codex version, Terra medium, isolation
adapter, and timeouts. Hash these inputs into one candidate ID. Any change after
this point creates a different cohort.

Exit condition: a local `manifest.json` exists and its identity recomputes
without drift.

### Phase 2 — Calibrate the harness

Use a fake host to exercise successful installation, product failure, safety
failure, infrastructure invalidation, malformed event streams, timeouts,
resume, and artifact rejection. Then run one disposable live calibration that
is not counted in the cohort. Calibration may improve the harness, but every
improvement requires returning to Phase 1 and freezing a new candidate.

Exit condition: deterministic tests pass and the live adapter can start and
resume a task without exposing the operator's home or repository checkout.

The sandbox mounts only the system binaries and the small `/etc` allowlist
needed for name resolution and TLS. It mounts the pinned Codex executable and
its sibling `codex-code-mode-host`; the live preflight must execute a command
through that host before a candidate can be prepared. Host password files, SSH
host keys, the operator home, and unrelated repository paths are absent.

### Phase 3 — Execute ten primary simulations

For each frozen profile, create a fresh Bubblewrap workspace and Codex home.
Expose the verified release read-only during onboarding. Start one Codex task,
answer the language choice and four questions exactly as the scenario defines,
capture the complete recommendation, verify that no install mutation occurred,
confirm once, and verify the resulting host readback.

Record every transition in the append-only journal. Continue after a product
failure. Stop the cohort immediately after a safety failure. Only an
infrastructure-invalid attempt may be superseded.

The runner enforces the frozen scenario order and permits only one unfinished
attempt. `resume` reports `START`, `RESUME`, `FINISH`, `RETRY`, or `DONE` for
each scenario without rewriting its journal. A safety terminal event stops the
next run even if interruption occurred before its receipt was written.

Exit condition: either ten valid primary receipts exist or the safety-stop rule
has fired.

### Phase 4 — Verify a genuinely new task

Open a separate Codex task in the installed environment. Do not expose the
release or source checkout. Ask it to perform the frozen BibTeX operation. Pass
only if observable command execution resolves to the installed plugin cache and
the result matches the expected fixture hash.

Exit condition: the receipt contains a successful installed-path probe, not a
model assertion.

### Phase 5 — Seal and classify

Validate journals, receipts, schemas, permissions, hashes, supersession links,
and secret/path exclusions. Build a deterministic summary and artifact index.
Keep resumable runtime state outside the reviewable index.

Exit condition: the local cohort is immutable and has no unresolved automatic
classifications, or each unresolved item has a bound adjudication record.

### Phase 6 — Independent review

Tim reviews the manifest, all primary receipts, every abnormal attempt, full
sanitized examples for at least one Russian and one English flow, repository
gate evidence, and the scope of the proposed claims. The review is bound to the
candidate and artifact-index hashes.

Exit condition: a signed-off local review records acceptance, rejection, or
explicit reservations.

### Phase 7 — Distill product improvements

Convert observations into product findings. Combine repeated symptoms only
when their user-visible behavior and evidence support the same problem. Keep
observed facts separate from inferred causes. Rank opportunities by frequency,
impact, confidence, and the cost of leaving the problem unresolved.

Only the product problem statement and improvement decision may later become a
repository issue or task. Raw prompts, transcripts, commands, paths, timings,
receipts, and other technical experiment artifacts stay local.
