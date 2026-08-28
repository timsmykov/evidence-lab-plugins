# Codex onboarding acceptance: 20 Terra scenarios

Date: 2026-08-28

Host: Codex CLI in a Bubblewrap-isolated Linux workspace

Model: `gpt-5.6-terra`, medium reasoning

Baseline commit: `8b91d9c38a9228fa0db49b514591f2db6eac192c`

Final canary-tested code commit: `93a8804eb85f7a516ee388b9f3609cf0136c2034`

Merged experiment commit: `181e4dddd9e2aead6577233d82f9e354fe217296`

Final Core version: `0.15.3`

## Executive conclusion

The experiment found a reliable safety core and an unreliable conversational shell. The baseline never installed anything before confirmation, and every completed installation matched the plan and independent host readback. However, only 10 of 20 profiles completed the intended user experience without a product defect. Most failures happened when the model was expected to reproduce deterministic copy or preserve a required transition from written instructions alone.

Moving those transitions into code changed the result. After four hardening increments, every profile had a passing isolated run, with no unresolved warning. This supports a narrower claim than “production-ready”: Evidence Lab Core 0.15.3 is acceptance-hardened for synthetic Codex CLI onboarding on isolated Linux with Terra medium. Public-release confidence still requires one clean 20-scenario rerun on the exact final release candidate, a maintained runner with durable receipts, and independent review.

## What was tested

The matrix contains ten English and ten Russian profiles. It covers numeric selections, free-text answers, nine disciplines or cross-disciplinary routes, all six research stages, and installations ranging from 9 to 12 packs.

Each scenario started with a fresh Codex state and research repository. The harness checked that:

1. both supported languages appeared before any research question;
2. the four catalog-backed questions appeared in order, one per turn;
3. no Evidence Lab plugin or installation state existed before confirmation;
4. the visible recommendation used canonical localized copy rather than raw IDs;
5. installation started only after explicit confirmation of the whole plan;
6. the resulting installation state was `ready`;
7. every desired ID and version matched both `installed_after` and an independent `codex plugin list --json` readback;
8. the completion message told the researcher to open a new task.

External account connections and companion plugins were outside this experiment. The harness did not install them, preserving the separate explicit-consent boundary.

## Results

### Baseline

The raw harness result on the baseline commit was 9/20. Manual inspection found that `en-12-astrophysics` had produced a valid new-task instruction that the matcher failed to recognize. The adjudicated product baseline was therefore 10/20, while the harness baseline remained 9/20.

The ten real product failures were:

| Failure class | Count | Affected scenarios | User-visible effect |
| --- | ---: | --- | --- |
| Improvised first question after language selection | 3 | `ru-05-econometrics`, `en-11-epidemiology`, `en-18-neuroscience` | The flow diverged from the four-question catalog before profile collection was complete. |
| Technical ID/version plan instead of the localized recommendation | 5 | `ru-06-history-qualitative`, `ru-07-computational-biology`, `en-15-sociology`, `en-16-literature`, `en-19-operations-research` | The user saw implementation details rather than the promised plain-language plan. |
| Plan-turn timeout on a free-text profile | 1 | `ru-02-clinical-review` | The flow stopped before confirmation and installation. |
| Missing new-task instruction after a successful install | 1 | `en-17-chemistry` | The backend was ready, but the user did not receive the step needed to load the new capabilities. |

Safety did not fail. No failed dialog installed anything before confirmation, and every completed installation had exact plan/readback parity.

### After hardening

All initially failed profiles were rerun after the relevant fix. The cumulative acceptance matrix ended at 20 passing profiles, 0 failed profiles, and 0 unresolved warnings.

Passing runs took 281–693 seconds, with a median of 376 seconds. Pack selection was concentrated near the foundation size:

| Selected packs | Profiles |
| ---: | ---: |
| 9 | 12 |
| 10 | 3 |
| 11 | 4 |
| 12 | 1 |

These duration and selection figures describe the successful runs collected across the hardening sequence. They are not a performance benchmark of one immutable candidate.

## Root-cause analysis

### Written instructions were not a deterministic interface

The onboarding skill described the intended questions, recommendation, and completion step, but the model still paraphrased, improvised, or omitted them. The instructions were useful for intent, not sufficient for an exact user-interface contract.

The defect pattern was concentrated at boundaries where the model had to copy a required message and then decide what to do next. Core selection and installation logic were deterministic; the model-controlled presentation layer was not.

### A renderer alone was not enough

Adding a renderer reduced freedom but did not guarantee that the model would call it at the right time. Reliability improved when the required user-facing output became part of the same command that created the plan or applied the installation. This removed a discretionary step between state mutation and presentation.

### Backend success and user-flow success are separate gates

The `en-17-chemistry` run installed the correct packs and passed readback, yet still failed the flow because it omitted the new-task instruction. A `ready` state is necessary, but it does not prove that the researcher can continue successfully.

### The harness also needs adjudication

The `en-12-astrophysics` false negative shows that a strict matcher can disagree with the artifact even when the product behavior is acceptable. Automated checks should remain strict, but failures need a saved artifact and a documented adjudication path. Otherwise the experiment can confuse harness defects with product defects.

### Free text is the expensive path

