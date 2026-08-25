# Evaluation Prompts

Use these prompts to regression-test the writing skill. They are not part of the normal writing workflow. Use them when the user asks to test, validate, benchmark, or compare the skill.

For each test, the agent should route to the correct language and genre references, produce the requested output, and then self-check against the expected failure modes. Do not expose this file during normal user-facing writing tasks.

## How to Evaluate

For each prompt:

1. Identify task type, language, genre, audience, and source constraints.
2. Load the relevant language and genre references.
3. Draft or rewrite the output.
4. Apply `quality-gates.md`.
5. Score the result informally on:
   - source discipline
  - language-specific naturalness
  - genre fit
  - glossary/termbank handling
  - translationese removal for Russian text based on English sources
  - diagnostic audit behavior when requested
  - voice preservation
   - anti-AI artifact removal
   - meaning preservation
6. A passing answer should avoid the listed failure modes without becoming over-edited or factually richer than the prompt allows.

## Russian Language Tests

### RU-1: Bureaucratic business rewrite

Prompt:

> Перепиши текст для внутреннего письма команде. Нужно сделать его ясным, человеческим и деловым, без канцелярита, но не слишком неформально: «В рамках реализации мероприятий по повышению эффективности взаимодействия между подразделениями было принято решение о проведении регулярного мониторинга статуса выполнения задач. Данный процесс позволит обеспечить своевременное выявление проблемных зон и осуществление корректирующих действий.»

Expected routing:

- language: Russian
- genre: business/professional
- task type: rewrite/polish

Must fix:

- `в рамках реализации мероприятий`
- nominalization chains
- passive/impersonal constructions
- `данный процесс`
- `осуществление корректирующих действий`

Must preserve:

- business tone
- meaning: regular monitoring, task status, finding problems early, corrective action

Should not:

- add fake deadlines, owners, metrics, or tools
- become slangy

### RU-2: Pseudo-academic paragraph

Prompt:

> Улучши русский академический стиль, но не делай текст разговорным: «Важно отметить, что на сегодняшний день проблема цифровой трансформации является крайне актуальной и представляет собой комплексный феномен, оказывающий значительное влияние на развитие современных организаций.»

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- meta-intro
- `на сегодняшний день`
- redundant `является` / `представляет собой`
- empty adjectives unless narrowed

Must preserve:

- formal academic register
- cautious tone

Should not:

- invent citations or empirical claims
- turn into blog language

### RU-3: Russian publicistic false balance

Prompt:

> Напиши короткий публицистический абзац на русском по тезису: «ИИ в образовании полезен только там, где он усиливает учителя, а не заменяет его». Нужен живой, уверенный тон, без «с одной стороны / с другой стороны» и без мотивационного финала.

Expected routing:

- language: Russian
- genre: essay/publicistic
- task type: create from brief

Must demonstrate:

- clear stance
- no false balance
- concrete distinction between amplification and replacement
- no generic `в современном мире`

Should not:

- invent studies or statistics
- end with slogan

### RU-4: Russian copy without fake proof

Prompt:

> Сделай hero-блок лендинга на русском для сервиса, который автоматически распределяет входящие заявки между менеджерами и показывает просроченные ответы. Никаких цифр, гарантий, «уникальный», «инновационный», «лидер рынка».

Expected routing:

- language: Russian
- genre: copywriting
- task type: create from brief

Must demonstrate:

- concrete user outcome
- mechanism-based benefit
- natural CTA
- no fake proof

Should not:

- add customer counts
- claim guaranteed growth
- use pseudo-premium tone

### RU-5: Russian creative prose stock emotion

Prompt:

> Перепиши фрагмент художественной прозы на русском так, чтобы грусть была показана через действие и деталь, а не названа напрямую. Сохрани простой реалистичный стиль: «Она была очень грустна. За окном шёл дождь. В комнате стояла тишина, и сердце её сжалось от воспоминаний.»

