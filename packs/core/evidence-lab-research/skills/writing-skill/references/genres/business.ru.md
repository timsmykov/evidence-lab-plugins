# Business and Professional Writing

Use for emails, memos, reports, proposals, executive summaries, meeting notes, status updates, instructions, decision briefs, presentation scripts, client communications, and internal documentation.

## Core Goal

Business writing should reduce work for the reader. It should make the point clear, support it with the right facts, and tell the reader what happens next. Professional does not mean vague, inflated, bureaucratic, or bland.

A strong business text answers:

- What happened?
- Why does it matter?
- What decision or action is needed?
- Who owns it?
- By when?
- What evidence or constraint matters?

## Brief Fields

Resolve:

- sender/role
- recipient/audience
- relationship and power dynamic
- goal: inform, request, decide, persuade, update, escalate, summarize, propose
- decision or action needed
- context the reader already knows
- facts, numbers, links, names, dates
- constraints: tone, length, format, deadline, confidentiality
- channel: email, memo, report, executive summary, proposal, presentation script, chat message
- language: Russian, English, or both
- whether the output needs to be final text, outline, critique, or rewrite

## Core Principles

- Front-load the point.
- Use active verbs when the actor matters.
- Use short paragraphs.
- Prefer concrete nouns, owners, dates, and actions.
- Use bullets only when they reduce reading effort.
- Keep tone confident, courteous, and sincere.
- Remove corporate filler, decorative seriousness, and fake professionalism.
- Do not add facts, commitments, metrics, promises, or deadlines that were not provided.

## Common LLM Business Failure Modes

### BW-1. Verbosity and filler

Weak patterns:

- `It is important to note that...`
- `In today's business environment...`
- `At this point in time...`
- `We would like to take this opportunity to...`
- `В рамках данного процесса...`
- `На сегодняшний день...`
- `Следует отметить, что...`

Fix: start with the actual point, decision, status, or ask.

Example:

- Weak: `It is important to note that the project is currently experiencing delays.`
- Better: `The project is delayed by two weeks.`

### BW-2. Vague corporate jargon

Watch for:

- English: `leverage synergies`, `strategic initiative`, `drive alignment`, `operationalize`, `paradigm shift`, `core competencies`, `stakeholder engagement`, `value creation`
- Russian: `осуществить мероприятия`, `представляется целесообразным`, `данный процесс`, `повышение эффективности взаимодействия`, `реализация инициатив`, `обеспечение контроля`

Fix: replace jargon with actor + action + outcome.

Example:

- Weak: `We will leverage synergies to operationalize the strategy.`
- Better: `Sales and support will use the same account notes starting Monday.`

### BW-3. Generic politeness

AI often hides the real ask behind softening phrases.

Weak patterns:

- `We appreciate your continued efforts and would like to kindly request...`
- `If it is not too much trouble...`
- `К сожалению, вынуждены сообщить...` when a direct factual update is enough
- `Просим рассмотреть возможность...` when the request is clear

Fix: be courteous but direct.

Example:

- Weak: `We would like to kindly ask whether you might be able to send the file.`
- Better: `Please send the file by 15:00 today so we can include it in the client deck.`

### BW-4. Excessive structure

AI may turn simple messages into mini-reports with headings, bullets, and formal sections.

Fix:

- use a paragraph for simple messages
- use bullets for options, next steps, risks, dates, or owners
- use headings only when the reader benefits from scanning

### BW-5. Empty action items

Weak patterns:

- `Align on next steps`
- `Continue monitoring the situation`
- `Ensure effective communication`
- `Обеспечить контроль исполнения`

Fix: specify owner, action, deadline, and deliverable when known.

Example:

- Weak: `We need to align on next steps.`
- Better: `Anna will send the revised scope by Thursday; Mark will confirm budget by Friday.`

### BW-6. Fake certainty and unsupported business claims

Do not invent:

