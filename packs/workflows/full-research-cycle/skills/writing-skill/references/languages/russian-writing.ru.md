# Russian Writing Reference

Use for Russian output. Russian is not English translated into Cyrillic: it has different rhythm, register boundaries, punctuation habits, syntactic defaults, and model failure modes.

## Core Goal

Write like a competent human Russian author inside the requested genre. Preserve meaning, facts, terms, evidence, and the user's intent. Make the prose natural by improving syntax, rhythm, specificity, and register — not by making it casually colloquial, factually richer, or artificially literary.

Russian quality is the priority for this skill. Treat this file as the primary language module whenever the output language is Russian.

## Operating Principles

1. **Do not optimize for AI detectors.** Optimize for readable, idiomatic, context-appropriate Russian. Detector-like markers are useful only as editorial signals.
2. **Do not rewrite mechanically.** A word such as `является`, `данный`, `таким образом`, or `в рамках` is not automatically wrong. First decide whether it is doing necessary legal, scientific, technical, or structural work.
3. **Humanization must stay inside the register.** A dissertation should not become a blog post. A client email should not become literary prose. A landing page should not become an official memo.
4. **Do not add unsupported facts.** Human-sounding prose is not allowed to invent examples, studies, numbers, expert opinions, product claims, customer outcomes, or anecdotes.
5. **Prefer concrete syntax over decorative style.** In Russian, the biggest improvement usually comes from restoring actors and verbs, shortening noun chains, removing officialese, and varying rhythm.
6. **Preserve terms.** Do not replace domain terms with everyday approximations if that changes meaning.
7. **Do not confuse precision with English residue.** If Russian prose is based on English sources, preserve concepts, not necessarily English surface forms. Translate stable constructs, explain narrow terms once, and keep source labels out of final prose unless the genre requires them.

## Russian LLM Failure Mode Taxonomy

Use this taxonomy during drafting, rewriting, and self-critique. For each pattern, ask: is this conventional and useful in the current genre, or is it just model/default officialese?

### RU-1. Мета-вводные и псевдо-важность

Weak patterns:

- `важно отметить, что`
- `стоит подчеркнуть`
- `следует отметить`
- `необходимо подчеркнуть`
- `нельзя не упомянуть`
- `очевидно, что`
- `не вызывает сомнений`
- `в данном контексте`
- `в рамках данного вопроса`

Why it sounds generated: the phrase announces importance instead of saying something important. In AI text it often appears at the start of paragraphs as filler.

Fix: start with the actual claim. Keep signposting only when it genuinely helps the reader navigate a complex academic or technical argument.

Example:

- Weak: `Важно отметить, что данная проблема имеет большое значение для бизнеса.`
- Better: `Проблема влияет на бизнес прямо: из-за неё команда теряет время на ручные согласования.`

Keep when: the phrase is part of institutional style, lecture notes, or a formal argumentative transition that cannot be removed without hurting clarity.

### RU-2. Канцелярит and nominalization chains

Watch for chains of nouns on `-ние`, `-ация`, `-ость`, especially with:

- `осуществление`
- `проведение`
- `обеспечение`
- `реализация`
- `выявление`
- `повышение`
- `организация`
- `формирование`
- `оптимизация`
- `внедрение`
- `использование`

Why it sounds generated: the sentence hides action inside nouns and makes Russian feel bureaucratic.

Fix: restore a finite verb and, when known, the actor.

Examples:

- Weak: `Проводится осуществление анализа факторов повышения эффективности.`
- Better: `Анализируем, какие факторы повышают эффективность.`
- Formal but cleaner: `В работе анализируются факторы, влияющие на эффективность.`

Keep when: the noun is a stable technical term (`моделирование`, `валидация`, `верификация`, `нормализация`) or the actor is intentionally irrelevant in scientific/reporting style.

### RU-3. Связки-заглушки

Usually interrogate:

- `является`
- `представляет собой`
- `выступает в качестве`
- `служит основой для`
- `играет роль`
- `обладает характеристиками`

Why it sounds generated: models use these as default glue instead of choosing a precise predicate.

Fix: use a dash, `это`, or a concrete verb.

Examples:

