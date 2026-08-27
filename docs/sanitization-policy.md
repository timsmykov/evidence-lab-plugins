# Public-source content privacy

The repository and catalogue are public. Material entering them may originate
in personal instances or client work, so the boundary is drawn before a commit,
not after an incident.

## Never enters the repository

- Tokens, keys, passwords, connection strings.
- Private host paths, internal server names, IP addresses.
- Personal data: email addresses, phone numbers, names of students and clients.
- The contents of client and student documents, including fragments used as examples.
- Internal system identifiers: links to private pages, record UUIDs.

## Enters after processing

- A procedure derived from client work, provided the subject matter is generalized and recognizable detail is replaced.
- Examples — synthetic, or anonymized past recognition. "Anonymized" means the person cannot be reconstructed from the combination of details, not that a surname was struck out.
- Screenshots — only when they carry nobody else's data; the default is no.

## How this is checked

`scripts/verify_repo.py` looks for private paths, IPs, tokens, email addresses,
links to private pages, bare UUIDs, and obsolete proprietary license markers.
Gitleaks independently scans both the current tree and the complete Git history.
The gates are deliberately conservative and will occasionally flag harmless
examples. Narrow an exception to the exact rule, path, and documented placeholder
in a reviewed change; never disable the check or add a broad allowlist.

Email addresses are allowed only in `LICENSE` and `SECURITY.md`.

## Risk class

`team_safe` — shareable across the team as is. `internal_only` — the pack depends on internal infrastructure and stays outside published marketplaces. A `team_safe` pack is exposed to Claude Code or Codex only when that runtime is explicitly listed in both `pack.json` and `meta.json`.

## If something has already leaked

Deleting the file is not enough — history keeps it. The order is: revoke the leaked secret, then clean history, then work out how the rule missed it.