Expected routing:

- language: Russian
- genre: creative prose
- task type: rewrite/polish

Must fix:

- emotion label
- generic rain sadness
- `тишина`, `сердце сжалось`, `воспоминания` cliché cluster

Must preserve:

- sadness
- quiet room
- realistic tone

Should not:

- become ornate or melodramatic

## Academic Writing Tests

### AC-1: Fake citation prevention

Prompt:

> Напиши академический абзац на русском о том, что использование LLM повышает продуктивность студентов на 30%. Источников у меня нет. Нужно оформить как для курсовой.

Expected routing:

- language: Russian
- genre: academic
- task type: create from brief

Must demonstrate:

- no fabricated citation
- no presentation of 30% as verified
- source placeholder or caveat
- formal academic register

Should not:

- invent author, journal, DOI, university, date, sample size, or ГОСТ entry

### AC-2: English academic overclaiming

Prompt:

> Rewrite this academic claim in careful English without adding sources: “Research proves that remote learning is always more effective than classroom learning.”

Expected routing:

- language: English
- genre: academic
- task type: rewrite/polish

Must fix:

- `Research proves`
- `always`
- unsupported causal/comparative certainty

Must demonstrate:

- hedging
- source need if evidence is required
- concise academic tone

### AC-3: Citation style discipline

Prompt:

> I have one source: Smith, John. “AI Feedback in Higher Education.” Journal of Learning Research, 2023. Write two English academic sentences using APA-style placeholder formatting. Do not invent volume, issue, pages, DOI, or findings.

Expected routing:

- language: English
- genre: academic
- task type: create from brief

Must demonstrate:

- use only provided bibliographic data
- no invented details
- APA-style in-text reference such as `(Smith, 2023)`
- cautious phrasing if no findings were provided

### AC-4: Russian thesis intro formula cleanup

Prompt:

> Улучши фрагмент введения ВКР, сохрани формальный стиль и структуру, но убери пустую псевдоакадемичность: «Актуальность темы обусловлена тем, что в современном мире цифровизация играет ключевую роль во всех сферах общественной жизни. Данная работа является попыткой комплексного рассмотрения указанной проблемы.»

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- generic relevance formula unless assignment requires it
- `в современном мире`
- `играет ключевую роль`
- `данная работа является`
- `комплексное рассмотрение указанной проблемы`

Must preserve:

- ВКР/institutional register
- introduction-like function

Should not:

- become conversational
- invent object/subject/methods unless marked as placeholders

### AC-5: Russian academic translationese cleanup

Prompt:

> Улучши русский академический стиль фрагмента ВКР. Сохрани смысл, ссылки и осторожность выводов, но убери английские кальки и термины, которые не должны оставаться в основном русском тексте: «В e-commerce perceived risk связан с purchase intention, а trust выступает механизмом, который помогает потребителю перейти к покупке. Для sportswear особенно важны fit tools, size guides, UGC and AR/VTO, поскольку они могут снижать fit uncertainty и return behavior (Phamthi et al., 2024; Balaram et al., 2022).»

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- `e-commerce`
- `perceived risk`
- `purchase intention`
- `trust`
- `sportswear`
- `fit tools`
- `size guides`
- `UGC and AR/VTO`
- `fit uncertainty`
- `return behavior`

Must preserve:

- academic register
- cautious causal language
- citations
- distinction between risk, trust, purchase intention, fit uncertainty, and returns

Reference output:

> В электронной торговле воспринимаемый риск связан с намерением покупки, а доверие может помогать потребителю принимать решение в условиях неполной информации. Для спортивной одежды особенно важны инструменты подбора и оценки размера, таблицы размеров, пользовательский контент и виртуальная примерка, поскольку они помогают снизить трудности с оценкой посадки и могут влиять на решения о возврате товара (Phamthi et al., 2024; Balaram et al., 2022).

Should not:

- invent new sources
- overstate effects
- turn the paragraph conversational
- remove needed author-year citations

### AC-6: Russian academic calqued modifiers

Prompt:

> Отредактируй фрагмент ВКР: «Товарный контент, товарная презентация и платформенные сигналы формируют диагностичность товара. Контентные решения должны включать размерные рекомендации, товарные описания и пользовательские фото.» Нужно сохранить академический стиль, но убрать кальки с английского.

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- `товарный контент`
- `товарная презентация`
- `платформенные сигналы`
- `диагностичность товара` without explanation
- `контентные решения`
- `размерные рекомендации`
- `товарные описания`

Must preserve:

- the conceptual point: content and platform/service signals help evaluate the product
- formal academic tone

Reference output:

> Контент о товаре, его визуальная презентация и сигналы платформы помогают покупателю оценить товар до покупки. Поэтому решения в области контента должны включать рекомендации по выбору размера, описания товара и пользовательские фотографии.

Should not:

- remove all terminology
- introduce unsupported claims

### AC-7: Preserve valid abbreviations while translating source labels

Prompt:

> Перепиши академический абзац на русском. Нужно убрать английские source labels, но сохранить аббревиатуры, которые в научном тексте лучше оставить: «PRISMA используется для прозрачного описания поиска источников. В модели TAM usage intention зависит от perceived usefulness, однако в тексте ВКР также рассматриваются purchase intention, engagement and eWOM.»

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- `usage intention`
- `perceived usefulness`
- `purchase intention`
- `engagement and eWOM`

Must preserve:

- `PRISMA`
- `TAM`
- the distinction between model terms and translated constructs

Reference output:

> PRISMA используется для прозрачного описания поиска источников. В модели TAM намерение использовать продукт связано с воспринимаемой полезностью; в тексте ВКР отдельно рассматриваются намерение покупки, вовлеченность и электронное сарафанное радио.

Should not:

- translate protocol/model abbreviations mechanically
- fabricate definitions beyond the given sentence

### AC-8: Russian academic source-base wording

Prompt:

> Отредактируй фрагмент ВКР: «Корпус источников исследования включает 50 научных работ. На основе данного корпуса публикаций были выделены основные подходы к анализу потребительского поведения.» Нужно сохранить академический стиль, но убрать неестественное употребление слова «корпус».

Expected routing:

- language: Russian
- genre: academic
- task type: rewrite/polish

Must fix:

- `корпус источников`
- `данный корпус публикаций`
- unnecessary `данный`
- source-base wording that sounds like a literal transfer from English academic labels

Must preserve:

- 50 scientific works
- the idea that sources/publications were used to identify approaches
- formal academic register

Reference output:

> Источниковая база исследования включает 50 научных работ. На основе рассмотренных публикаций были выделены основные подходы к анализу потребительского поведения.

Should not:

- ban `корпус` where it means a linguistic or annotated text corpus
- invent source-selection criteria
- change the number of works

### AC-9: Russian diagnostic audit before rewrite

Prompt:

> Проведи диагностику фрагмента перед переписыванием. Не переписывай весь текст, сначала дай карту проблем: «В fashion-сегменте product diagnosticity является ключевым драйвером purchase intention через trust and perceived risk. Товарный контент и платформенные сигналы позволяют потребителю перейти к покупке, снижая возвратное поведение.»

Expected routing:

- language: Russian
- genre: academic
- task type: diagnostic audit

Must diagnose:

- English islands: `fashion-сегмент`, `product diagnosticity`, `purchase intention`, `trust and perceived risk`
- calqued modifiers: `товарный контент`, `платформенные сигналы`
- overclaiming: `ключевой драйвер`, direct move to purchase
- calqued construct: `возвратное поведение`
- syntax: English-shaped formula `X is a driver of Y through Z`

Reference diagnostic shape:

> - `P2 Terminology`: `product diagnosticity`, `purchase intention`, `trust and perceived risk` are English source labels inside Russian syntax. Use Russian terms or explanatory phrases.
> - `P2 Translationese`: `fashion-сегмент`, `товарный контент`, `платформенные сигналы` are calqued forms. Prefer `сегмент модной одежды`, `контент о товаре`, `сигналы платформы`.
> - `P1 Evidence and claims`: `ключевой драйвер` and `позволяют потребителю перейти к покупке` overstate causality unless the source directly supports it. Use cautious association language.
> - `P2 Terminology`: `возвратное поведение` is a literal calque. Prefer `решения о возврате товара` or `частота возвратов`.

Should not:

- produce a full rewrite unless requested
- add sources
- treat all English abbreviations as automatically wrong

## Business Writing Tests

### BW-1: English jargon memo rewrite

Prompt:

> Rewrite this as a concise internal update for executives: “Currently, we are proactively leveraging our core competencies to drive a paradigm shift in operational synergy across stakeholder groups.” Facts available: support and sales will use the same account notes starting Monday. No metrics yet.

Expected routing:

- language: English
- genre: business/professional
- task type: rewrite/polish

Must fix:

- corporate jargon
- no clear action
- inflated importance

Must preserve/add from provided facts only:

- support and sales
- shared account notes
- starting Monday
- no metrics yet if relevant

Should not:

- invent KPIs or impact

### BW-2: Russian actionability rewrite

Prompt:

> Перепиши как короткий деловой апдейт на русском: «Следует обеспечить эффективное взаимодействие подразделений и поставить вопрос на контроль». Факты: маркетинг и продажи будут обновлять общий план каждый вторник до 12:00; ответственный — Анна.

Expected routing:

- language: Russian
- genre: business/professional
- task type: rewrite/polish

Must fix:

- `следует обеспечить`
- `эффективное взаимодействие`
- `поставить вопрос на контроль`

Must include:

- marketing and sales
- shared plan
- Tuesdays by 12:00
- Anna as owner

### BW-3: Client email tone

Prompt:

> Write a short client-facing email in English. Message: we cannot attend tomorrow’s meeting; propose rescheduling to Thursday or Friday; keep it courteous but direct. Do not over-apologize.

Expected routing:

- language: English
- genre: business/professional
- task type: create from brief

Must demonstrate:

- clear first-line purpose
- courteous direct tone
- specific alternatives
- no generic politeness fog

### BW-4: Meeting notes discipline

Prompt:

> Turn this into meeting notes: “We talked about launching in May. Sarah might own pricing, but not confirmed. The team agreed to ask legal about the terms page.” Do not turn uncertain items into decisions.

Expected routing:

- language: English
- genre: business/professional
- task type: adapt to genre

Must demonstrate:

- decisions vs open questions separated
- no invented owners/deadlines
- `Sarah might own pricing` remains uncertain
- legal terms page ask captured as agreed action if owner missing, mark owner placeholder

## English Language Tests

### EN-1: Corporate buzzword rewrite

Prompt:

> Rewrite this for a product page in clear human English. Keep it professional, but remove buzzwords and unsupported claims: “Our transformative, seamless platform empowers teams to unlock productivity and drive business value through a robust, user-friendly interface.”

Expected routing:

- language: English
- genre: copywriting
- task type: rewrite/polish

Must fix:

- `transformative`
- `seamless`
- `empowers`
- `unlock productivity`
- `drive business value`
- `robust, user-friendly interface`

Should not:

- invent product features
- add fake metrics

### EN-2: English essay generic opener

Prompt:

> Write a short English essay opening arguing that remote work did not kill office culture; it exposed which parts of office culture were weak. Avoid “In today’s fast-paced world,” “at its core,” and “not just X but Y.”

Expected routing:

- language: English
- genre: essay/publicistic
- task type: create from brief

Must demonstrate:

- clear thesis
- no generic opener
- no formulaic contrast
- concrete direction for the argument

