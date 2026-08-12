---
description: Reference entry point — run the example-domain procedure over a folder of documents
argument-hint: путь к каталогу с документами
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill", "AskUserQuestion"]
---

# /example-domain

Точка входа для человека. Команда не пересказывает скилл, а запускает его с нужными параметрами и собирает результат.

1. Если путь не передан аргументом — спроси, где лежат документы.
2. Загрузи скилл `example-domain:example-procedure` и выполни процедуру.
3. На шаге подтверждения признаков остановись и спроси пользователя через `AskUserQuestion`.
4. После сборки `summary.md` вызови субагента `example-domain-critic` и приложи его замечания.
5. Верни путь к `summary.md`, охват и список замечаний одним сообщением.
