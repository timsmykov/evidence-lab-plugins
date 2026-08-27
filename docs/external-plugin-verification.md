# External plugin verification record

Verified against the OpenAI Codex plugin snapshot fetched at `2026-08-27T10:59:31.573949222Z`.
This is a bounded technical verification, not scientific acceptance or permission to make a plugin a default.

## Results

| Candidate | Structural validation | Behavior evidence | Current decision |
|---|---|---|---|
| Life Science Research 1.0.3 | passed Codex plugin validation; 50 skills found | 16 bundled unit tests passed; no representative live database workflow was run | candidate, not automatic |
| Life Sciences NGS Analysis 1.0.3 | passed Codex plugin validation; 18 skills found | 47 bundled tests passed; 1 skipped because `scanpy/anndata` was unavailable; no end-to-end scientific dataset run | explicit opt-in only |
| Zotero 0.1.2 | passed Codex plugin validation; 1 skill found | CLI help loaded; safe local probe reported every route unavailable because Zotero Desktop was not running | explicit opt-in after detection/request |
| Build Web Data Visualization 0.1.21 | passed Codex plugin validation; 18 skills found | no representative Evidence Lab output benchmark yet | explicit opt-in only |
| Mixpanel Headless 0.1.2 | catalog manifest inspected; 4 skills found | setup skill requires Mixpanel authentication and a Python analytics stack | excluded from the researcher default |
| Boltz 0.1.1 | catalog manifest inspected; 8 skills found | setup skill requires `boltz-api` authentication; execution prompts explicitly require cost estimation and spend confirmation | specialist opt-in only after a behavior and spend-safety benchmark |

The Zotero probe is expected fail-closed behavior: it did not enable, restart, or mutate Zotero. NGS tests cover planners, resource gates, preflight, summaries, and selected helpers; they do not prove the correctness of a real sequencing analysis.

## Credential and dependency boundary

- **No API key required:** Life Science Research uses public database endpoints; network access is still required.
- **No API key, substantial local dependencies:** NGS Analysis needs scientific executables, references, and compute appropriate to the chosen lane.
- **No API key, local application required:** Zotero needs Zotero Desktop and its local API.
- **No API key for the skill bundle:** Build Web Data Visualization still needs the normal local web-development toolchain for generated outputs.
- **Separate account connection:** Wolfram, BioRender, Consensus, Scite, Elicit, SciSpace, and similar directory apps are not zero-dependency skill bundles.
- **Skill bundle with provider account:** Mixpanel Headless and Boltz prove that `skills-only` does not mean free or self-contained.

## Promotion gate

An external plugin may move to `approved-baseline` only when all of the following are recorded:

1. stable directory ID and observed version;
2. structural validation;
3. representative Evidence Lab behavior tests, including negative and unavailable-dependency cases;
4. overlap analysis showing why the component complements rather than duplicates an Evidence Lab pack;
5. plain-language install/connection flow and host readback;
6. independent review appropriate to the scientific risk.

Until then the deterministic companion planner may recommend, offer an explicit opt-in, offer a separate connection, or withhold the plugin. It may not silently install it.
An `explicit-opt-in` component is omitted from the normal recommendation list unless the researcher names it; this keeps the short onboarding from turning into a catalogue browser.
