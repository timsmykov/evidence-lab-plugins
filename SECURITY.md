# Security policy

## Supported releases

Security fixes target the latest published `release-*` snapshot. Draft packs
are included for testing and feedback but are not represented as independently
validated scientific methods.

## Report a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a
public issue when a report contains a credential, an exploitable installation
path, private data, or enough detail to reproduce an unpatched vulnerability.

Include the affected release tag, pack, host, reproduction steps, expected and
observed behavior, and the minimum information needed to validate the report.
Never attach real client, student, or research-subject data.

## Scope

Relevant reports include unsafe bootstrap behavior, release-lock bypasses,
command or path injection, credential exposure, unauthorized plugin removal,
and deterministic helper scripts that write outside their documented output
boundary.

Scientific disagreement with a method belongs in a normal issue unless it also
creates a software security or privacy risk.