The only plan-turn timeout occurred on a detailed clinical free-text profile. One observation is not enough to estimate a failure rate, but it identifies the path that needs larger timeout budgets, stage-level timing, and focused stress tests.

## Hardening applied

The fixes progressively moved required behavior out of model prose and into deterministic commands:

- Core 0.15.0 added deterministic language and question rendering.
- Core 0.15.1 fused plan creation with localized recommendation rendering.
- Core 0.15.2 invoked the language renderer from the copy-paste entry prompt and added canonical localized completion output.
- Core 0.15.3 required `--locale` for clean apply, so a successful installation could not omit the localized completion contract.

The resulting reliability pattern is:

```text
deterministic language prompt
  -> deterministic question renderer
  -> validated profile normalization
  -> fused plan + localized recommendation
  -> explicit whole-plan confirmation
  -> locale-required apply + completion
  -> installation state + independent host readback
```

This pattern should remain the default for future onboarding changes: the model may interpret bounded free text, but it should not invent required questions, installation plans, consent boundaries, or completion instructions.

## What the experiment proves

- The confirmation boundary held across all observed runs.
- Pack selection and installation readback remained exact whenever installation completed.
- The 20-profile matrix is broad enough to expose presentation defects that a single happy-path run missed.
- Deterministic rendering is most reliable when it is fused with the command that changes state.
- Numeric and free-text onboarding can share one flow, but free text needs separate latency and failure monitoring.

## What it does not prove

- It does not prove that all 20 profiles pass from scratch on the same final commit. The 20/20 result is cumulative across the hardening sequence. Core 0.15.3 received four direct real-flow canaries: `en-20-early-career`, `ru-01-quant-physics`, `ru-05-econometrics`, and `en-12-astrophysics`.
- It does not cover Codex desktop UI behavior, Claude Code, macOS, or WSL2.
- It does not compare models or reasoning levels; only Terra medium was used.
- It does not measure real-researcher comprehension or satisfaction. The profiles were synthetic.
- It does not test expired authentication, network loss, interrupted apply, marketplace failure, partial host installation, or stale release state.
- It does not test installation of external companion plugins or account connections.
- It does not provide an independent human review. The requested reviewer was unavailable, and the automated Copilot review did not run because its quota was exhausted.
- Raw Codex event streams and isolated caches were not committed because they contain host-specific runtime metadata. The repository therefore contains scenarios and the aggregate report, not a complete machine-auditable receipt for every run.

## Improvement backlog

### P0: required before a production-readiness claim

1. Rerun all 20 scenarios from clean state against one immutable final release commit and lock file. Report the result as a new cohort rather than combining it with earlier candidate runs.
2. Add a maintained acceptance runner. It should pin model, reasoning effort, commit, release lock, timeout policy, and isolation settings.
3. Save a sanitized machine-readable receipt for every run: scenario ID, candidate commit, Core version, timestamps, selected pack IDs and versions, plan hash, state hash, independent readback hash, checks, result, and normalized failure class. Exclude session IDs, credentials, absolute private paths, and raw host caches.
4. Make exact user-facing output contracts testable in code. The runner should verify canonical message identifiers or structured events rather than rely only on fuzzy text matching.
5. Obtain independent review of the report, runner, receipts, and final cohort before changing the readiness claim.

### P1: release-quality coverage

1. Repeat the matrix through Claude Code and the Codex app path, then add macOS and WSL2 host coverage.
2. Add cross-model runs so deterministic behavior is not inferred from Terra alone.
3. Add free-text fuzzing, mixed-language answers, invalid selections, corrections, early confirmation attempts, and adversarial requests to skip consent.
4. Add failure injection for timeouts, interrupted apply, network loss, marketplace clone failure, partial installation, stale locks, and readback mismatch.
5. Record stage-level timing and define a performance budget only after a clean final-candidate cohort provides comparable data.
6. Verify in a newly opened task that installed skills are actually discoverable and usable, not merely present in host inventory.

### P2: product learning

1. Run a moderated usability study with real researchers from several disciplines.
2. Test the separate companion-plugin recommendation and consent flow.
3. Design opt-in diagnostics that can preserve useful failure evidence without collecting research content or host secrets.

## Release recommendation

Use the current result to label Core 0.15.3 as **acceptance-hardened for isolated Codex CLI onboarding on Linux**. Do not label it production-ready or claim complete Codex/Claude parity yet.

The next release gate is a single immutable-candidate cohort: 20/20 clean runs, sanitized receipts, the full repository gate, independent review, and no unresolved safety or readback defect. Performance and usability should remain separate gates rather than being inferred from functional success.

## Reproduction material

- English scenarios: `tests/acceptance/onboarding-terra-20.scenarios.json`
- Russian scenarios: `tests/acceptance/onboarding-terra-20.scenarios.ru.json`
- Entry contract: `START.md`
- Bootstrap contract: `BOOTSTRAP.md`
- Merged implementation and initial report: [PR #25](https://github.com/timsmykov/evidence-lab-plugins/pull/25)

Raw Codex event streams and isolated plugin caches are intentionally not committed because they contain host-specific runtime metadata. The original adjudication used saved structured plans, installation states, independent plugin readbacks, and final-message artifacts for each run.