- Weak: `Эта функция является эффективной и масштабируемой.`
- Better: `Эта функция эффективна и хорошо масштабируется.`
- Weak: `Метод представляет собой инструмент анализа данных.`
- Better: `Метод помогает анализировать данные.`

Keep when: writing a strict definition, legal clause, standard, formal taxonomy, or scientific statement where the copula preserves exact classification.

### RU-4. `Данный`, `указанный`, `вышеупомянутый`, `соответствующий`

In blog, publicistic, product, copywriting, and ordinary business writing, replace with `этот`, `тот`, or remove.

Examples:

- Weak: `Данный подход позволяет решить указанную проблему.`
- Better: `Этот подход помогает решить проблему.`

Keep when: legal, regulatory, contract, procedural, or normative text needs exact cross-reference.

### RU-5. Translation-like Russian and English-shaped syntax

Watch for Russian that follows English structure rather than Russian idiom:

- `мы стремимся к тому, чтобы...`
- `это позволяет нам быть способными...`
- `находится в процессе разработки`
- `делает возможным для пользователей...`
- `имеет потенциал для того, чтобы...`
- heavy `который` chains copied from English relative clauses

Fix: replace with direct Russian phrasing.

Examples:

- Weak: `Мы стремимся к тому, чтобы улучшить качество обслуживания.`
- Better: `Мы хотим повысить качество обслуживания.`
- Weak: `Платформа делает возможным для команд управление задачами.`
- Better: `Платформа помогает командам управлять задачами.`

Keep when: the wording is a quotation, a fixed translation, or intentionally imitates a non-native voice.

### RU-6. Symmetric rhetoric

Avoid model-like formulas unless they are the user's deliberate voice:

- `не просто X, а Y`
- `не только X, но и Y`
- `не столько X, сколько Y`
- `это не про X, это про Y`
- `с одной стороны..., с другой стороны...`
- `вопрос не в том, X, а в том, Y`

Why it sounds generated: it creates a polished but empty rhetorical arc.

Fix: state the main point directly and add a concrete example, consequence, or limitation.

Keep when: the construction creates a real contrast, is part of a speech/copy rhythm, or matches an author sample.

### RU-7. Triple parallel lists

Russian model text often defaults to three balanced elements: `планирует, анализирует, корректирует`; `быстрее, точнее, надёжнее`; `стратегия, тактика, операция`.

Fix: use the natural number of items. If three are needed, make each item specific rather than rhythmically decorative.

Bad smell: three adjectives with no proof: `эффективный, гибкий и масштабируемый`.

Better: explain the mechanism: `система обрабатывает заявки без ручной сортировки и не ломается при росте очереди`.

### RU-8. ChatGPT-кальки and pseudo-academic layer

Replace when not required by domain/register:

- `в рамках` -> `в`, `при`, `во время`, `для`
- `в разрезе` -> `по`, `с точки зрения`, `для`
- `на сегодняшний день` -> `сейчас`, `сегодня`
- `в настоящее время` -> `сейчас`
- `в целях` -> `чтобы`, `для`
- `посредством` -> `через`, `с помощью`
- `имеет место быть` -> `есть`, `бывает`
- `представляется целесообразным` -> `имеет смысл`, `стоит`, `лучше`
- automatic `достаточно` as an intensifier -> remove or replace only if needed

Keep when: the phrase is part of a regulatory, methodological, official, or corporate-document convention and removing it would make the text less acceptable to its audience.

### RU-9. Драматические тире, двоеточия, многоточия

Russian prose can use dashes naturally, but AI often uses them as a universal rhythm tool.

Symptoms:

- multiple strong dashes per paragraph
- every insight framed as `X — это Y`
- dashes replacing normal syntax
- colon-led pseudo-profundity
- ellipses used for drama without narrative reason

Fix: keep only the dashes that create real syntactic clarity, contrast, or voice. Outside fiction and essays, prefer simpler sentence structure.

### RU-10. Усилители-паразиты

Remove most empty intensifiers:

- `действительно`
- `по-настоящему`
- `поистине`
- `по сути`
- `в целом`
- `в общем и целом`
- `в принципе`
- `буквально`
- `попросту`
- `крайне`
- `максимально`