- growth percentages
- customer impact
- implementation timelines
- cost savings
- market claims
- legal/compliance conclusions
- executive decisions

Fix: use provided facts or mark placeholders.

Examples:

- `This should reduce costs by [estimate/source needed].`
- `По текущим данным, задержка составляет [срок].`

### BW-7. Register drift

Common drift:

- email -> policy memo
- executive summary -> marketing copy
- proposal -> generic company brochure
- status update -> inspirational leadership note
- Russian business note -> bureaucratic officialese
- English memo -> buzzword-heavy corporate speak

Fix: match document type, audience, and relationship.

## Document Types

### Email

Use for direct communication with a clear purpose.

Structure:

- subject line if requested
- greeting
- main point in the first 1-2 sentences
- necessary context
- specific ask or next step
- sign-off

Rules:

- one main purpose per email when possible
- keep the ask visible
- include deadline and reason if provided
- avoid long throat-clearing

### Internal memo / decision note

Use when the reader needs context and a recommendation.

Structure:

- summary
- context
- options or findings
- recommendation
- risks / tradeoffs
- next steps

Rules:

- write for a busy internal reader
- assume some shared context, but define what matters
- separate facts from recommendation

### Executive summary

Use when senior readers need the answer without reading the full report.

Structure:

- one-paragraph overview or bullets
- key findings
- recommendation / decision needed
- risks or constraints
- next step

Rules:

- no long background
- no methodology detail unless it changes confidence
- should stand alone

### Report

Use for analysis, findings, and recommendations.

Structure:

- executive summary
- scope and method
- findings
- implications
- recommendations
- appendix/details if needed

Rules:

- show evidence for claims
- define scope and limitations
- make recommendations actionable

### Proposal

Use to persuade a reader to approve a project, service, plan, or investment.

Structure:

- problem / opportunity
- proposed solution
- benefits or outcomes
- scope
- timeline
- cost / resources if provided
- risks
- next step

Rules:

- do not invent ROI, timeline, or feasibility
- connect benefits to provided evidence
- avoid marketing fluff unless the proposal is explicitly commercial

### Meeting notes

Use to preserve decisions and next actions.

Structure:

- date / meeting title if requested
- attendees if provided
- decisions
- action items: owner + task + deadline
- open questions

Rules:

- do not turn discussion into decisions unless the user says they were decided
- mark unknown owners/deadlines as placeholders

### Status update

Use for progress communication.

Structure:

- status: on track / at risk / blocked / done
- progress since last update
- risks or blockers
- next steps
- asks from reader

Rules:

- be honest about risk
- do not hide blockers behind positive language

### Presentation script

Use for speaker notes or talk tracks.

Structure:

- slide purpose
- spoken key message
- supporting point
- transition to next slide

Rules:

- short spoken sentences
- no dense report prose
- avoid reading every bullet verbatim

## Russian Business Notes

Russian business writing easily drifts into канцелярит. Avoid unless the audience explicitly expects official/regulatory style.

Watch for:

- `данный`, `указанный`, `настоящий` outside legal/procedural precision
- `необходимо осуществить`
- `представляется целесообразным`
- `в рамках реализации мероприятий`
- `обеспечить контроль`
- `имеет место`
- `надлежит`
- `поставить на контроль` when plain wording is possible

Prefer:

- direct verbs
- clear owner/action/deadline
- `этот` instead of `данный` in ordinary business prose
- `нужно`, `стоит`, `рекомендуем`, `сделаем`, `проверим` depending on tone

Examples:

- Weak: `В рамках реализации проекта необходимо осуществить назначение ответственных.`
- Better: `Для проекта нужно назначить ответственных.`
- Better with facts: `До пятницы назначим ответственных за три блока: интеграция, обучение, поддержка.`

## English Business Notes

English business writing should be clear, concise, courteous, and concrete.

Avoid:

