---
name: research-image-analysis
description: Inspect scientific or research images while preserving source identity, acquisition context, transformations, measurement definitions, exclusions, and interpretation limits. Use for microscopy, experimental photographs, scans, or instrument images; do not use merely to make decorative figures or infer unsupported diagnoses.
---

# Research Image Analysis

Keep observation, processing, measurement, and interpretation separate. Work only with images the researcher is authorized to use, and preserve the original asset unchanged.

## Procedure

1. Record the source ID, original file hash when available, acquisition context, scale, channel or modality, and missing metadata.
2. Define the inspection or measurement question and obtain researcher confirmation before transformations or exclusions.
3. Log every crop, contrast adjustment, filter, annotation, segmentation, or resampling step with parameters. Never overwrite the original.
4. Record measurement definitions, units, calibration, inclusion or exclusion decisions, and software versions.
5. Run `scripts/validate_image_provenance.py` and report observations separately from interpretations and domain conclusions.

## Boundaries

This skill does not diagnose, authenticate manipulated imagery, validate an instrument, or replace domain-specific image-analysis software and expert review.
