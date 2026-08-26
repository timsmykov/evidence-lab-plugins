---
name: life-science-protocols
description: Add life-science-specific protocol, biological-control, bias, biosafety-boundary, reporting, and acquisition-metadata checks to a study or image workflow. Use when a life-science project is being planned or biological images are analysed; do not provide clinical decisions or experimental safety authorization.
---

# Life-Science Protocols

Make domain assumptions and missing protocol information visible before generic research procedures are treated as sufficient.

## Procedure

1. Record the biological system, sample or population, protocol identity and version, unit of analysis, controls, endpoints, timing, batches, and exclusion rules.
2. Identify applicable bias sources, contamination or batch risks, blinding or randomization, and reporting context.
3. Record the responsible institutional or domain authority for safety, ethics, clinical, animal, or biosafety decisions. The agent cannot approve them.
4. For images, add acquisition modality, scale, channel, calibration, and preprocessing metadata.
5. Obtain researcher confirmation of material design choices, then run `scripts/validate_protocol_record.py` before downstream analysis.

## Boundaries

This draft skill does not authorize laboratory work, diagnose or treat patients, replace ethics or biosafety review, or assert compliance with a guideline that has not been explicitly checked.