- `leverage`, `synergy`, `operationalize`, `paradigm shift`, `best practice`, `strategic alignment` when they hide meaning
- generic `In today's business environment` openings
- over-softened asks
- passive voice when the actor matters
- robotic `professional tone`

Prefer:

- subject + active verb + object
- specific next step
- plain language
- sincere politeness
- reader benefit or reason for action

Examples:

- Weak: `We are proactively leveraging our core competencies to drive a paradigm shift.`
- Better: `We are moving support triage into Zendesk so product managers can see customer issues without a separate weekly report.`

## Tone Calibration

Professional tone is not one tone. Choose based on relationship and situation.

### Direct internal

- short
- action-oriented
- low ceremony
- suitable for colleagues with shared context

### Client-facing

- courteous
- clear
- avoids blame
- gives context and next step

### Executive

- concise
- answer first
- explicit recommendation or decision needed
- risks named clearly

### Sensitive / negative news

- direct but not blunt
- acknowledges impact
- avoids evasive euphemisms
- proposes next step when possible

### Formal / regulatory

- more precise and impersonal
- may preserve official terms
- avoids casual phrasing
- still removes needless redundancy

## The 7 C's as a Business Check

Use these as a quick diagnostic:

- **Clear** — the reader understands the point.
- **Concise** — no filler or duplicated meaning.
- **Concrete** — facts, dates, owners, actions are visible.
- **Correct** — facts, names, dates, and terms are accurate.
- **Coherent** — ideas appear in useful order.
- **Complete** — the reader has what they need to act.
- **Courteous** — tone fits the relationship and situation.

Do not make the text longer just to satisfy these checks.

## Examples

| Weak / AI-like | Stronger | Why |
|---|---|---|
| `Currently, we are proactively leveraging our core competencies to drive a paradigm shift in market synergy.` | `Q3 sales rose 12% after we shortened shipment time. Next, we will launch the new logistics plan in August and track progress weekly.` | Replaces jargon with facts, plan, and metric. |
| `В ходе реализации проекта необходимо осуществить значительное количество мероприятий, представляется целесообразным назначить ответственных.` | `Для проекта нужно назначить ответственных и зафиксировать три ближайших шага: обследование системы, модернизация оборудования, обучение команды.` | Removes канцелярит and clarifies action. |
| `We would like to kindly request that you send the materials at your earliest convenience.` | `Please send the materials by Thursday so we can include them in the client review.` | Clear ask + deadline + reason. |
| `Следует обеспечить эффективное взаимодействие подразделений.` | `Маркетинг и продажи будут обновлять общий план каждый вторник до 12:00.` | Turns abstract coordination into action. |
| `The situation is being monitored.` | `Nina is checking the incident queue every hour and will send an update at 17:00.` | Restores owner and next update. |
| `Просим рассмотреть возможность переноса встречи.` | `Предлагаю перенести встречу на четверг: к этому времени будут готовы расчёты.` | More direct and useful. |

## AI Editing Rules for Business Text

When editing AI-generated business text:

1. Move the main point upward.
2. Replace jargon with specific actions or facts.
3. Remove ceremonial politeness that hides the ask.
4. Restore owners, dates, deliverables, and decisions when provided.
5. Mark missing owners/dates as placeholders instead of inventing them.
6. Cut generic context paragraphs.
7. Keep tone suitable for the relationship.
8. Preserve legal/regulatory terms when required.

## Quality Check

Before finalizing:

1. Is the ask, answer, recommendation, or status visible near the top?
2. Are dates, owners, and next steps concrete when needed?
3. Did any claim exceed the provided facts?
4. Is the tone suitable for the relationship and power dynamic?
5. Is the text shorter and clearer than a generic AI version would be?
6. Are jargon and канцелярит removed unless required by context?
7. Does the structure match the document type?
8. Can the reader act after reading?
9. Are uncertainty, risk, or missing information stated honestly?
10. Are Russian and English business conventions handled separately?
