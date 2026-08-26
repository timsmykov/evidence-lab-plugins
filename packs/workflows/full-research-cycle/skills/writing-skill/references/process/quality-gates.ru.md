# Quality Gates

Use these checks before the final response. For short one-paragraph tasks, apply them mentally. For medium and long texts, run them explicitly before the `humanizer` final pass.

A quality gate is not a passive checklist. If a gate fails, revise the draft before final output. Do not explain the gate to the user unless the user asked for critique, rationale, or a process view.

## Gate Workflow

1. **Task fit pass** — confirm task type, language, genre, audience, purpose, length, format, and source constraints.
2. **Evidence pass** — check that every factual claim is supported by user-provided material, cited/retrieved sources, common non-controversial knowledge, or a visible placeholder.
3. **Genre pass** — apply exactly one primary genre reference. For hybrid tasks, identify the dominant genre and borrow secondary rules only when needed.
4. **Language pass** — apply the selected language reference. Do not mix Russian and English heuristics.
5. **Voice pass** — compare the draft against user samples, requested tone, audience, and channel.
6. **Translationese pass** — for Russian text based on English-language sources, remove English islands, literal calques, hybrid compounds, and source-language syntax unless intentionally preserved.
7. **Diagnostic pass** — when requested, report issues by category and priority before rewriting; otherwise run the same checks internally.
8. **Anti-AI pass** — remove formulaic, generic, inflated, or over-smoothed language while preserving meaning.
9. **Meaning-preservation pass** — verify names, numbers, dates, terms, quotes, caveats, causal links, claims, source attributions, and document-specific commitments.
10. **Humanizer pass** — apply the separate `humanizer` skill in the same language and register, then re-check meaning preservation.

## Universal Gates

### 1. Task Fit

The output must match the requested task type, language, genre, length, audience, and format.

If it fails:

- reroute to the correct language or genre reference
- change mode: create, rewrite, adapt, critique, shorten, expand, or variants
- cut or expand to fit length
- change structure to match the requested format
- ask a clarifying question only if the missing constraint would materially change the output

### 2. Source Discipline

Every factual claim must come from user-provided material, cited/retrieved sources, or be marked as a placeholder. Do not invent citations, statistics, studies, examples, customer claims, expert names, legal claims, product capabilities, testimonials, methods, sample sizes, dates, financial outcomes, or personal anecdotes.

If it fails:

- replace unsupported factual claims with placeholders such as `[источник]`, `[citation needed]`, `[данные]`, `[proof needed]`, `[нужно подтверждение]`
- weaken the claim into a hypothesis or possibility
- remove fake authority phrases such as `исследования показывают`, `experts agree`, or `studies show`
- ask for sources only when a useful draft cannot be produced with placeholders

### 3. Genre Routing

One genre reference should govern the draft:

- academic -> `references/genres/academic.md`
- business/professional -> `references/genres/business.md`
- essay/publicistic -> `references/genres/essay-publicistic.md`
- copywriting -> `references/genres/copywriting.md`
- creative prose -> `references/genres/creative-prose.md`

If it fails:

- choose the closest dominant genre
- remove structures borrowed from the wrong genre
- preserve hybrid elements only when they serve the user's task
- do not let copywriting become essay, essay become neutral report, creative prose become plot summary, or business writing become a decorative memo

### 4. Language Routing

Russian and English checks are not interchangeable. Mixed-language outputs must be reviewed passage by passage.

If it fails:

- apply Russian checks only to Russian passages
- apply English checks only to English passages
- avoid translating language-specific advice directly across languages
- preserve native idiom rather than producing translation-shaped prose

### 5. Structure

The text should have a clear internal line of thought, but it should not look like a mechanical template.

If it fails:

- merge repetitive sections
- remove headings or bullets that do not reduce reader effort
- vary paragraph length when the genre allows it
- make each paragraph add a new claim, example, turn, mechanism, consequence, beat, action, finding, or recommendation

### 6. Voice and Register

The register must fit the user, audience, channel, and genre. The draft should not be over-polished, too official, too casual, too promotional, too literary, too academic-sounding without evidence, or too motivational.

If it fails:

