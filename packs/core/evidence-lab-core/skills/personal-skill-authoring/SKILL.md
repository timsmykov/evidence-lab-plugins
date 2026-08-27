---
name: personal-skill-authoring
description: >-
  Turns a repeated personal research task into a small, portable, tested agent
  skill. Use when a researcher asks to create, teach, save, automate, improve,
  or package their own recurring workflow for Codex or Claude Code. Do not use
  merely to perform a one-off research task.
---

# Personal Skill Authoring

Help the researcher preserve a repeatable way of working without requiring
them to understand plugin structure, YAML, scripts, or terminal commands.

## User experience

Work in ordinary chat. Ask only what is still unknown, one short question at a
time. Offer concrete choices and always accept a free-form answer. The default
route needs four decisions:

1. What repeated result should the skill produce?
2. What inputs does the researcher normally provide?
3. Which decisions must remain with the researcher?
4. What would prove that the result is good enough?

Infer obvious details from the current conversation and files. Do not make the
researcher repeat information already available. Before creating files, show a
plain-language card with the proposed name, trigger, inputs, output, human
confirmation points, and acceptance checks. Continue only after the researcher
confirms or corrects that card.

## Authoring workflow

### 1. Bound one reusable job

Create one skill for one recognizable job. Separate a broad request into
multiple skills when it has independent triggers or outputs. Keep transient
project facts, client data, credentials, and unpublished source material out of
the reusable instructions.

Write a discriminating description that says both what the skill does and when
it should activate. Include a negative boundary when an adjacent skill could be
confused with it.

### 2. Design the smallest useful package

Start with `SKILL.md`. Add only resources that materially improve reliability:

- `scripts/` for deterministic parsing, validation, conversion, calculation,
  or repeated boilerplate;
- `references/` for procedures, rubrics, schemas, or source-specific guidance
  that should be loaded only when needed;
- `assets/` for templates copied into the user's deliverable;
- `evals/trigger_eval.json` for at least five positive and three negative
  trigger examples.

Prefer host-neutral instructions. Put Codex- or Claude-specific installation
steps in a thin adapter, not in the research method itself. Never copy a
platform-owned system skill into the new package.

### 3. Scaffold without exposing technical steps

The agent may run `scripts/scaffold_personal_skill.py` after the confirmation
card. The researcher should see progress such as “I created the draft and am
checking it,” not a command they must paste into a terminal.

Choose the destination through the active host adapter. If the destination is
unknown, create the draft inside the current project and explain that it has
not yet been installed. Never overwrite an existing skill; update it through a
reviewed diff instead.

### 4. Write operational instructions

Use direct actions, explicit inputs and outputs, and visible stop conditions.
State where the model may reason and where a deterministic script or human
decision is required. Keep the main file concise and move detailed reference
material out of it.

Use `references/quality-checklist.md` before validation. For a safety-critical,
scientifically consequential, or complex skill, test it independently against
representative inputs rather than treating structural validation as evidence
of quality.

### 5. Validate and demonstrate

Run `scripts/validate_personal_skill.py PATH_TO_SKILL`. Fix every error. Then
exercise all trigger cases and at least one representative end-to-end example.
Report separately:

- what was created;
- where it lives;
- what the structural and trigger checks established;
- what still needs a real research run or domain review.

Do not call a skill production-ready only because its files are valid.

## Updating an existing personal skill

Read the current skill and its resources first. Preserve user-specific choices
that remain valid. Show the behavioral change in plain language, edit narrowly,
rerun validation and trigger tests, and keep a recoverable copy or versioned
history when the host supports it.
