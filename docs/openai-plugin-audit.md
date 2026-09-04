# Codex researcher plugin marketplace audit

Snapshot fetched at `2026-08-31T11:54:38.767836828Z`; SHA-256 `eeb90d6c8990edc7235a095eeafc930346137529dd13c50225202b38e0b42d02`.
This is a complete catalog screen, not a claim that every external service has been behavior-tested.

## What was audited

- All directory records: **3205**; active, listed, installable records: **2818**.
- Whole active catalog: **2520 app-only**, **261 hybrid**, **37 skills-only**.
- Complete researcher-facing category inventory: **303** entries across Education & Research, Data & Analytics, and Scientific Research.
- In those categories: **259 app-only**, **32 hybrid**, **12 skills-only**.
- Exact `Tectonic` matches: **0**; names containing `LaTeX`: **0**.

The Install button is not evidence of zero cost or zero setup. App-only and hybrid entries connect an external service. A skills-only entry can still require an account, local software, a heavy toolchain, or paid jobs.

## Pure skill bundles in the three target categories

| Plugin | Category | Skills | Provider/runtime dependency | Bootstrap decision |
|---|---|---:|---|---|
| Mixpanel Headless | Data & Analytics | 4 | `external-account-required` / `python-sdk-and-mixpanel-account` | `exclude-from-researcher-default` |
| Life Science Research | Education & Research | 50 | `no-provider-account-observed` / `public-endpoints-and-local-runtime` | `candidate-after-behavior-benchmark` |
| Life Sciences NGS Analysis | Education & Research | 18 | `no-provider-account-observed` / `heavy-local-bioinformatics-toolchain` | `explicit-domain-opt-in` |
| Zotero | Education & Research | 1 | `local-application-required` / `local-zotero-desktop` | `explicit-tool-opt-in` |
| Adaptyv Bio | Scientific Research | 4 | `external-account-required` / `external-protein-experiment-platform` | `exclude-from-researcher-default` |
| Biological Sequence & Alignment Viewer | Scientific Research | 1 | `no-provider-account-observed` / `local-scientific-viewer-runtime` | `explicit-domain-opt-in-after-benchmark` |
| Boltz | Scientific Research | 8 | `external-account-and-spend-confirmation-required` / `boltz-cli-auth-and-paid-jobs` | `explicit-domain-opt-in-after-benchmark` |
| Life Sciences Databases | Scientific Research | 44 | `no-provider-account-observed` / `public-life-science-database-endpoints` | `candidate-after-behavior-benchmark` |
| Life Sciences Literature | Scientific Research | 3 | `no-provider-account-observed` / `public-literature-and-open-access-endpoints` | `candidate-after-behavior-benchmark` |
| Molecular Structure Viewer | Scientific Research | 1 | `no-provider-account-observed` / `local-scientific-viewer-runtime` | `explicit-domain-opt-in-after-benchmark` |
| NGS Analysis Workbench | Scientific Research | 5 | `no-provider-account-observed` / `local-sequencing-analysis-toolchain` | `explicit-domain-opt-in-after-benchmark` |
| Slide Viewer | Scientific Research | 1 | `no-provider-account-observed` / `local-scientific-viewer-runtime` | `explicit-domain-opt-in-after-benchmark` |

## Bootstrap policy

1. Evidence Lab-owned packs remain the portable Codex + Claude layer.
2. A reviewed pure skill bundle may be proposed only when its profile signals match and its dependency preflight passes.
3. App-only and hybrid plugins are connection offers. They are never silently installed or described as free without current official evidence.
4. Account, subscription, API, data-sharing, and paid-compute terms are independent fields. Unknown means unknown, not free.
5. User confirmation is required before every external connection and before any workflow that can incur spend.

## Product-review shortlist

