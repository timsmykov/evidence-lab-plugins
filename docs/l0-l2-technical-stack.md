# L0-L2 technical stack

This is the minimum Evidence Lab stack for a first consultation. The machine-readable source of truth is [`catalog/l0-l2-stack.json`](../catalog/l0-l2-stack.json); this page is the review view.

## Cost boundary

“Free L0-L2” means that Evidence Lab does not require a paid extension, MCP service, or external memory system. The researcher still needs access to one primary agent. Codex or Claude Code access may require an eligible subscription, organizational entitlement, API billing, or an approved cloud-provider route.

The second agent is optional. No L0-L2 component may require both hosts.

## Level contract

| Level | Accepted result | Required boundary |
|---|---|---|
| L0 | One agent is installed, signed in, and limited to a safe project folder. | Account route, client, project boundary, backup, and data policy. |
| L1 | The agent completes small file tasks with visible instructions, approvals, diffs, and checks. | Project control files, local Git, local search, permissions, source verification, and acceptance. |
| L2 | Work produces traceable artifacts and can be installed, updated, removed, and recovered from recorded state. | Evidence Lab foundation, research records, and installation lifecycle. Document and data tools remain conditional. |

## Profiles

**Base** is the only universal profile. It contains 13 components: one provider route, one client, the project boundary, local controls, and the Evidence Lab installation lifecycle.

**Documents** adds Poppler, OCRmyPDF, Pandoc, Quarto, and Zotero only when the materials or output format require them.

**Data** adds a project-local Python environment with uv and, when needed, Jupyter. R is a separate discipline or laboratory branch.

## Component review

| Level | Component | Inclusion | Cost class | Verification | Current decision |
|---|---|---|---|---|---|
| L0 | Primary agent account and access | Route required | Provider access required | Docs verified | Choose Codex or Claude Code; check current account terms during intake. |
| L0 | Primary agent client | Route required | No separate Evidence Lab charge | Observed on Linux | Codex 0.150.1 and Claude Code 2.1.220 were present; macOS and WSL2 lifecycle runs remain open. |
| L0 | Isolated project workspace | Required | No extra charge | Docs verified | One local project boundary with explicit output and check areas. |
| L0 | Data boundary, backup, and secrets | Required | Client-specific | Docs verified | Use the client's approved systems; Evidence Lab does not introduce another provider. |
| L1 | Portable project instructions | Required | No extra charge | Simulated on both hosts | Shared rules live in `AGENTS.md`; host adapters must not duplicate the method. |
| L1 | Local Git history | Required | Free local software | Observed on Linux | A remote repository is optional and depends on the data policy. |
| L1 | Local file search | Required | Free local software | Observed on Linux | Use ripgrep or the host-bundled copy. |
| L1 | Permission baseline | Required | Included with host | Docs verified | Start conservatively and expand only for a demonstrated task. |
| L1 | Primary-source verification | Required | Host-route dependent | Docs verified | Built-in search is enough at L1; external research MCP is not part of the base. |
| L1 | Diff, checkpoint, and acceptance | Required | No extra charge | Simulated on both hosts | Every material task ends with a visible check. |
| L2 | Evidence Lab frozen foundation | Required | Free local software | Simulated on both hosts | Installation mechanics are covered; research packs remain draft until representative runs and independent review. |
| L2 | Source ledger and decision trail | Required | No extra charge | Docs verified | The dedicated capabilities are still planned gaps, so L2 cannot yet be called complete. |
| L2 | Installation state and recovery | Required | No extra charge | Simulated on both hosts | Exact plan, readback, reconciliation, removal, and restore paths are test-covered with fake hosts. |
| L2 | Poppler text extraction | Conditional | Free local software | Observed on Linux | Add for PDF work after a fixture test. |
| L2 | OCRmyPDF | Conditional | Free local software | Docs verified | Absent on the observed host; remains Pilot. |
| L2 | Pandoc | Conditional | Free local software | Observed on Linux | Add when conversion is required; formal fixtures remain open. |
| L2 | Quarto | Conditional | Free local software | Docs verified | Absent on the observed host; remains Pilot. |
| L2 | Zotero Desktop and managed export | Conditional | Free local app; optional paid storage | Docs verified | Export-first route; plugin access needs a separate audit. |
| L2 | Python, uv, and Jupyter | Conditional | Free local software | Partially observed | uv was present; Jupyter and a locked data fixture remain open. |
| L2 | R environment | Conditional | Free local software | Docs verified | Install only for a matching discipline or laboratory; no live fixture yet. |

## Verification meanings

- `docs-verified`: current primary documentation supports the lifecycle or boundary, but no complete local run is recorded.
- `locally-observed`: the component or command was observed on one Linux host. This does not prove clean installation or removal.
- `simulated-cross-host`: deterministic tests cover both host adapters and lifecycle branches with controlled fake-host readback.
- `live-cross-host`: reserved for successful clean install, representative use, update, removal, and readback on both hosts. No component has this status yet.

## What remains before the task is Done

1. Run the Base profile on clean macOS, WSL2, and Linux environments for Codex and Claude Code.
2. Record install, sign-in, update, removal, and residual-file readback without storing credentials.
3. Add one fixture for every conditional Documents and Data component before promoting it from Pilot.
4. Implement and test the source-ledger and research-log gaps in the frozen foundation.
5. Have an independent reviewer accept the matrix and the saved run evidence.

Until these checks pass, the registry is the canonical plan and gap map, not a production certification.
