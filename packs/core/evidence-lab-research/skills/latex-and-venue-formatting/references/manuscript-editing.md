# Conservative LaTeX and mathematical editing

Use this reference for theorem-, proof-, equation-, notation-, or cross-reference-heavy source.

## Modes

- In edit mode, make only requested or uniquely forced corrections.
- In review-only mode, report findings without rewriting source.
- In self-review mode, inspect changed hunks plus the definitions and conventions needed to judge them.

## Preserve meaning

Establish the project's language variant, notation, macros, theorem conventions, citation commands, and formatting style before editing. Do not normalize equivalent LaTeX commands merely for taste.

A change to an operator, relation, sign, coefficient, variable, index, exponent, subscript, superscript, quantifier, hypothesis, conclusion, domain, codomain, or proof step is a **mathematical-token change**. Make one only when the intended correction is uniquely forced by immediate context and does not require a new argument. List every such change in the final report. Otherwise leave the source unchanged and flag the issue.

Proofreading does not repair a proof gap. A repeated pattern does not by itself justify changing a sign or index.

## Checklist

- grammar, agreement, punctuation, terminology, and display integration;
- balanced delimiters, valid environment nesting, math mode, alignment markers, and line breaks;
- labels, references, equation references, citations, and local custom commands;
- symbols, indices, primes, decorations, ranges, dimensions, units, and stated assumptions;
- consistency between a statement, its proof, adjacent equations, abstract, introduction, examples, and conclusion;
- exact citation and notation translation for external results;
- explicit tested range for computational evidence.

When integrating an already validated result, map its durable source, target theorem hierarchy, hypotheses, limitations, notation translation, citations, and downstream claims before editing. Update the smallest coherent region and preserve the human or specialist review status.

Use compiler-safe reviewer comments only when explicitly requested:

```latex
% REVIEWER NOTE: precise unresolved issue and required verification
```