| Plugin | Category | Type | Access evidence | Decision |
|---|---|---|---|---|
| Academic Writing Toolkit | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Ace Knowledge Graph | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Acumen by Talarion | Education & Research | `hybrid` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| alphaXiv | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Amass | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Article Galaxy | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Biological Sequence & Alignment Viewer | Scientific Research | `skills-only` | `no-provider-account-observed` | `explicit-domain-opt-in-after-benchmark` |
| BioRender | Creativity | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Boltz | Scientific Research | `skills-only` | `external-account-and-spend-confirmation-required` | `explicit-domain-opt-in-after-benchmark` |
| Build Web Data Visualization | Developer Tools | `skills-only` | `no-provider-account-observed` | `optional-output-format-opt-in` |
| Consensus | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| CourtListener | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Data Analytics | Data & Analytics | `hybrid` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Deep Research | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Dewey Data | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Elicit | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| GoVeda Patent | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Life Science Research | Education & Research | `skills-only` | `no-provider-account-observed` | `candidate-after-behavior-benchmark` |
| Life Sciences NGS Analysis | Education & Research | `skills-only` | `no-provider-account-observed` | `explicit-domain-opt-in` |
| Midpage Legal Research | Education & Research | `hybrid` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Mixpanel Headless | Data & Analytics | `skills-only` | `external-account-required` | `exclude-from-researcher-default` |
| Molecular Structure Viewer | Scientific Research | `skills-only` | `no-provider-account-observed` | `explicit-domain-opt-in-after-benchmark` |
| PaperDock | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Patent Connector | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Precise Special Functions | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Readwise | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Scholar Gateway | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Scholar Sidekick | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| SciSpace | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Scite | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Sider Scholar | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Slide Viewer | Scientific Research | `skills-only` | `no-provider-account-observed` | `explicit-domain-opt-in-after-benchmark` |
| Strive PDF Generator | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Transkriptor | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Undermind | Scientific Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Wolfram | Education & Research | `app-only` | `external-service-terms-unverified` | `connection-candidate-after-benchmark` |
| Zotero | Education & Research | `skills-only` | `local-application-required` | `explicit-tool-opt-in` |

## Official access review for high-priority services

These facts are intentionally separate from the catalog manifest and must be refreshed when provider terms change.

| Plugin | Current access evidence | Official source |
|---|---|---|
| Consensus | Free account tier includes limited MCP/ChatGPT calls; paid tiers raise limits and can enable metered overage. | https://help.consensus.app/en/articles/10059020-consensus-in-chatgpt |
| Elicit | Free Basic plan exists with limited agent/report usage; paid plans add capacity and exports. | https://elicit.com/pricing |
| Readwise | Thirty-day free trial, then a paid subscription; no permanent free plan is advertised. | https://readwise.io/pricing/reader |
| SciSpace | Free Basic tier is credit-limited; paid subscriptions increase monthly agent credits. | https://scispace.com/resources/credits-pricing-guide/ |
| Scite | MCP access is included in paid individual plans; the public pricing page offers a time-limited trial, not a perpetual free MCP tier. | https://scite.ai/pricing |
| Zotero | The local open-source application is free; optional hosted file storage has a free allowance and paid larger tiers. | https://www.zotero.org/storage |

## Complete category inventory

Every active entry in the three target categories appears below. `catalog-screened` means identity and component shape were checked from the Codex directory; it does not mean pricing or behavior was independently verified.

