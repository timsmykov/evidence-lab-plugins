---
name: systematic-review
description: Build and run a reproducible systematic-search, deduplication, and screening workflow with explicit eligibility criteria and decision reasons. Use for systematic, scoping, or evidence reviews that require an auditable record flow; do not use for an informal literature overview or fabricate database coverage.
---

# Systematic Review

Create an auditable review process, not merely a fluent synthesis. Keep the protocol, search strings, source coverage, exported records, deduplication keys, screening decisions, exclusions, and amendments as separate artefacts.

## Procedure

1. Define the review question, eligibility criteria, date and language boundaries, sources, and planned synthesis.
2. Obtain researcher approval of the protocol before screening. Record later amendments instead of silently changing criteria.
3. Run documented searches and retain exact query, source, time, result count, and inaccessible sources.
4. Normalize records and run `scripts/deduplicate_records.py`; preserve duplicate-to-canonical mappings.
5. Screen with stable record IDs and explicit reasons. Keep uncertain records for human resolution.
6. Report flow counts and coverage. Never infer that an unavailable database was searched.

## Boundaries

This draft workflow does not certify PRISMA compliance, clinical validity, meta-analysis correctness, or protocol registration. Those claims require the applicable current standard and accountable expert review.