- compare against user-provided samples
- remove the extra stylistic layer
- keep formality where the genre requires it
- preserve useful roughness, asymmetry, directness, or compression when it belongs to the voice
- do not add jokes, slang, emotion, anecdotes, or intimacy unless requested

### 7. Specificity

Abstract claims should be tied to concrete actors, actions, mechanisms, limits, examples, or evidence.

If it fails:

- replace empty adjectives with mechanisms or evidence
- replace vague benefits with user-visible outcomes
- replace vague business actions with owner/action/deadline where provided
- add placeholders where proof is needed
- do not invent examples just to add specificity

### 8. Meaning Preservation

Quotes, names, terms, numbers, dates, caveats, conditions, causal links, source attributions, POV, character facts, product facts, academic claims, and business commitments must survive revision and humanization.

If it fails:

- restore the original fact or caveat
- undo over-aggressive simplification
- preserve exact terminology when it carries domain meaning
- preserve character, scene, offer, argument, citation, recommendation, or business decision facts unless the user requested transformation

### 9. Anti-AI Surface

Remove formulaic openings, generic summaries, symmetrical rhetoric, decorative transitions, inflated conclusions, over-neat lists, and over-smoothed paragraph rhythm.

If it fails:

- replace formula with the actual claim, scene, pressure, mechanism, ask, finding, or recommendation
- cut filler signposting
- vary rhythm only where it helps meaning
- end on a concrete implication, decision, next action, image, limitation, unresolved tension, citation need, or specific CTA

### 10. Final Dependency

Apply the separate `humanizer` skill to the draft in the same language before final output.

If the environment cannot load `humanizer`, perform a short final anti-AI pass using the selected language reference. Do not mention implementation details to the user.

After humanization, re-check meaning preservation. If the humanizer changed facts, emphasis, caveats, terms, claims, citations, business commitments, or voice, restore the safer version.

## Russian Gate

For Russian texts, check especially:

- канцелярит and long nominalization chains
- `является / представляет собой / выступает в качестве` outside strict definitions
- `данный / указанный / вышеупомянутый / соответствующий` outside legal or normative register
- pseudo-academic intros: `важно отметить`, `следует подчеркнуть`, `в данном контексте`
- translation-like syntax: `стремимся к тому, чтобы`, `делает возможным`, `находится в процессе`
- overused connectors: `таким образом`, `кроме того`, `однако`, `следовательно`
- empty adjectives: `эффективный`, `комплексный`, `ключевой`, `актуальный`, `инновационный`, `уникальный`, `премиальный`
- universal openings: `в современном мире`, `в эпоху цифровизации`, `сегодня как никогда`
- vague authority: `исследования показывают`, `эксперты считают` without a named source
- too-even paragraphs and too-smooth logic
- punctuation drama: too many dashes, colons, or ellipses
- English calques in Russian copy, business, or academic prose
- English construct labels embedded in Russian grammar without a reason
- hybrid compounds such as `fashion-сегмент`, `apparel/fashion-контекст`, or `sportswear-категория`
- calqued modifiers such as `товарный контент`, `платформенные сигналы`, `размерные рекомендации`
- case government after rewriting
- over-humanization into slang, jokes, fake intimacy, or unsupported examples

If the Russian gate fails:

1. Restore actor and verb where possible.
2. Replace noun chains with actions unless they are terms of art.
3. Remove officialese outside legal, regulatory, technical, academic-conventional, or institutional contexts.
4. Preserve scientific/legal/academic terminology when precision matters.
5. Replace empty adjectives with mechanisms, proof, or narrower wording.
6. Translate or explain English-source terms when Russian academic prose requires it.
7. Re-check cases, agreement, and caveats after rewriting.

## Translationese Gate

Use this gate especially for Russian academic, business, and expert texts based on English sources, machine translation, bilingual notes, source matrices, or literature reviews.

Check:

- English terms appear in Russian sentences only when justified: proper names, model/protocol abbreviations, first-definition originals, source titles, code, direct quotes, formulas, or citations.
- Stable constructs are translated consistently: `purchase intention` -> `намерение покупки`, `perceived risk` -> `воспринимаемый риск`, `engagement` -> `вовлеченность`.
- Narrow constructs are explained rather than fake-Russified: `product diagnosticity` -> `достаточность информации о товаре для его оценки`.
- English list glue is gone: no `UGC and AR/VTO`, `trust and perceived risk`, `fit, size, material and comfort` inside Russian syntax.
- Hybrid compounds are resolved: `fashion-сегмент` -> `сегмент модной одежды`, `sportswear context` -> `контекст спортивной одежды`.
- Calqued adjective chains are checked: `товарное описание`, `товарная презентация`, `платформенные сигналы`, `контентные решения`, `размерные рекомендации`.
- Source-base wording is checked: avoid `корпус источников`, `корпус научных работ`, `корпус публикаций`, or `корпус литературы` unless the method really uses a linguistic/text corpus. Prefer `источниковая база`, `база источников`, `массив публикаций`, `выборка публикаций`, or `рассмотренные исследования`.
- Sentence structure is genuinely Russian, not a literal English relative-clause or noun-stack pattern.
- English-shaped association formulas are reviewed: `X связан с Y через Z`, `X выступает драйвером Y`, `X влияет на Y посредством Z`, `X делает возможным для потребителя Y`.
- Repeated hedge chains are compressed without changing evidence strength: `может быть связан`, `может способствовать`, `может оказывать влияние`.
- Project glossary or termbank decisions override generic preferences.
- If no project glossary exists, `references/languages/russian-termbank.md` governs common English-source terms.
- Internal source labels, spreadsheet categories, and search keywords did not leak into the final text.

If the gate fails:

1. Classify each English term as preserve, translate, explain once, or keep internal.
2. Replace unjustified English islands with Russian terms.
3. Rebuild sentences in Russian rather than swapping words one by one.
4. Keep original English only at first definition when it prevents ambiguity.
5. Re-check that citations, caveats, and causal claims still match the source.

## Diagnostic Output Gate

Use this gate when the user asks for an audit, diagnosis, quality review, issue map, or pre-rewrite inspection.

The diagnostic output should include:

- categorized findings, not a full rewrite by default
- short quoted fragments or precise locators
- priority labels: `P1` meaning/evidence risk, `P2` major term/style risk, `P3` polish
- safe fix patterns, not unsupported new claims
- a separate note when the problem is uncertainty rather than an error

For Russian text, use categories when relevant:

- `Terminology`
- `Translationese`
- `Register`
- `Evidence and claims`
- `Syntax and readability`
- `Structure`
- `Voice preservation`

If there are no substantive issues, say that clearly and mention residual risks such as missing sources or untested glossary decisions.

## English Gate

For English texts, check especially:

- formulaic openings: `In today's fast-paced world`, `Let's dive in`, `Here's what you need to know`
- symmetric rhetoric: `not just X, but Y`, `at its core`, `stands as a testament`
- significance inflation: `pivotal`, `transformative`, `game-changing`, `unprecedented`
- corporate buzzwords: `seamless`, `unlock`, `elevate`, `leverage`, `drive value`
- vague authority without a source: `studies show`, `experts agree`, `users report`
- generic AI vocabulary clusters: `delve`, `landscape`, `underscore`, `foster`, `showcase`
- em dash overuse
- tidy three-item lists without a reason
- mechanical title-case headings or bold-label bullets
- generic positive conclusions
- invented specificity
- register drift
- over-humanization into fake anecdotes, fake first-person experience, slang, or unsupported examples

If the English gate fails:

1. Start with the real point, not a generic setup.
2. Replace buzzwords and vague abstractions with mechanisms, evidence, or concrete outcomes.
3. Remove unsupported claims or mark them with placeholders.
4. Vary sentence rhythm without making the prose theatrical.
5. Keep formal, technical, legal, academic, or business terms when they are accurate and expected.

## Genre Gates

### Academic

Check:

- thesis, research question, argument, method, and limits are explicit where relevant
- sources are real, provided/retrieved, or marked as placeholders
- no invented authors, titles, journals, DOIs, sample sizes, statistics, dates, quotes, or page numbers
- citation style is consistent with the user request: ГОСТ, APA, MLA, IEEE, Chicago, or custom
- claims are cautious: no unsupported certainty, no fake consensus, no `research proves` without evidence
- terms stay stable; no synonym cycling of core concepts
- paragraphs perform clear academic functions: claim, evidence, analysis, method, limitation, transition
- conclusions stay within the evidence
- RU/EN academic conventions are not mixed