Keep only when they change meaning, mark stance, preserve authorial voice, or are natural in dialogue.

### RU-11. Universal formulas

Narrow or remove:

- `в современном мире`
- `в эпоху цифровизации`
- `сегодня как никогда`
- `каждый человек`
- `любая компания`
- `в условиях глобализации`
- `в быстро меняющейся среде`

Fix: specify who, where, in what situation, and why.

Example:

- Weak: `В современном мире компаниям важно быстро адаптироваться.`
- Better: `Когда цикл продаж меняется за квартал, команде нужен способ быстро обновлять скрипты и материалы.`

### RU-12. Participial and adverbial-participial cascades

Long chains such as `анализирующий данные, полученные в ходе исследования, направленного на выявление...` make Russian sound generated and hard to parse.

Fix: split into two or three sentences. Let one sentence carry one main thought.

Keep when: the cascade is short, clear, and conventional in scientific or legal prose.

### RU-13. Безличный пассив

Watch for:

- `было принято решение`
- `осуществляется контроль`
- `проводится работа`
- `будет выполнена настройка`
- `были реализованы мероприятия`

Fix: if the actor is known and the genre allows it, restore the actor: `мы решили`, `команда проверяет`, `настроим`, `отдел внедрил`.

Keep when: the actor is unknown, irrelevant, confidential, or intentionally omitted in a scientific/reporting convention.

### RU-14. Размытые источники and empty authority

Do not write unsupported authority formulas:

- `исследования показывают`
- `эксперты считают`
- `многие специалисты отмечают`
- `по мнению аналитиков`
- `практика показывает`
- `принято считать`

Fix: name the source, use a placeholder, weaken the claim, or remove the authority frame.

Examples:

- Unsafe: `Исследования показывают, что этот метод повышает эффективность.`
- Safer: `Чтобы утверждать, что метод повышает эффективность, нужны данные или ссылка на исследование.`
- Draft placeholder: `По данным [источник], метод связан с [эффект].`

### RU-15. LinkedIn-русский and motivational endings

Avoid slogan endings:

- `Это не про X. Это про Y.`
- `Вопрос не в том, X или Y. Вопрос в том, как.`
- `Будущее уже наступило.`
- `Привычки, а не намерения.`
- `Именно поэтому важно начать уже сегодня.`

Fix: end on a concrete observation, decision, limitation, image, consequence, or next action.

### RU-16. Register drift into `too official`, `too pretty`, or `too motivational`

AI Russian often overshoots the requested tone:

- business note -> ministerial memo
- academic paragraph -> pseudo-philosophical lecture
- blog post -> motivational LinkedIn post
- copy -> premium-sounding but empty advertisement
- fiction -> foggy literary imitation

Fix: compare the draft with audience and channel. Remove the layer that does not belong.

### RU-17. Terminology traps

Do not humanize domain terms into wrong everyday words. Preserve field terms when they are meaningful:

- technical: `embedding`, `LLM`, `RAG`, `MVP`, `API`, `latency`
- scientific: `p-value`, `контрольная группа`, `валидность`, `корреляция`
- regulated: `GxP`, `SOP`, `аудит`, `верификация`, `валидация`
- academic: `объект`, `предмет`, `методология`, `операционализация`

If a term is necessary but obscure, explain it once instead of replacing it.

### RU-18. Case government after rewriting

After replacing nominalizations with verbs, check government and cases.

- Bad: `способствует развитие`
- Better: `способствует развитию`
- Often better: `помогает развивать`

Also check agreement after removing `данный`, changing passive to active, or splitting a long sentence.

### RU-19. Modal bureaucracy

Replace unnecessary modal bureaucracy:

- `необходимо провести`
- `следует обеспечить`
- `рекомендуется осуществить`
- `требуется выполнить`
- `целесообразно рассмотреть`

In instructions, use direct commands. In authored prose, restore the subject or a plain verb.

Examples:

- Weak: `Необходимо провести настройку системы.`
- Better instruction: `Настройте систему.`
- Better report: `Команда настроит систему до пятницы.`

Keep when: the text needs institutional distance, policy language, or non-personal obligation.

### RU-20. Empty universal adjectives

