---
name: literature-review
description: Plan and conduct reproducible literature reviews with explicit search boundaries, documented screening decisions, structured evidence extraction, quality appraisal, synthesis, and verified citations. Use for systematic, scoping, rapid, or narrative reviews; use paper-lookup for a bounded paper search and writing-skill only after the evidence set is stable.
allowed-tools: Read Write Edit Bash
license: MIT
metadata:
  version: "1.7"
  skill-author: K-Dense Inc.
---

# Literature Review

## Overview

Conduct bounded literature reviews following an explicit protocol. Search appropriate scholarly databases, preserve the search and screening trail, synthesize findings without overstating coverage, and verify citations against the underlying records and texts.

Use `paper-lookup` for scholarly API retrieval, `database-lookup` for other documented public databases, and `citation-management` for metadata verification and bibliography output. General web search may supplement these routes when available, but it is never an undocumented substitute for a reproducible database strategy.

## Researcher confirmation points

Before retrieval, obtain confirmation for any material choice the request has not already settled: review type, research question, date and language limits, databases, inclusion and exclusion criteria, grey literature or preprint treatment, and stopping rule. Before synthesis, confirm any consequential changes to the protocol and record them as deviations. The accountable researcher owns screening judgments and substantive conclusions.

## When to Use This Skill

Use this skill when:
- Conducting a systematic literature review for research or publication
- Synthesizing current knowledge on a specific topic across multiple sources
- Performing meta-analysis or scoping reviews
- Writing the literature review section of a research paper or thesis
- Investigating the state of the art in a research domain
- Identifying research gaps and future directions
- Requiring verified citations and professional formatting

## Optional visual artefacts

Add a figure only when it improves auditability or understanding. Use `markdown-mermaid-writing` for a versionable search or screening flow, and `scientific-visualization` for data-derived figures. A review is not incomplete merely because it has no decorative illustration.

---

## Core Workflow

A literature review runs in seven phases, documented in full with commands and templates
in [references/core_workflow.md](references/core_workflow.md):

1. **Planning and scoping** — the question, inclusion and exclusion criteria, and scope.
2. **Systematic literature search** — multi-database searching with recorded queries.
3. **Screening and selection** — title/abstract then full-text screening with counts kept
   for the PRISMA flow.
4. **Data extraction and quality assessment** — structured extraction and risk-of-bias
   or quality appraisal.
5. **Synthesis and analysis** — thematic or quantitative synthesis across studies.
6. **Citation verification** — every citation checked against the actual source.
7. **Document generation** — assembling the review with a complete bibliography.

Record every search string and date as you go: a review that cannot reproduce its own
search is not systematic. Per-database search guidance and citation styles are in
[references/search_and_citation.md](references/search_and_citation.md), and a full worked
review is in [references/example_workflow.md](references/example_workflow.md).

## Best Practices

### Search Strategy
1. **Start with the protocol**: Choose databases because their coverage matches the question, not because an arbitrary minimum is required.
2. **Use complementary databases when needed**: Record why each database earns its place and disclose known coverage gaps.
3. **Decide preprint treatment explicitly**: Include or exclude them according to the protocol and label them clearly.
4. **Document everything**: Preserve exact search strings, dates, filters, result counts, and exported records.
5. **Test and refine**: Run pilot searches, review results, adjust search terms
6. **Sort by citations**: When available, sort search results by citation count to surface influential work first

### Screening and Selection
1. **Use clear criteria**: Document inclusion/exclusion criteria before screening
2. **Screen systematically**: Title → Abstract → Full text
3. **Document exclusions**: Record reasons for excluding studies
4. **Consider dual screening**: For systematic reviews, have two reviewers screen independently

### Synthesis
1. **Organize thematically**: Group by themes, NOT by individual studies
2. **Synthesize across studies**: Compare, contrast, identify patterns
3. **Be critical**: Evaluate quality and consistency of evidence
4. **Identify gaps**: Note what's missing or understudied

