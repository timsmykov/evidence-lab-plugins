# Academic Writing

Use for essays, reports, рефераты, доклады, курсовые, ВКР, theses, dissertations, literature reviews, scientific articles, research proposals, and research-based sections.

## Core Goal

Write academically useful prose: evidence-based, logically structured, appropriately cautious, and clear. Do not imitate academic style through inflated abstractions, fake citations, fabricated consensus, or pseudo-scholarly vocabulary. Academic writing is not formal-sounding prose; it is disciplined reasoning supported by sources.

## Source Discipline

Academic writing must not invent sources.

- If sources are provided, use only those sources.
- If sources are missing, write an outline, argument map, or draft with placeholders.
- Use `[источник]`, `[citation needed]`, `[данные исследования]`, `[source: author/year]`, or `[Source: ____]` where evidence is required.
- Do not fabricate author names, article titles, journals, DOI, statistics, sample sizes, dates, quotes, page numbers, or consensus.
- Do not cite a source unless it was provided, retrieved, or confidently known and verifiable in the current environment.
- If a user asks for claims that require evidence but provides none, mark the claim as needing verification instead of presenting it as fact.

Default warning for missing sources:

> Draft below uses source placeholders. Replace them with real sources before submission.

Russian version:

> Ниже черновик со вставками `[источник]`; перед сдачей их нужно заменить реальными источниками.

## Brief Fields

Resolve:

- discipline and subfield
- exact topic
- assignment type
- required language
- required length
- citation style: ГОСТ, APA, MLA, IEEE, Chicago, or custom
- source materials and whether they are mandatory or optional
- thesis, research question, hypothesis, or problem statement
- required sections
- institution-specific constraints
- level: school, undergraduate, graduate, professional, journal article
- whether the user wants outline, draft, critique, or final text

## Academic LLM Failure Modes

### AC-1. Fabricated references

LLMs often invent full-looking references: author names, titles, journals, DOIs, dates, page ranges, and URLs.

Rule:

- Never create a bibliographic item from memory unless the source was supplied or verified.
- Use placeholders when a citation is needed.
- If asked to format provided sources, format only the provided data and mark missing fields.

Bad:

- `Smith, J. (2021). AI and Learning. Journal of Digital Pedagogy, 14(2), 55-72.` when no such source was provided.

Better:

- `[Author, Year] argues that [claim].`
- `A source is needed here to support the claim that [claim].`

### AC-2. Unsupported or overgeneralized claims

Weak patterns:

- `research proves`
- `it is widely known`
- `all scholars agree`
- `безусловно доказано`
- `исследования однозначно подтверждают`

Rule: claims must be narrower than evidence. Use hedging where evidence is limited.

Useful hedges:

- English: `may`, `appears to`, `suggests`, `is associated with`, `preliminary evidence`, `within the available data`
- Russian: `может указывать`, `вероятно`, `по имеющимся данным`, `позволяет предположить`, `в рамках рассмотренных источников`

### AC-3. Pseudo-academic style

AI may sound academic by using heavy words while saying little.

Weak patterns:

- `This phenomenon represents a complex and multifaceted issue of great relevance.`
- `Данная проблема является актуальной и представляет собой комплексный феномен.`

Rule: replace abstract importance with topic, scope, mechanism, and evidence need.

Better:

- `The paper examines how [factor] affects [outcome] in [context].`
- `В работе анализируется, как [фактор] связан с [результат] в [контекст].`

### AC-4. Prompt-language contamination

AI may reuse metaphors, emotional words, or informal phrasing from the prompt inside academic prose.

Rule: remove subjective or colloquial language unless the assignment explicitly permits reflective writing.

Watch for:

- `regrettably`, `fortunately`, `obviously`, `heart of the issue`
- `к сожалению`, `очевидно`, `важнейший`, `болевая точка`

### AC-5. Logic and category errors

Academic drafts must check internal logic.

Watch for:

- overlapping categories presented as separate
- percentages that do not add up
- claims that contradict earlier definitions
- methods that do not answer the research question
- conclusions that exceed the data
- orphaned headings or inconsistent numbering

Rule: if a logical or numerical problem cannot be fixed from the provided material, flag it.

### AC-6. Repetition and filler

AI academic prose often repeats the same claim in different formal wording.

Rule:

- each paragraph should add a claim, evidence, analysis, method, limitation, or transition
- remove duplicate thesis restatements
- do not pad with `relevance`, `importance`, or `complexity` language

### AC-7. Lack of original argument

AI tends to produce safe summaries.

Rule: when the genre requires argument, produce a thesis, distinction, framework, or research question — not just topic coverage.