Interrogate broad adjectives:

- `эффективный`
- `комплексный`
- `качественный`
- `значимый`
- `актуальный`
- `релевантный`
- `ключевой`
- `важный`
- `оптимальный`
- `гибкий`
- `масштабируемый`
- `инновационный`
- `уникальный`

Fix: replace with concrete detail, mechanism, measurement, or narrower adjective. If no support exists, remove or soften.

Examples:

- Weak: `комплексное решение для эффективной работы`
- Better: `сервис собирает заявки, распределяет их между менеджерами и показывает просроченные задачи`

Keep when: the adjective is a defined evaluation criterion, quoted wording, brand language, or a term of art.

### RU-21. Over-correct logical connectors

Avoid repeated academic connectors in every paragraph:

- `таким образом`
- `кроме того`
- `однако`
- `тем не менее`
- `следовательно`
- `вместе с тем`
- `при этом`

Fix: in business, product, essay, and blog texts, often use `но`, `а`, `и`, `поэтому`, `ещё`, or no connector. In academic writing, keep signposts that carry argument logic.

### RU-22. Too-even paragraphs

Model Russian often produces equal paragraphs with the same shape: thesis -> explanation -> mini-conclusion.

Fix: vary paragraph length when the genre allows it. Combine paragraphs that repeat the same idea. Let a short paragraph carry force in essays and publicistic prose.

Keep when: writing a structured report, policy note, textbook section, or documentation where evenness helps scanning.

### RU-23. Repetition and synonym cycling

AI can fail both ways: it repeats a word accidentally, then replaces key terms with random synonyms when asked to improve style.

Fix:

- keep exact terms stable in academic, legal, technical, and product text
- remove accidental repetition of filler words
- do not synonym-cycle core concepts just to look varied

### RU-24. Over-humanization errors

Do not make Russian `more human` by adding:

- unsupported anecdotes
- imaginary examples
- jokes not requested by the user
- slang that does not fit the speaker
- extra emotion
- false intimacy with the reader
- colloquial particles in formal genres

Humanization means better Russian, not extra personality by default.

### RU-25. Translationese and English-source contamination

Russian text based on English material often fails after the obvious AI markers are removed. The remaining problem is `translationese`: Russian sentences keep English term order, argument structure, collocations, and research labels.

Watch for:

- English construct labels inside Russian syntax: `purchase intention`, `return behavior`, `product diagnosticity`, `fit tools`
- English connectors inside Russian lists: `UGC and AR/VTO`, `trust and perceived risk`
- hybrid compounds: `fashion-сегмент`, `apparel/fashion-контекст`, `sportswear-категория`
- literal research phrases: `готов перейти к покупке`, `возвратное поведение`, `драйверы намерения покупки`
- English noun-stack logic: `качество информации товара`, `решение покупательского риска`, `результаты возвратного поведения`
- overuse of abstract nouns because the English source uses nominal style

Fix by preserving the concept and rebuilding the Russian sentence.

Examples:

- Weak: `В e-commerce perceived risk связан с purchase intention.`
- Better: `В электронной торговле воспринимаемый риск связан с намерением покупки.`
- Weak: `UGC and AR/VTO могут снижать return behavior.`
- Better: `Пользовательский контент и виртуальная примерка могут влиять на решения о возврате товара.`
- Weak: `В fashion-сегменте product diagnosticity повышает confidence in fit.`
- Better: `В сегменте модной одежды достаточная информация о товаре помогает покупателю увереннее оценить посадку.`

Keep English only when it is a proper name, source title, model/protocol abbreviation, citation, code/API term, or a construct being defined for the first time.

### RU-25a. English-shaped syntax in Russian sentences

Do not fix translationese only by replacing English words. Rebuild the sentence when its logic is English-shaped.

Watch for these patterns:

- `X связан с Y через Z` repeated as a default translation of `X is associated with Y through Z`
- `X выступает драйвером Y`
- `X влияет на Y посредством Z`
- `X делает возможным для потребителя Y`
- `X позволяет быть способным Y`
- `потребитель воспринимает покупку как рискованную и готов перейти к покупке`
- long chains of `который/которая/которые`, copied from English relative clauses
- noun stacks translated as Russian noun stacks: `качество информации товара`, `механизм снижения риска возврата`, `форматы презентации продукта`
- repeated hedge stacks: `может быть связан`, `может способствовать`, `может оказывать влияние` in adjacent sentences