### Quality and Reproducibility
1. **Assess study quality**: Use appropriate quality assessment tools
2. **Verify all citations**: Run verify_citations.py script
3. **Document methodology**: Provide enough detail for others to reproduce
4. **Follow guidelines**: Use PRISMA for systematic reviews

### Writing
1. **Be objective**: Present evidence fairly, acknowledge limitations
2. **Be systematic**: Follow structured template
3. **Be specific**: Include numbers, statistics, effect sizes where available
4. **Be clear**: Use clear headings, logical flow, thematic organization

## Common Pitfalls to Avoid

1. **Single database search without a coverage rationale**: May miss relevant papers; justify the selected database set
2. **No search documentation**: Makes review irreproducible; document all searches
3. **Study-by-study summary**: Lacks synthesis; organize thematically instead
4. **Unverified citations**: Leads to errors; always run verify_citations.py
5. **Too broad search**: Yields thousands of irrelevant results; refine with specific terms
6. **Too narrow search**: Misses relevant papers; include synonyms and related terms
7. **Silent preprint policy**: Decide whether preprints are eligible and label their status
8. **No quality assessment**: Treats all evidence equally; assess and report quality
9. **Publication bias**: Only positive results published; note potential bias
10. **Outdated search**: Field evolves rapidly; clearly state search date

## Integration with Other Skills

Use the smallest relevant set of neighboring core skills:

- **paper-lookup**: scholarly discovery, identifiers, citation graphs, and available full text.
- **database-lookup**: reproducible retrieval from documented public databases outside the paper index layer.
- **citation-management**: metadata validation, deduplication, and bibliography output.
- **scientific-critical-thinking**: claim and evidence-quality appraisal.
- **statistical-analysis**: only for an agreed quantitative synthesis plan.
- **writing-skill**: drafting after the evidence table and synthesis boundaries are stable.

## Resources

### Bundled Resources

**Scripts:**
- `scripts/verify_citations.py`: Verify DOIs and generate formatted citations
- `scripts/generate_pdf.py`: Convert markdown to professional PDF
- `scripts/search_databases.py`: Process, deduplicate, and format search results

**References:**
- `references/citation_styles.md`: Detailed citation formatting guide (APA, Nature, Vancouver, Chicago, IEEE)
- `references/database_strategies.md`: Comprehensive database search strategies

**Assets:**
- `assets/review_template.md`: Complete literature review template with all sections

### External Resources

**Guidelines:**
- PRISMA (Systematic Reviews): http://www.prisma-statement.org/
- Cochrane Handbook: https://training.cochrane.org/handbook
- AMSTAR 2 (Review Quality): https://amstar.ca/

**Tools:**
- MeSH Browser: https://meshb.nlm.nih.gov/search
- PubMed Advanced Search: https://pubmed.ncbi.nlm.nih.gov/advanced/
- Boolean Search Guide: https://www.ncbi.nlm.nih.gov/books/NBK3827/

**Citation Styles:**
- APA Style: https://apastyle.apa.org/
- Nature Portfolio: https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards
- NLM/Vancouver: https://www.nlm.nih.gov/bsd/uniform_requirements.html

## Dependencies

### Required Python Packages
```bash
uv pip install requests  # For citation verification
```

### Required System Tools
```bash
# For PDF generation
brew install pandoc  # macOS
apt-get install pandoc  # Linux

# For LaTeX (PDF generation)
brew install --cask mactex  # macOS
apt-get install texlive-xetex  # Linux
```

Check dependencies:
```bash
python scripts/generate_pdf.py --check-deps
```

## Summary

This literature-review skill provides:

1. **Systematic methodology** following academic best practices
2. **Reproducible search routing** through documented scholarly and public-database interfaces
3. **Explicit coverage boundaries** rather than implied comprehensiveness
4. **Citation verification** ensuring accuracy and credibility
5. **Professional output** in markdown and PDF formats
6. **Comprehensive guidance** covering the entire review process
7. **Quality assurance** with verification and validation tools
8. **Reproducibility** through detailed documentation requirements

Conduct thorough, rigorous literature reviews that meet academic standards and provide comprehensive synthesis of current knowledge in any domain.