Do not invent originality. Build it from the provided materials, a clear conceptual distinction, or a cautious proposed angle.

## Genre Shapes

### Essay

- Introduction: problem, context, thesis.
- Body: 2-4 arguments; each has claim, evidence, analysis.
- Counterargument when relevant.
- Conclusion: answer the thesis without motivational flourish.

Avoid generic hooks such as `In today's world` or `В современном мире`.

### Реферат / доклад

- Титульный блок if requested.
- Содержание if long.
- Введение: актуальность, цель, задачи.
- Основная часть by subtopic.
- Заключение.
- Список источников.

Keep formulaic university requirements if the assignment demands them, but make prose as clear as the format allows.

### Курсовая / ВКР

- Введение: актуальность, степень разработанности, цель, задачи, объект, предмет, методы, база исследования, структура работы.
- Chapter 1: theory and literature.
- Chapter 2: analysis or empirical material.
- Chapter 3: recommendations/practice, if required.
- Заключение.
- Список источников.
- Приложения, if needed.

Do not invent object, subject, methods, or empirical base if not provided. Propose placeholders.

### Thesis / dissertation section

- Define the exact function of the section: theory, literature, method, results, discussion, limitations.
- Keep terms stable.
- Avoid journalistic claims.
- Use cautious links between evidence and conclusion.

### Scientific article

- Abstract.
- Keywords.
- Introduction.
- Literature/context.
- Methods.
- Results.
- Discussion.
- Limitations.
- Conclusion.
- References.

Do not report methods/results that were not provided.

### Literature review

- Organize by theme, method, debate, chronology, or theory — not by source summary only.
- Compare sources rather than listing them.
- Mark gaps and limits.
- Do not fabricate consensus.

## Citation Policy

Use the citation style requested by the user or required by the discipline/institution. If no style is specified, ask when it materially matters; otherwise use placeholders and keep style consistent.

### GOST / Russian academic contexts

Use when the user requests ГОСТ or a Russian institution likely expects it.

- In-text references commonly use numbered brackets: `[1]`, `[1, с. 45]`.
- References are listed in a numbered bibliography.
- Preserve Cyrillic titles, publication data, and access dates if provided.
- Do not invent missing bibliographic fields.

Placeholder examples:

- `В исследовании [1] показано, что...`
- `...что требует дополнительной проверки [источник].`

### APA

Common in social sciences, education, psychology, and business research.

- In-text: `(Smith, 2023)` or `Smith (2023)`.
- Page where needed: `(Smith, 2023, p. 45)`.
- Reference list alphabetized by author.

Use only with real/provided sources.

### MLA

Common in humanities.

- In-text: `(Smith 45)`.
- Works Cited list.

### IEEE

Common in engineering and computer science.

- In-text numeric citations: `[1]`, `[2]`.
- References ordered by first appearance.

### Chicago / custom styles

Follow user-provided requirements. If fields are missing, mark them.

## RU vs EN Academic Conventions

### Russian academic writing

- Usually avoids first person singular.
- Often uses impersonal constructions: `в работе рассматривается`, `анализируются`, `показано`.
- Can use formal section formulas in реферат/ВКР contexts.
- Should still avoid unnecessary канцелярит and empty relevance claims.
- May place emphasis later in the sentence; do not force English subject-first rhythm.
- Use `автор`, `исследователь`, or impersonal phrasing when appropriate.

Good:

- `В работе анализируются причины...`
- `Полученные данные позволяют предположить...`

Weak:

- `Данная работа является крайне актуальной в условиях современного мира.`

### Russian academic writing from English-language sources

Russian dissertations, theses, literature reviews, and articles often rely on English-language research. Do not let the source language define the final Russian style.

Core rule:

- preserve the concept and citation;
- normalize the term for Russian academic prose;
- keep the English original only when it is needed for precision, first-definition alignment, or bibliography/source identification.

Use this sequence before finalizing:

1. Identify English construct labels, abbreviations, hybrid words, and literal calques.
2. Check project glossary or termbank first.
3. Decide whether each term is preserved, translated, explained once, or kept only in internal notes.
4. Rebuild the sentence in Russian syntax instead of translating word by word.
5. Re-check that citations still support the claim.

Typical fixes:

| Source-shaped phrase | Academic Russian |
|---|---|
| `purchase intention` | `намерение покупки` / `готовность купить` |
| `engagement` | `вовлеченность` / `взаимодействие с контентом` |
| `return behavior` | `решения о возврате товара` / `частота возвратов` |
| `return-related outcomes` | `результаты, связанные с возвратами` |
| `product diagnosticity` | `достаточность информации о товаре для его оценки` |
| `fit uncertainty` | `трудности с оценкой посадки` |
| `fit tools` | `инструменты подбора и оценки размера` |
| `size guides` | `таблицы размеров` / `рекомендации по выбору размера` |
| `user-generated content`, `UGC` | `пользовательский контент` |
| `eWOM` | `электронное сарафанное радио`, if the project glossary requires Russian wording |
| `virtual try-on`, `VTO` | `виртуальная примерка` |

Do not over-Russify:

- keep author names in original spelling in author-year citations;
- keep established protocol/model abbreviations such as `PRISMA`, `TAM`, `TPB`, `S-O-R`;
- keep exact source titles in bibliography and when discussing a paper title;
- preserve technical abbreviations when Russian alternatives would be less precise.

Bad:

> `В fashion-сегменте product diagnosticity влияет на purchase intention через trust and perceived risk.`

Better:

> `В сегменте модной одежды информация о товаре влияет на намерение покупки через доверие и воспринимаемый риск, если помогает покупателю оценить товар до физического контакта.`

If a construct has no stable Russian equivalent, explain it. A clear explanatory phrase is better than a pseudo-term.

### English academic writing

- Often leads with the subject, claim, or research action.
- Can use first person plural in many fields: `we examine`, `we argue`, `we find`, depending on discipline.
- Uses explicit hedging and clear paragraph claims.
- Avoids grand claims without evidence.
- Prefers concise formal prose over inflated formality.

Good:

- `This paper examines...`
- `The findings suggest...`

Weak:

- `In today's globalized world, it is well known that...`

## Writing Rules

- Claims must be narrower than evidence.
- Use cautious language for uncertain findings.
- Separate the agent's analysis from cited claims.
- Keep terms stable; do not synonym-cycle core concepts.
- Define key terms once, then use them consistently.
- Make paragraph function visible: claim, evidence, analysis, limitation, transition.
- Avoid `актуальность темы обусловлена...` unless the assignment requires that formula.
- Avoid empty phrases: `имеет важное значение`, `играет ключевую роль`, `is highly relevant`, `plays a crucial role` without specifying how.
- Do not add data, methods, results, or literature that the user did not provide.

## Examples

| Weak / AI-like | Stronger | Why |
|---|---|---|
| `In today's globalized world, it is well-known that climate change has bad effects.` | `This section examines how rising temperatures affect crop yields in [region], using evidence from [source].` | Narrows scope and marks source need. |
| `Данная работа рассматривает проблему, которая очень актуальна в современном мире.` | `В работе анализируются причины [явление] в [контекст] и сравниваются подходы [A] и [B].` | Replaces generic relevance with research action. |
| `Research proves that online learning is effective.` | `Existing studies suggest that online learning can be effective under specific conditions, including [condition] and [source].` | Adds caution and conditions. |
| `Учёные доказали, что метод повышает эффективность на 30%.` | `Утверждение о росте эффективности на 30% требует источника: [источник].` | Prevents fake data. |
| `This paper will delve into the multifaceted nature of leadership.` | `This paper compares two approaches to leadership: [A] and [B].` | Removes pseudo-academic language. |
| `Автор считает, что это, безусловно, лучший подход.` | `В рамках рассмотренных источников этот подход имеет два преимущества: [A] и [B].` | Removes subjective overstatement. |

## Output Patterns

### Missing sources

Use a short caveat and placeholders.

English:

> Draft below uses citation placeholders. Replace them with real sources before submission.

Russian:

> Ниже черновик со вставками `[источник]`; перед сдачей их нужно заменить реальными источниками.

Then write the draft.

### User asks for citations but gives no sources

Do not fabricate references. Provide:

- a source-needed outline
- a draft with placeholders
- a suggested search plan
- a list of source types needed

### User provides sources

- Use only provided sources.
- Keep claims attached to the right source.
- Do not attribute a source's claim to another source.
- Preserve page numbers and quotes if provided.

## Quality Check

Before finalizing:

1. Are all factual claims sourced, common/non-controversial, or marked with placeholders?
2. Are there any invented citations, titles, authors, DOIs, journals, dates, statistics, or quotes?
3. Is the thesis or research question clear?
4. Does each paragraph perform a specific academic function?
5. Are claims appropriately hedged?
6. Do conclusions stay within the evidence?
7. Are terms stable and definitions consistent?
8. Is the citation style consistent with the user's request?
9. Are Russian and English academic conventions handled separately?
10. Did the text avoid pseudo-academic filler while preserving formal register?