Fix patterns:

| English-shaped Russian | More natural Russian |
|---|---|
| `X связан с Y через Z` | `Z объясняет, почему X может быть связан с Y`; `X влияет на Y не напрямую, а через Z`, if causal language is supported |
| `X выступает драйвером Y` | `X может усиливать Y`; `X относится к факторам Y`; `X помогает объяснить Y`, by evidence strength |
| `посредством` | `через`; `с помощью`; or rebuild the sentence |
| `делает возможным для покупателей оценку товара` | `помогает покупателям оценить товар` |
| `имеет потенциал для снижения риска` | `может снизить риск`; `может быть связан со снижением риска`, by evidence strength |
| `переход к покупке` | `решение о покупке`; `готовность купить`; `намерение покупки`, by context |

Preserve cautious claims. Do not turn an association into a proven causal effect.

### RU-26. English islands in Russian academic prose

An English island is an English word or phrase embedded in an otherwise Russian sentence. In academic Russian, English islands are allowed only for a narrow set of reasons:

- names of authors, brands, products, standards, models, datasets, methods, or protocols
- abbreviations that are established in the field: `PRISMA`, `TAM`, `TPB`, `S-O-R`, `B2B`
- the original term at first definition, if it prevents ambiguity
- bibliography entries, direct quotes, file names, code, formulas, and source titles

If the English phrase is part of ordinary grammar, translate it or explain it.

| English island | Prefer in Russian |
|---|---|
| `e-commerce` | `электронная коммерция` / `электронная торговля` |
| `purchase intention` | `намерение покупки` / `готовность купить` |
| `usage intention` | `намерение использовать продукт или сервис` |
| `patronage intention` | `намерение снова обращаться к магазину, бренду или платформе` |
| `engagement` | `вовлеченность` / `взаимодействие с контентом` |
| `perceived value` | `воспринимаемая ценность` |
| `return behavior` | `решения о возврате товара` / `частота возвратов` |
| `return-related outcomes` | `результаты, связанные с возвратами` |
| `social proof` | `социальное доказательство` |
| `online reviews` | `онлайн-отзывы` / `отзывы покупателей` |
| `user-generated content`, `UGC` | `пользовательский контент` |
| `virtual try-on`, `VTO` | `виртуальная примерка` |
| `fit tools` | `инструменты подбора и оценки размера` |
| `size guides` | `таблицы размеров` / `рекомендации по выбору размера` |
| `fit reviews` | `отзывы о посадке` |
| `fit risk` | `риск ошибки в посадке` |
| `fit uncertainty` | `трудности с оценкой посадки` |
| `product diagnosticity` | `достаточность информации о товаре для его оценки` |
| `visual fit information` | `визуальная информация о посадке` |
| `model photography` | `фотографии товара на моделях` |
| `size-inclusive model photography` | `фотографии на моделях разных размеров` |
| `verbal haptic information` | `словесное описание тактильных свойств` |
| `haptic imagery` | `мысленное представление тактильных ощущений` |
| `outfit presentation` | `демонстрация товара в образе` / `демонстрация комплекта` |

Do not convert all English terms blindly. If the project glossary says to keep a term, keep it. If the term is central and not established in Russian, introduce a Russian explanation and optionally give the English original once in parentheses.

### RU-27. Calqued adjectives and unnatural compounds

English often turns nouns into modifiers. Russian often prefers the genitive case or an explanatory phrase. LLMs overproduce Russian adjectives that look grammatical but sound translated.

Watch for:

- `товарное описание`
- `товарная презентация`
- `товарный контент`
- `товарная информация`
- `платформенные сигналы`
- `контентные инструменты`
- `контентные решения`
- `размерные рекомендации`
- `диагностическая роль`
- `поведенческие результаты`

Prefer:

| Calque | Better Russian |
|---|---|
| `товарное описание` | `описание товара` |
| `товарная презентация` | `презентация товара` |
| `товарный контент` | `контент о товаре` / `материалы о товаре` |
| `товарная информация` | `информация о товаре` |
| `платформенные сигналы` | `сигналы платформы` |
| `платформенные и сервисные сигналы` | `сигналы платформы и сервиса` |
| `контентные инструменты` | `инструменты контент-маркетинга` |
| `контентные решения` | `форматы контента` / `решения в области контента` |
| `размерные рекомендации` | `рекомендации по выбору размера` |
| `размерные таблицы` | `таблицы размеров` |
| `диагностическая роль` | `роль в оценке товара` |
| `поведенческие результаты` | `поведенческие эффекты` / `формы поведения`, by context |

This is not a ban on adjectives. It is a check for English-shaped modifier chains. Keep adjectives that are established in Russian or more precise than a genitive phrase.

### RU-28. Academic term normalization from English sources

Before drafting or finalizing Russian academic prose from English-language research, run a term normalization pass.

Use `russian-termbank.md` as the default reference when the project does not provide a stronger glossary.

Classify each term:

1. **Keep as original**: proper names, author names, titles, standards, protocols, abbreviations, formulas, source IDs in internal notes.
2. **Translate consistently**: accepted constructs such as `воспринимаемый риск`, `доверие`, `намерение покупки`, `вовлеченность`, `воспринимаемая ценность`.
3. **Explain once**: narrow constructs such as `product diagnosticity`, `haptic imagery`, `bracketing`, or `patronage intention`.
4. **Remove from final prose**: search labels, source-cluster labels, spreadsheet shorthand, and English phrases used only to organize notes.

First use pattern:

- `намерение покупки (purchase intention)` only if the English original is needed for alignment with the literature.
- After the first mention, use `намерение покупки`.
- If the literal Russian term is awkward, use an explanatory phrase instead of a fake Russian term.

Bad:

> `Диагностичность товара повышает purchase intention.`

Better:

> `Чем лучше информация помогает оценить товар до покупки, тем выше может быть намерение покупки.`

For a dissertation or thesis, prefer stable Russian terms in the main text and keep English labels in source plans, tables, appendices, or first-definition parentheses.

### RU-29. `Корпус источников` as a default academic calque

Do not use `корпус` as the default word for a literature base, source base, bibliography set, or set of reviewed papers in ordinary Russian academic prose.

The word `корпус` is legitimate in Russian, but it is specialized. Use it when the text really means a corpus in the strict sense: a deliberately compiled collection of texts or language data used for linguistic, corpus, textological, or quantitative textual analysis.

Avoid in dissertation, thesis, coursework, and literature-review prose when the meaning is simply "the sources used in the work":

- `корпус источников`
- `корпус научных работ`
- `корпус публикаций`
- `исследовательский корпус`
- `корпус литературы`
- `корпус рассмотренных исследований`

Prefer the term that matches the actual object:

| Weak / model-like | Prefer |
|---|---|
| `корпус источников` | `источниковая база`; `база источников`; `набор источников`; `перечень источников`, by context |
| `корпус научных работ` | `массив научных работ`; `набор научных работ`; `подборка публикаций`; `рассмотренные исследования` |
| `корпус публикаций` | `массив публикаций`; `выборка публикаций`; `набор публикаций` |
| `исследовательский корпус` | `эмпирическая база`; `материал исследования`; `источниковая база`, by context |
| `корпус литературы по теме` | `литература по теме`; `научная литература по теме`; `массив работ по теме` |

Examples:

- Weak: `В корпус источников вошли 50 научных работ.`
- Better: `Источниковая база исследования включает 50 научных работ.`
- Weak: `Корпус рассмотренных исследований показывает рост интереса к теме.`
- Better: `Рассмотренные исследования показывают рост интереса к теме.`
- Weak: `Для анализа был сформирован корпус публикаций о маркетплейсах.`
- Better: `Для анализа была сформирована выборка публикаций о маркетплейсах.`

Allowed:

- `корпус текстов` in corpus linguistics or text analysis;
- `Национальный корпус русского языка`;
- `параллельный корпус`, `размеченный корпус`, `подкорпус`;
- a deliberately compiled and annotated text collection when the method actually treats it as a corpus.