| Category | Plugin | Developer | Type | Skills | Apps | Screen decision |
|---|---|---|---|---:|---:|---|
| Data & Analytics | AIDA Platform | Vibezz | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | AirOps | Rivington Labs, Inc. dba AirOps | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | AiTrillion | Aitrillion | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Alation | http://alation.com/ | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Alizé | Alizé | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Allium | Allium Labs Inc. | `hybrid` | 6 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Amplifyr | Amplifyr Engineering Team | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | ApartmentIQ | ApartmentIQ | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Appskyline | Appskyline | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Atlan | Atlan | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | august | Fermat Commerce | `hybrid` | 9 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Aurora | Consilio, LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | AWS Data Analytics | Amazon Web Services | `hybrid` | 9 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Azadea One | HYVE LABS LLC | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | BencinaMCP | Kemeny Studio | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | BigGeo AI | BigGeo Globle Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | BlazeSQL | Blaze Analytics vGmbH | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Blockscout Blockchain Data | Blockscout LTD | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Book Report | Chapter 14 Publishing Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Brand & Market Social Research | Telemark Digital | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Carbon Arc | Carbon Arc Corporation | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Catchr | Catchr | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | CData Connect AI | CData Software Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Centiment | Centiment LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | ChartMogul | ChartMogul | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Clarivate IPOne CM Trademarks | Clarivate | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Cleverbridge | Cleverbridge | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Clics | ESSONAM MAXIMIN PAGNIOU | `hybrid` | 1 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Collecte MTL | Sebastien Castiel | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Coupler.io | Coupler.io | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Coupler.io | Railsware Products Studio, LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Crunchbase | Crunchbase | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Customer Journey Analytics | Adobe | `hybrid` | 6 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Daily Command | Doceree | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Damoov Telematics | Damoov | `hybrid` | 3 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Data Analytics | OpenAI | `hybrid` | 15 | 20 | `connection-candidate-after-benchmark` |
| Data & Analytics | DataAssist-IO | Absolute TechTeam | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Datadog Experiments | Datadog Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Dataslayer | Dataslayer | `hybrid` | 7 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Deepnote | Deepnote, inc. | `hybrid` | 5 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | DMAP AI | AgriMetSoft LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | DXB Interact | DXBInteract | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Enterpret | Enterpret Inc | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Evidence Studio | Evidence Technologies | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Extract | Extract | `hybrid` | 3 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Ezoic Analytics | Ezoic | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Feedoptimise | Feedoptimise | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Formester | Formester Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Fr8Labs Analytics | Fr8labs | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Fullmetrix | Fullmetrix | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Gainsight Customer Communities | gainsight | `hybrid` | 1 | 1 | `not-bootstrap-priority` |
| Data & Analytics | GIS Cloud | GIS Cloud | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Helium 10 | Helium 10 | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Hex | Hex | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Homesage.ai | Homesage.ai | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Hypha | Hypha | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Improvado AI Agent | Improvado Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Isocarto | 2803 MEDIA | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Jepto | Jepto | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | JoomPulse | Joom | `hybrid` | 17 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | K-water | 한국수자원공사 (K-water) | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Kanal | Kanal | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Kindora | Justin Richard Steele | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | KrystalView | Krystal Unity Pty Ltd | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Landstack | Thovex Ltd | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Lead Recorder | Lead Recorder | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Leo - Running Coach | NICOLAS AGUER | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Lytical | Lytical, Inc. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Master Metrics | Master Metrics LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Metorik | Metorik | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Minter.io | Minterly Limited | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Mixpanel | Mixpanel | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Mixpanel Headless | Mixpanel | `skills-only` | 4 | 0 | `exclude-from-researcher-default` |
| Data & Analytics | MoSPI | NSO India | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | MotherDuck | MotherDuck Corporation | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | New Vintage | New Vintage Labs, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Omni | Omni Analytics | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Padel Analyst | Ferran Figueredo | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | PagePulse | Page Pulse, LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Parcelle Cadastre | 2803 MEDIA | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Peec AI | Peec AI | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Polar Analytics | Polar Analytics, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | PolicyNote | FiscalNote | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Porter Metrics | Porter Metrics | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | PostHog | PostHog Inc. | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | PowerDMARC | PowerDMARC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Powerset Research | Powerset Research | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Propalt | Propalt | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Property Hazard MCP | ERIC SHEN | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Pulse by PassBy | PassBy | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Quanti IA | Quanti | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Ramp Data | Ramp | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Recall Scout | SIMON MAN SHIH | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Refiner | Refiner SASU | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Remedy Legal | LISTO LABS | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Repuso | OnClick Solutions Ltd | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Reverse Contact | Reverse Contact | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | SEO Programático | ESTEBAN ROBERTO ALEART SALAS | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Serpstat | Serpstat | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Similarweb | Similarweb Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | SiteTrax.io | SiteTrax.io | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Sixtyfour Intelligence | SixtyFourAI | `hybrid` | 1 | 1 | `not-bootstrap-priority` |
| Data & Analytics | SkyWatch | SkyWatch Space Applications Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Sleekplan | Sleekplan GmbH | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Sometrend | VAIV Company Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Sometrend | VAIV Company | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | StatsHawk | EdgeHawk | `hybrid` | 2 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Steep | Steep Analytics | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Subtext | Fullstory | `hybrid` | 6 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Sweet Analytics | Sweet Analytics | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Syncly Social | Syncly | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Tableau | Salesforce, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Tango MCP | MakeGov Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Technis | Technis SA | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Temso | Temso | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Tenzo | Tenzo | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | ThoughtSpot Spotter | ThoughtSpot | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Trace | Trace | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Typeform | Typeform | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Waldo | Curiosities, Inc. | `hybrid` | 6 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | WaveMaster AI | GUSTAVO FELIPE DAROS TRENTINI | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Data & Analytics | Webless | Webless | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Windsock | Windsock | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | WitCloud | Witbee Sp. z o.o. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | Yuno | Yuno | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Data & Analytics | ラッコキーワード | ラッコ株式会社 | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | A-Z Daily Word | Spheric Admin Ltd | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | A-Z Dictionary | Widget | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | AbS | AbS GLOBAL INVESTMENT INT'L LTD | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Academic Writing Toolkit | VULCA | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Ace Flashcard Maker | Sider AI | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Ace Knowledge Graph | Sider AI | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Ace Quiz Maker | Sider AI | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Acumen by Talarion | Talarion, Inc. | `hybrid` | 1 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | ADTraining | ADTraining | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Agora | Factagora Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | AhaMotion | Sider AI | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | AI4F Japanese Study | Tin Nguyen | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | AL WAKEELO | Al Wakeelo | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | AliXAi | 42Lab | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | alphaXiv | alphaXiv | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Amass | Amass Technologies ApS | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Any Fact Widget | Widget | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | AnyLessonPlan for Teachers | Spheric Admin Limited | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | API Lessons | Level 250 Inc. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | ApplyBoard | ApplyBoard | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Article Galaxy | Article Galaxy | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Assessment Generator | Colossyan Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Audioscrape | Audioscrape Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Açık Silivri Havadis | Can Tasdemir | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Beast Academy - All Ten | Art of Problem Solving | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Bee Spelling | Spheric Admin Ltd | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | BestColleges.com | Red Ventures | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Bible | Life.Church (YouVersion) | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Blossom | Flower&Technology | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Bodhaka Virtual Labs | BuoyantWave Learning Technologies LLP | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Boluda | JOAN BOLUDA LLONGUERAS | `hybrid` | 4 | 1 | `not-bootstrap-priority` |
| Education & Research | Brisk Teaching | Brisk Labs Co. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Chegg Study | Chegg Inc | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Chessvia Openings | Chessvia | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Chymia | Noah Galvão | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Cody Reading | Cody Reading Inc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | College Vidya | Blackboard E-Learning Pvt Ltd | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Common Room | Common Room | `hybrid` | 6 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Consensus | Consensus | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Contact Center AI Association | ProxyLink | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | CoreStepPrep | CoreStepPrep | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Course Studio | Colossyan | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Coursera | Coursera | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | CourtListener | Free Law Project | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | DataCamp | DataCamp | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Deep Research | OpenAI | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Descrybe Legal Engine | Descrybe.com | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Dewey Data | Dewey Data Inc. | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Dhamma Data | boothcheck llc | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Digital Compass | Marian Matinca | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Dow Jones Factiva | Factiva, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Drill | Jordan Martinelli | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Eclat Institute | WEI JIE CHEE | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | edifyedu.in | Rishi Kumar | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | EduInsights | AI Idea  Lab | `hybrid` | 4 | 1 | `manual-review-if-profile-matches` |
| Education & Research | EduRolia | Majotek | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Edvoy | Edvoy technologies private limited | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | edX | 2U, LLC | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Elicit | Elicit, Inc. | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Emona | Emona | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | ETT | ETT Education & Technology Group | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Examen Civique | Maison Logiciels | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Explain Video Generator | Scrimba AS | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Flashcards Space | nicksmind.com | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | getMindmap | The Faculty Club SLU | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Glossarize | Widget | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | GoVeda Patent | GoVeda | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | GovQuery | Program Integrity Alliance (PIA) | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | How To Student | Vraj Shroff | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Inflearn | inflab.com | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | italki language learning | italki | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Kahoot! | Kahoot! | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Kiuwo | Mea S.R.L. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | KMath.app | CLASSCUBE CO.,LTD | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Kuliko AI | Kuliko Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Language Coach: English | Maxim Dubovitsky | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | LeapScholar | Leapscholar | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Learning Commons | Learning Commons | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Legal Data Hunter | GoodLegal | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Life Analytics IAS | Life Analytics Co LTD | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Life Science Research | OpenAI | `skills-only` | 50 | 0 | `candidate-after-behavior-benchmark` |
| Education & Research | Life Sciences NGS Analysis | OpenAI | `skills-only` | 18 | 0 | `explicit-domain-opt-in` |
| Education & Research | Lingard | Lingard | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Linked Word | GEORG M ZIMMER | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Lune | Tony | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Lurna | Lurna | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Mantic | Mantic Technologies | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | MedStats | Jonas Becker | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | MentorCruise | MentorCruise Inc | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | MetaMetrics® Lexile Analyzer | MetaMetrics Inc. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Metronome: Music tempo+beat | Widget | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Midpage Legal Research | Midpage | `hybrid` | 4 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | monPIF | Joris Cimpaka-Kapeta | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | MSDS Chain | LAgentBot Pte. Ltd. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Music Block | OLEKSII SHEVCHENKO | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Mynawoo AI Language Tutor | Alireza Saligheh | `hybrid` | 1 | 1 | `not-bootstrap-priority` |
| Education & Research | NoBrainner | Adenilson Ribeiro | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | NYCU Library | National Yang Ming Chiao Tung University Library | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Nylon | Nylon | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Omphalis | Voxiven, LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | OpenRegs: Regulatory Research | OpenLaws Public Benefit Corporation | `hybrid` | 2 | 1 | `manual-review-if-profile-matches` |
| Education & Research | PaperDock | Hanbit Kim | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Parenting Hub | JupitLunar | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Particl Market Research | Particl | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Patent Connector | Funktionslust GmbH | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Pencil Spaces | Pencil Learning Technologies | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | PhysioKeys | Physiokeys | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | PokeBot.ai Career Coach | PokeBot | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Powers Index | KP Powers | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Precise Special Functions | Assaf Lanir | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Premom Ovulation Calculator | Easy Healthcare Corporation | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Preply Language Tutor Finder | Preply | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Promova | Unlimited Promova Limited | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | ProSchool360 | ProSchool360 | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Protplex | Straintest | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | QuizFlight | QuizFlight Teknoloji A.S | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Quizlet | Quizlet | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | QuizStage | Filip Manzi | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | quran.ai | quran.com | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Readwise | Readwise Inc. | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Recall | Recall | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Replio | AitekLabs | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Scholar Gateway | John Wiley & Sons Inc. | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Scholar Sidekick | Mark Lavercombe | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | ScholarshipOwl | Scholarship Services Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | SciSpace | SciSpace | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Scite | Scite | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Self Plagiarism Checker | Concepts and Context (WordBinary) | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | SFT Brain | NutriGuide LLC | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Sider Scholar | Sider AI | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | SimpleFeed News & Video MCP | SimpleFeed, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Skarim! | Dima Bokov | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Skillsail | Skillsail GmbH | `hybrid` | 1 | 1 | `not-bootstrap-priority` |
| Education & Research | SkinKnowledgeBase | Fulcrai Labs | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Spanish Law Research | Alex Pervezentsev | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Special Education Law | Special Education Law, LLC | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | SRS (Spaced Repitation System) | Ashutosh Bodade | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Strive PDF Generator | Strive Math | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Studocu | StudeerSnel B.V. | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | StudyMe.ai | Fautor ApS | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Studyportals | Studyportals | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | suplla | 隼人 大石 | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Tailo Lens | Estendio Ltd | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Talents Kids | Temnikova LDA | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | TapWaterMap | Squidcode LLC | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Tarteel | Tarteel, Inc. | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Taxiger Doc | JORIS CIMPAKA-KAPETA | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | The Economist - Graphs | The Economist | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Time Machine | ILKER KAVAS | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Transkriptor | tor.app | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Trivana Study — Quiz My Notes | Rerato Technologies | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | TriviaQuiz | Veblab | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | TTMNG Public | KAMOLLARD CHIVASATVETCHAKUL | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Udemy | Udemy | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Vocabden | MUHAMMET DEMIRCI | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | Vocabulary Trainer Shchebitka | Shchebitka | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Wayground | Quizizz Inc. (DELAWARE CORPORATION), Wayground | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | Wolfram | Wolfram Research | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |
| Education & Research | Zotero | OpenAI | `skills-only` | 1 | 0 | `explicit-tool-opt-in` |
| Education & Research | ZZAIM | Jeonghyeon Lim | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | أرشيف الإسلام | MOHAMED HESHAM RAGEB | `app-only` | 0 | 1 | `manual-review-if-profile-matches` |
| Education & Research | 受験王 | 株式会社アスターリンク | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Education & Research | 상식이 | https://dean.kr | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Scientific Research | Adaptyv Bio | OpenAI | `skills-only` | 4 | 0 | `exclude-from-researcher-default` |
| Scientific Research | Biological Sequence & Alignment Viewer | OpenAI | `skills-only` | 1 | 0 | `explicit-domain-opt-in-after-benchmark` |
| Scientific Research | Boltz | Boltz | `skills-only` | 8 | 0 | `explicit-domain-opt-in-after-benchmark` |
| Scientific Research | Inductive Bio | Inductive Bio | `hybrid` | 3 | 1 | `not-bootstrap-priority` |
| Scientific Research | Life Sciences Databases | OpenAI | `skills-only` | 44 | 0 | `candidate-after-behavior-benchmark` |
| Scientific Research | Life Sciences Literature | OpenAI | `skills-only` | 3 | 0 | `candidate-after-behavior-benchmark` |
| Scientific Research | Molecular Structure Viewer | OpenAI | `skills-only` | 1 | 0 | `explicit-domain-opt-in-after-benchmark` |
| Scientific Research | NGS Analysis Workbench | OpenAI | `skills-only` | 5 | 0 | `explicit-domain-opt-in-after-benchmark` |
| Scientific Research | Proto | BRIAN LANCE HIE | `app-only` | 0 | 1 | `not-bootstrap-priority` |
| Scientific Research | Rosalind Workbench | OpenAI | `app-only` | 0 | 0 | `manual-review-if-profile-matches` |
| Scientific Research | Rowan | Rowan Scientific Corporation | `hybrid` | 1 | 1 | `manual-review-if-profile-matches` |
| Scientific Research | Slide Viewer | OpenAI | `skills-only` | 1 | 0 | `explicit-domain-opt-in-after-benchmark` |
| Scientific Research | Tamarind Bio | Tamarind Bio | `hybrid` | 14 | 1 | `manual-review-if-profile-matches` |
| Scientific Research | Undermind | Undermind AI, Inc. | `app-only` | 0 | 1 | `connection-candidate-after-benchmark` |

## Sources and reproducibility

- The committed JSON preserves the complete target-category inventory and every active skills-only bundle.
- Re-run `python3 scripts/audit_openai_plugins.py <catalog-snapshot>` when the Codex directory changes.
- Official plugin model: https://learn.chatgpt.com/docs/plugins and https://learn.chatgpt.com/docs/build-plugins.
