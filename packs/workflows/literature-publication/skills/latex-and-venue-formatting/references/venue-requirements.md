# Venue requirements evidence contract

Use this reference whenever the request depends on journal, conference, repository, poster, or funder rules.

## Resolve one controlling target

Record the exact venue or agency, year or funding cycle, track or program, document type, submission stage, and authoring format. Do not combine publisher-wide guidance with journal-specific instructions when the journal supplies its own guide. Do not combine main-track, workshop, short-paper, rebuttal, and camera-ready rules.

## Source hierarchy

Prefer, in order:

1. the current official call, author instructions, submission guide, or solicitation;
2. the official template archive linked by that source;
3. the official submission-system instructions;
4. a publisher or society-wide guide only where the venue delegates to it.

Community summaries can help locate official sources but cannot control the final requirements record.

For each controlling source, record its URL, title, `checked_at` date, and the claims it supports. Recheck a source when the year, track, stage, or template release changes.

## Requirements record

Start from `assets/venue-requirements.template.json`. Populate only verified fields. Use `null` or an explanatory note when a rule is not specified; never turn absence into permission.

At minimum capture:

- page limits and exactly which sections count;
- paper size, columns, margins, fonts, and line spacing where specified;
- required and forbidden sections, declarations, checklists, and metadata;
- anonymity model and whether source/PDF metadata must be scrubbed;
- bibliography system and treatment of references in page limits;
- figure, table, accessibility, color, and supplemental-material rules;
- source archive, PDF, supplementary, and naming requirements;
- template source, status, version or checksum, and license/redistribution review;
- AI-assistance, confidentiality, and disclosure policy where relevant.

## Template handling

- Preserve the downloaded official archive and its provenance outside the skill package.
- Do not rename an old style file to a new year or infer compatibility from a similar venue.
- Do not copy official or publisher templates into Evidence Lab unless their redistribution terms were reviewed.
- Keep class and style files unchanged. Put manuscript-specific overrides in the document only when explicitly permitted.
- A generic scaffold is acceptable for drafting, but label it generic and replace it before a template-controlled submission.

## Researcher confirmation point

Before a large rewrite or migration between templates, show the resolved target, sources, template status, page-limit interpretation, anonymity model, and expected source changes. Continue only after the researcher confirms that interpretation.
