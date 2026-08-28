# Codex onboarding acceptance: 20 Terra scenarios

Date: 2026-08-28

Host: Codex CLI in a Bubblewrap-isolated Linux workspace

Model: `gpt-5.6-terra`, medium reasoning

Final tested commit: `93a8804eb85f7a516ee388b9f3609cf0136c2034`

Final Core version: `0.15.3`

## Result

Every one of the 20 synthetic researcher profiles has a passing clean-user run after hardening: 20 passed, 0 failed, and 0 unresolved warnings. The matrix contains ten English and ten Russian flows, numeric and free-text answers, nine disciplines or cross-disciplinary routes, all six research stages, and selected installations ranging from 9 to 12 packs.

The passing-run duration was 281–693 seconds, with a median of 376 seconds. Twelve profiles selected 9 packs, three selected 10, four selected 11, and one selected 12.

## Acceptance checks per scenario

Each run used a fresh Codex state and research repository. The harness checked:

1. both supported languages were offered before any research question;
2. the four catalog-backed questions appeared in order, one per turn;
3. no Evidence Lab plugin or installation state existed before confirmation;
4. the visible recommendation used the canonical localized heading rather than raw IDs;
5. installation ran only after an explicit whole-plan confirmation;
6. `status` was `ready`;
7. every desired ID and version matched both `installed_after` and an independent `codex plugin list --json` readback;
8. the completion told the researcher to open a new task.

No external account connection or companion plugin was installed: those remain a separate explicit-consent boundary.

## Baseline and defects found

The initial `main` candidate at `8b91d9c38a9228fa0db49b514591f2db6eac192c` produced a raw harness result of 9/20. Manual artifact adjudication corrected one matcher false negative, giving a product result of 10/20. The ten real failures were:

- three improvised first questions after language selection;
- five technical ID/version plans instead of the localized recommendation;
- one plan-turn timeout on a free-text clinical profile;
- one successful installation that omitted the required new-task instruction.

Safety did not fail. No dialog failure installed anything before confirmation, and every completed installation had exact plan/readback parity.

## Hardening applied

- Core 0.15.0 added deterministic language and question rendering.
- Core 0.15.1 fused plan creation and localized recommendation rendering, so the plan command no longer encourages an ID summary.
- Core 0.15.2 placed the language renderer directly in the copy-paste entry prompt and added canonical localized completion output.
- Core 0.15.3 made locale mandatory for clean apply, so a successful installation cannot omit completion copy.

All initially failed profiles were rerun after the relevant fix. The final 0.15.3 candidate received direct real-flow canaries for the former completion failure, quantitative control, econometrics, and astrophysics. The full repository gate and immutable 14-pack release-lock verification passed at the final commit.

## Reproduction material

- English scenarios: `tests/acceptance/onboarding-terra-20.scenarios.json`
- Russian scenarios: `tests/acceptance/onboarding-terra-20.scenarios.ru.json`
- Entry contract: `START.md`
- Bootstrap contract: `BOOTSTRAP.md`

Raw Codex event streams and isolated plugin caches are intentionally not committed because they contain host-specific runtime metadata. The report is based on saved structured plans, installation states, independent plugin readbacks, and final-message artifacts for every run.