Should not:

- create fake studies or statistics

### EN-3: English publicistic false balance

Prompt:

> Revise this paragraph so it has a clear point of view without becoming unfair: “Some people say AI writing tools are good, while others say they are bad. Both sides have valid points. In conclusion, it is important to use them responsibly.”

Expected routing:

- language: English
- genre: essay/publicistic
- task type: rewrite/polish

Must fix:

- false balance
- generic conclusion
- weak thesis

Should preserve:

- fair-mindedness
- responsible-use idea

### EN-4: English copy fake urgency

Prompt:

> Create a short email CTA for a workshop. Facts available: it is a 90-minute live workshop, attendees will leave with a draft onboarding email sequence, registration closes Friday, and seats are capped at 25. Do not add testimonials, discounts, or extra claims.

Expected routing:

- language: English
- genre: copywriting
- task type: create from brief

Must demonstrate:

- real urgency based on provided facts
- one clear CTA
- no fake proof
- no hype

### EN-5: English creative dialogue with subtext

Prompt:

> Rewrite this dialogue so it has subtext and does not state the emotion directly. Keep it contemporary and understated. “I am angry because you lied to me,” she said. “I lied because I was afraid,” he replied. “That hurt me,” she said.

Expected routing:

- language: English
- genre: creative prose
- task type: rewrite/polish

Must fix:

- on-the-nose dialogue
- direct emotion labels
- flat character voice

Should not:

- add backstory
- overdramatize

## Mixed and Process Tests

### MIX-1: Mixed-language separation

Prompt:

> Сделай две версии одного и того же тезиса: русскую и английскую. Тезис: AI writing sounds bad when it adds structure instead of thought. Русская версия должна быть публицистической, английская — как короткий blog intro. Не смешивай языковые эвристики.

Expected routing:

- output languages: Russian and English
- genre: essay/publicistic for both, with language-specific checks separately

Must demonstrate:

- Russian version does not sound translated from English
- English version does not inherit Russian канцелярит rules mechanically
- both preserve the same thesis

### MIX-2: Missing sources policy

Prompt:

> Напиши академический абзац о том, что использование LLM повышает продуктивность студентов на 30%. Источников у меня нет.

Expected routing:

- language: Russian
- genre: academic
- task type: create from brief

Must demonstrate:

- refusal to invent source or statistic support
- placeholder or caveat
- possible rewrite as claim needing verification

Should not:

- cite fake research
- present 30% as verified

### PROC-1: Clarifying vs assuming

Prompt:

> Напиши текст про наш продукт.

Expected behavior:

- ask up to three clarifying questions because product, audience, genre, facts, and goal are missing
- do not draft a generic product text

### PROC-2: Quick safe assumption

Prompt:

> Напиши короткое дружелюбное напоминание коллеге на русском: он обещал прислать файл сегодня.

Expected behavior:

- proceed without questions
- produce a short Russian business/professional message
- no need to expose workflow

### PROC-3: Anti-overediting

Prompt:

> Сделай текст чуть чище, но сохрани мой резкий стиль: «Они опять всё усложнили. Вместо нормального процесса — пять согласований и никто ни за что не отвечает.»

Expected behavior:

- preserve sharp voice
- improve clarity only lightly
- do not turn into neutral corporate memo

## Passing Standard

The skill passes if:

- it routes correctly without mixing language rules
- it asks questions only when needed
- it avoids unsupported facts and fake proof
- it preserves meaning and voice during rewrites
- it removes major LLM artifacts from Russian and English
- it removes translationese and unjustified English islands from Russian text based on English sources
- it applies glossary and termbank rules without over-Russifying valid abbreviations
- it can diagnose issues before rewriting when asked
- it handles academic, business, essay/publicistic, copywriting, and creative prose as distinct genres
- it applies quality gates without exposing internal process by default
- it avoids over-polishing and does not add personality where unsupported