If it fails:

- add source placeholders instead of fake references
- narrow claims to match evidence
- add hedging where evidence is limited
- separate cited claims from the agent's analysis
- remove pseudo-academic filler, motivational language, journalistic flourish, or prompt-language contamination
- flag logical, numerical, or category errors that cannot be fixed from the provided material

### Business / Professional

Check:

- the answer, ask, recommendation, or status appears near the top
- action, owner, consequence, deliverable, and deadline are clear where relevant and provided
- the document type is correct: email, memo, executive summary, report, proposal, meeting notes, status update, or presentation script
- the reader can act after reading
- tone fits the relationship, power dynamic, and sensitivity of the message
- no decorative rhetoric, inflated importance, bureaucratic filler, vague alignment language, or empty politeness
- jargon and канцелярит are removed unless required by legal/regulatory/institutional context
- uncertainty, risk, and missing information are stated honestly

If it fails:

- move the conclusion upward
- replace politeness fog with a clear ask
- replace jargon with actor/action/outcome
- add missing owner/date/action only if provided, otherwise mark as placeholder
- cut anything that does not reduce reader effort
- adapt structure to document type

### Essay / Publicistic

Check:

- the thesis, central pressure, or argument is visible
- the piece has a real point of view when the genre asks for one
- examples and turns of thought are specific
- each section moves the argument forward
- the text does not flatten voice into neutral overview
- the text does not create false balance unless the assignment genuinely asks for comparison
- the ending lands on a concrete idea, image, implication, or question, not a slogan

If it fails:

- replace generic setup with a tension, claim, scene, or question
- remove false balance unless the piece truly compares positions
- add a turn, complication, or consequence
- preserve authorial voice rather than flattening it into neutral explainer prose
- remove unsupported broad claims or mark them with placeholders

### Copywriting

Check:

- audience, pain/desire, offer, objections, proof, and CTA are aligned
- no fake guarantees, fake urgency, fake scarcity, fake social proof, or unprovided claims
- benefits are concrete and connected to user-provided product facts
- every major benefit has a mechanism, proof, or clear use case
- the CTA names one clear action and fits funnel stage
- the copy does not rely on buzzwords as persuasion
- regulated claims are conservative and marked for approval where needed

If it fails:

- replace hype with mechanism or proof
- mark missing proof as `[proof needed]` or `[нужно подтверждение]`
- remove unsupported superlatives
- make the CTA specific and natural
- remove fake testimonials, fake numbers, fake urgency, or fake guarantees

### Creative Prose

Check:

- POV is consistent
- something changes in the scene or fragment
- emotion is carried through action, image, dialogue, rhythm, and subtext
- dialogue does not explain what the scene already shows
- dialogue has subtext, pressure, evasion, or conflict
- sensory detail is specific and narratively useful
- exposition does not break a pressure moment
- the prose avoids generic literary metaphors, stock gestures, and therapy-note explanations
- character voice remains distinct
- revision preserves authorial voice rather than over-smoothing it

If it fails:

- enter closer to a moment
- replace emotion labels with behavior, perception, or choice
- remove stock gestures unless character-specific
- add pressure, desire, obstacle, or shift
- restore roughness or asymmetry when it belongs to the voice
- stop when the scene's work is done

## Evaluation Gate

When the user asks to test, validate, benchmark, or compare the skill, use `references/process/evaluation-prompts.md`.

A regression test passes only if the output:

- routes to the correct language and genre
- asks clarifying questions only when needed
- avoids unsupported facts and fake proof
- preserves meaning and voice during rewrites
- removes major Russian and English LLM artifacts
- handles academic, business, essay/publicistic, copywriting, and creative prose as distinct genres
- keeps mixed-language outputs separate by language rules
- avoids over-polishing and unsupported personalization

## Final Output Protocol

Return the final text only unless the user requested outline, critique, rationale, variants, or process notes. If essential assumptions were made and the user did not ask for final-only output, add one short `Assumptions:` line before the text.

Do not expose the quality-gate checklist unless the user asks to see the review.
