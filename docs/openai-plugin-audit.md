# OpenAI Codex plugin directory audit

Snapshot fetched at `2026-08-27T10:29:23.043960168Z`; SHA-256 `0f8a326bd304f723110e91198145aa2d5ebda96ba6f7b50fb23c6aa92377314d`.
The audit script examines every entry in the snapshot and then narrows the product review to globally listed, available entries.

## Whole-catalog result

- All global directory entries: **3045**.
- Active, listed, installable entries: **2717**.
- App-only: **2444**; hybrid app + skills: **244**; skills-only: **29**.
- Exact plugin-name matches for `Tectonic`: **0**.
- Plugin names containing `LaTeX`: none.

A directory entry is not automatically a downloadable skill bundle. App-only and hybrid entries can require an account connection, an installation interstitial, or an external service. Evidence Lab must never silently treat those as zero-dependency skills.

## Active categories

| Category | Entries |
|---|---:|
| Business & Operations | 565 |
| Productivity | 505 |
| Other | 358 |
| Finance | 277 |
| Travel | 263 |
| Developer Tools | 164 |
| Education & Research | 158 |
| Data & Analytics | 119 |
| Creativity | 101 |
| Entertainment | 97 |
| Healthcare | 63 |
| Communication | 25 |
| Security | 18 |
| Scientific Research | 4 |

## Research shortlist

| Plugin | Developer | Type | Skills | Apps | Authentication | Review decision |
|---|---|---|---:|---:|---|---|
| BioRender | BioRender | `app-only` | 0 | 1 | `ON_INSTALL` | Useful life-science image companion app; separate user connection required. |
| Build Web Data Visualization | OpenAI | `skills-only` | 18 | 0 | `ON_USE` | Optional interactive/web visualization; not a replacement for publication figures. |
| Consensus | Consensus | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Data Analytics | OpenAI | `hybrid` | 15 | 20 | `ON_USE` | Hybrid with external apps; benchmark and connection flow required. |
| Elicit | Elicit, Inc. | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Life Science Research | OpenAI | `skills-only` | 50 | 0 | `ON_INSTALL` | Strong skill-bundle candidate; representative behavior tests required before default selection. |
| Life Sciences NGS Analysis | OpenAI | `skills-only` | 18 | 0 | `ON_INSTALL` | Explicit opt-in only; heavy local scientific toolchain and mixed maturity. |
| PaperDock | Hanbit Kim | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| SciSpace | SciSpace | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Scite | Scite | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Sider Scholar | Sider AI | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Strive PDF Generator | Strive Math | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Undermind | Undermind AI, Inc. | `app-only` | 0 | 1 | `ON_INSTALL` | External research app; benchmark before recommending a default. |
| Wolfram | Wolfram Research | `app-only` | 0 | 1 | `ON_INSTALL` | Useful quantitative companion app; separate user connection required. |
| Zotero | OpenAI | `skills-only` | 1 | 0 | `ON_INSTALL` | Recommend only when Zotero Desktop is used or detected; local application dependency. |

## Product boundary

1. Evidence Lab packs remain the portable Codex + Claude layer.
2. Codex runtime plugins already present on the host may be used as baseline capabilities after readback verification.
3. Reviewed skills-only plugins may enter deterministic selection only after structural and representative behavior tests.
4. Directory apps are recommendations, not silent bootstrap operations. The user confirms the connection in Codex and Evidence Lab verifies availability afterward.
5. External plugin contents are referenced by stable directory ID and observed version; they are not copied into this MIT repository.

Official references: https://learn.chatgpt.com/docs/plugins and https://learn.chatgpt.com/docs/build-plugins.
