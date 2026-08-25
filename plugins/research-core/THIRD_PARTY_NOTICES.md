# Third-party notices

## K-Dense Scientific Agent Skills

The following skills are adapted from K-Dense-AI/scientific-agent-skills at commit `36d8f13a1e754618794bf42f417884940077b4ae`:

- citation-management
- database-lookup
- experimental-design
- exploratory-data-analysis
- hypothesis-generation
- literature-review
- markdown-mermaid-writing
- markitdown
- paper-lookup
- peer-review
- scientific-critical-thinking
- scientific-visualization
- statistical-analysis
- statistical-power
- uncertainty-and-units

Upstream repository: https://github.com/K-Dense-AI/scientific-agent-skills

Upstream repository code is primarily MIT-licensed; copyright and license terms are preserved in `LICENSES/K-Dense-MIT.txt`. The bundled `markdown-mermaid-writing` skill declares Apache-2.0 and retains its author, source, contributor, and license metadata in `SKILL.md`.

## Evidence Lab Writing Skill

`writing-skill` is adapted from an existing Evidence Lab bilingual writing workflow and reorganized for the plugin format. Its academic mode is part of the general writer rather than a separate `scientific-writing` skill.

## Deliberate omissions

- `liteparse` is not included while the document-parsing architecture is under comparison.
- K-Dense `scientific-writing` is not included because its routing would overlap the general `writing-skill`.
