# Review checklist

The reviewer checks whether it works, not whether it reads well. The order below follows how often each item is what actually breaks.

## Reproducibility

- [ ] The pull request carries a real run: input, artefact, what came out wrong.
- [ ] Deterministic steps sit in `scripts/` and run without the agent.
- [ ] A rerun on the same input produces the same artefact.

## Provenance

- [ ] `meta.json` → `provenance.origin` names someone's practice, not general reasoning.
- [ ] `provenance.evidence` points at material that can be opened.
- [ ] The procedure was tried on two different cases, not one.

## Routing

- [ ] The description names concrete launch phrasings, including colloquial ones.
- [ ] Both English and Russian queries are covered.
- [ ] Negative cases come from neighbouring skills rather than being invented.
- [ ] No eval case overlaps in meaning with another skill in this plugin.

## Human decisions

- [ ] There is an explicit confirmation point wherever the procedure chooses criteria or boundaries.
- [ ] The skill does not present a model hypothesis as a result derived from data.
- [ ] Gaps are rendered as gaps.

## Boundaries and privacy

- [ ] The "what it does not do" section is honest and specific.
- [ ] No client documents, personal data, private paths or addresses.
- [ ] `risk_level` matches the contents.

## Formalities

- [ ] `verify_repo.py` is green and its output is attached.
- [ ] Version bumped, `CHANGELOG.md` updated.
- [ ] For `status: production`: reviewer differs from owner, `reviewed_at` is set.

## Verdict

Findings ordered by severity, each anchored to a place in the files. "Clean" is a valid verdict; do not manufacture findings for volume.