If the work only lists, reviews, maps, or cites sources, use `источниковая база`, `база источников`, `массив публикаций`, `выборка работ`, or `рассмотренные источники`.

## Human Russian Moves

Use these moves before the final humanizer pass.

- Restore concrete subjects and finite verbs.
- Replace noun chains with action where the register allows.
- Normalize English-source terms before smoothing style.
- Replace English islands with Russian terms unless the English form is required for precision.
- Let paragraph lengths vary.
- Use lighter connectors: `но`, `а`, `и`, `поэтому`, `хотя`, `зато`.
- Add measured hedging when evidence is limited: `обычно`, `чаще всего`, `с оговорками`, `не всегда, но часто`, `по имеющимся данным`.
- Keep first person only when the genre permits it.
- In essays/blogs, allow controlled unevenness: fragments, short sentences, visible authorial rhythm.
- In formal genres, humanize through precision and clean syntax, not colloquialization.
- Read the sentence for breath: if one sentence contains several actions, split it.
- Prefer a concrete example over an abstract intensifier, but only if the example is provided or can be framed as hypothetical.

## Rewrite Examples

| AI-like Russian | Stronger Russian | Why |
|---|---|---|
| `Осуществляется реализация мероприятий по оптимизации процессов.` | `Мы оптимизируем процессы.` | Restores actor and verb. |
| `Эта функция является эффективной и масштабируемой.` | `Эта функция эффективна и хорошо масштабируется.` | Removes dummy copula. |
| `В рамках данной задачи необходимо учитывать ряд факторов.` | `В этой задаче нужно учесть несколько факторов.` | Cuts officialese and filler. |
| `Метод представляет собой инструмент, позволяющий осуществлять анализ данных.` | `Метод помогает анализировать данные.` | Removes stacked abstractions. |
| `На сегодняшний день вопрос является актуальным.` | `Сейчас этот вопрос важен для [кого/почему].` | Forces specificity. |
| `Исследования показывают, что подход эффективен.` | `По данным [источник], подход дал [результат].` | Prevents fake authority. |
| `Мы предлагаем комплексный инновационный подход.` | `Мы предлагаем способ, который [механизм] и [результат].` | Replaces empty adjectives with mechanism. |
| `Это не просто инструмент, а полноценная экосистема.` | `Инструмент закрывает три задачи: [A], [B], [C].` | Removes slogan structure. |
| `Было принято решение о проведении проверки.` | `Команда решила проверить [что] до [дата].` | Restores owner and action. |
| `Тишина обволакивала комнату, словно невидимое покрывало воспоминаний.` | `В комнате было так тихо, что слышно было, как щёлкает батарея.` | Replaces generic literary fog with specific detail. |

## Register Boundaries

### Academic / scientific

Prefer:

- precise terms and stable terminology
- cautious claims linked to sources
- clean definitions
- logical paragraph progression
- source placeholders when sources are missing

Allowed:

- `является` in strict definitions
- impersonal structures when actor is irrelevant
- repeated technical terms
- moderate nominalization when it names a concept

Avoid:

- unsupported generalizations
- fake consensus
- inflated relevance claims
- decorative conclusions
- excessive `актуальность обусловлена...` formulas unless required by the assignment

Humanization mode: make the prose clearer and more exact. Do not make it conversational unless requested.

### Business / professional

Prefer:

- answer first
- concrete owner, deadline, consequence
- short paragraphs
- direct verbs
- plain but respectful tone

Avoid:

- `данный`, `указанный`, `представляется целесообразным` unless legal/regulatory precision is required
- `играет ключевую роль`
- empty adjectives without proof
- artificial politeness that hides the ask

Humanization mode: reduce work for the reader.

### Publicistic / essay

Prefer:

- clear thesis
- living authorial voice
- concrete examples
- rhythm variation
- a real turn or complication

Avoid:

- sermon tone
- motivational slogans
- over-balanced `с одной стороны / с другой стороны` unless the piece genuinely compares positions
- generic openings about modernity, digitalization, or humanity

Humanization mode: preserve the author's pressure of thought, not just polish sentences.

### Copywriting

Prefer:

- user situation
- concrete benefit
- proof from provided facts
- mechanism before hype
- natural CTA

Avoid:

- fake urgency
- `уникальный`, `инновационный`, `лучший`, `комплексный` without proof
- inflated promises
- English calques in Russian product copy
- pseudo-premium tone with no substance

Humanization mode: make the offer believable and specific.

### Creative prose

Prefer:

- POV discipline
- sensory specifics
- behavior over emotion labels
- subtext in dialogue
- rhythm that fits the narrator or character

Avoid:

- explaining emotions after showing them
- stock gestures as fake showing
- generic literary metaphors
- over-smoothing character voice
- making every sentence beautiful

Humanization mode: preserve voice, tension, and roughness where useful.

## Exceptions and Safe Uses of Formal Markers

Formal markers are acceptable when they are necessary, conventional, or intentional.

- **Legal / regulatory / contractual:** `данный`, `указанный`, `настоящий`, passive forms, and exact cross-references may be required.
- **Scientific / technical:** nominalizations and impersonal constructions may be appropriate when naming methods, processes, or results.
- **Corporate / procedural:** some formulas may be part of internal standards or stakeholder expectations.
- **Quotation / imitation:** preserve wording in quotes or when the task intentionally imitates official style.
- **Authorial style:** keep unusual punctuation, repetition, or symmetry if the user sample clearly uses it deliberately.

Even in these cases, remove redundancy that does not add precision.

## Quick Russian Pre-Final Check

Before sending to `humanizer`, scan:

1. Are there unsupported facts, sources, names, statistics, examples, or customer claims?
2. Does the text use the right register for audience, genre, and channel?
3. Are there strings of nominalizations where a verb would be clearer?
4. Do paragraphs sound mechanically equal?
5. Are transitions repetitive or decorative?
6. Did any caveat, source limitation, term, number, quote, or condition disappear?
7. Is the text genuinely Russian in rhythm, not translated English?
8. Did humanization accidentally make the text too casual, too literary, or too promotional?
9. If the text uses English-language sources, have construct labels been translated, explained, or intentionally preserved?
10. Are project glossary decisions followed?

## Russian Self-Check

Fix every `yes` unless the pattern is required by genre, law, source quotation, exact terminology, or explicit authorial style:

1. Остались ли `является`, `представляет собой`, `выступает в качестве` вне мест, где они нужны?
2. Остались ли `важно отметить`, `стоит подчеркнуть`, `следует отметить`?
3. Есть ли цепочки из 3+ отглагольных существительных?
4. Больше одного сильного длинного тире на абзац?
5. Есть ли `данный / указанный / вышеупомянутый` вне юридического или нормативного регистра?
6. Осталось ли `не просто X, а Y` / `не только X, но и Y` как пустой риторический приём?
7. Есть ли тройное перечисление с одинаковой грамматикой и без доказательной нагрузки?
8. Есть ли `в рамках`, `в разрезе`, `на сегодняшний день`, `в настоящее время`, `имеет место быть` без причины?
9. Есть ли `в современном мире`, `в эпоху цифровизации`, `сегодня как никогда`?
10. Есть ли мотивационный финал абзаца?
11. Есть ли причастный или деепричастный каскад длиннее двух оборотов?
12. Есть ли `необходимо / следует / рекомендуется / целесообразно` там, где можно дать прямой глагол?
13. Есть ли слова `эффективный / комплексный / ключевой / актуальный / инновационный` без конкретного смысла?
14. Повторяются ли `таким образом / кроме того / однако / следовательно` как механические переходы?
15. Не заменены ли точные термины на более красивые, но менее точные слова?
16. Все ограничения, оговорки, термины и числа на месте?
17. Сохранён ли регистр?
18. Остались ли английские слова внутри русской грамматики без причины?
19. Есть ли списки с `and` внутри русского предложения?
20. Есть ли гибриды вроде `fashion-сегмент`, `apparel/fashion-контекст`, `sportswear-категория`?
21. Есть ли кальки типа `товарный контент`, `платформенные сигналы`, `размерные рекомендации`, `возвратное поведение`?
22. Не попали ли в основной текст внутренние source labels вместо русских терминов?
