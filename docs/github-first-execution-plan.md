# GitHub-first execution plan

Status: active  
Scope decision: complete route through a clean-user GitHub release  
Release model: immutable repository snapshots plus independent pack SemVer  
Platforms: Codex and Claude Code

## Outcome

A researcher can start from a trusted Evidence Lab release, answer four short
questions in chat, review an explainable recommendation, approve it once, and
receive a reproducible research stack. Free text improves classification but
cannot invent a pack, skill, command, or repository source.

Marketplace listing and marketplace-provider verification are a later external
gate. This plan makes the GitHub route complete without depending on them.

## Product and trust model

```text
researcher answer
      |
      v
LLM normalization suggestion        controlled vocabulary
      |                                      |
      +-------------- validate --------------+
                         |
                         v
                 normalized profile
                         |
                         v
          deterministic Selection Policy
                         |
                         v
       ordered packs + rule IDs + explanation
                         |
                  user confirmation
                         |
                         v
       native host install / update / removal
                         |
                         v
                  host readback + state
```

The LLM boundary ends at normalization. Selection, dependency resolution,
ordering, conflict detection, installation, and readiness are deterministic.

## What already exists

- Host-neutral `pack.json` files and generated Codex/Claude adapters.
- Four installable packs with dependencies and independent versions.
- Four-question English/Russian onboarding catalogs.
- A normalized profile schema and deterministic selector.
- Installation plans with tamper checks and explicit confirmation.
- Native Codex and Claude Code adapters, host readback, atomic state,
  idempotent retry, and bounded rollback.
- Fake-host lifecycle coverage and real isolated installation evidence.

The work below extends these paths. It must not build a second installer,
second pack catalog, or host-specific selection implementation.

## Architecture decisions

1. Pack is the physical installation and release unit. Skills remain procedures
   inside a pack and are routed at task time.
2. Large packs are split only when scenario tests show systematic over-installation
   or when dependencies/lifecycle differ, not merely because a taxonomy permits it.
3. Selection rules live with the pack that they select. One central Selection
   Policy owns the vocabulary, matching semantics, confidence thresholds,
   fallback behavior, and ordering contract.
4. LLM output is untrusted structured input. Unknown IDs are rejected and useful
   unmatched text is retained only as `specialization`/`unmapped` evidence.
5. Removal is never an implicit side effect of answering onboarding differently.
   Reconciliation shows additions, updates, retained extras, and proposed removals;
   removals require a separate explicit confirmation.
6. A distribution release is one immutable repository snapshot. Pack versions
   remain independent, while a release lock records the exact combination.

## Delivery sequence

### R1. Selection Policy v1

Deliverables:

- controlled vocabulary for every profile field;
- explicit rule grammar (`any`, `all`, `none`) and stable rule IDs;
- deterministic rule evaluation and dependency-aware pack ordering;
- structured reasons in selection plans;
- catalog/policy/question drift checks;
- migration of the four current packs from broad OR matching;
- positive, negative, boundary, conflict, and ordering fixtures.

Definition of Done:

- the same profile and catalog always produce byte-equivalent plans;
- an unknown profile value fails before selection;
- `active-research` alone no longer installs the full-cycle pack;
- no LLM or host branch exists in the selector;
- all generated adapter, schema, repository, and selector tests pass.

### R2. Safe LLM normalizer contract

Deliverables:

- normalization request/result schemas;
- a host-neutral normalization instruction and localized researcher copy;
- confidence per mapped value, `unmapped` evidence, and follow-up status;
- deterministic post-validation against Selection Policy;
- adversarial evals for invented IDs, prompt injection, mixed languages,
  ambiguous disciplines, very long answers, and empty answers;
- a no-LLM numeric/option path that remains the default fast route.

Definition of Done:

- free text can only emit vocabulary IDs declared by the policy;
- low-confidence mappings cannot change the installation plan silently;
- injection-shaped answers remain inert data;
- RU and EN fixtures produce equivalent normalized IDs when semantically equal;
- the option-only route works without an LLM normalization call.

### R3. Pack-boundary evidence and catalog expansion

Deliverables:

- scenario matrix covering the initial target researcher segments;
- over-installation and missing-capability report per scenario;
- split/keep decision record for each current pack;
- prioritized additions for publication monitoring, systematic review,
  life sciences, qualitative/social research, and research images;
- provenance, license, owner, reviewer, behavior evals, and lifecycle status for
  every published pack.

Definition of Done:

- every published pack is selected by at least one positive scenario and excluded
  by at least one negative scenario;
- no pack is created solely to mirror a taxonomy label;
- dependency graphs are acyclic and every conflict has a tested resolution;
- new packs pass representative behavior runs before `production` status.

### R4. Reconcile, update, remove, and restore

State transition:

```text
profile change
    |
    v
new desired set ---- compare ---- installed readback
    |                                |
    +------------ reconcile ---------+
                       |
       +---------------+----------------+
       |               |                |
     add/update     retain extra    propose removal
       |               |                |
 first approval     no mutation     separate approval
       +---------------+----------------+
                       |
                 apply + readback
                       |
             ready / failed / partial
```

Deliverables:

- reconcile-plan and state schemas;
- exact diff between desired and installed packs;
- update of selected packs to release-lock versions;
- retained-extra default and explicit removal plan;
- pre-change snapshot and restore command;
- interrupted-run recovery and stale-plan detection;
- Codex/Claude parity and real-host acceptance tests.

Definition of Done:

- profile changes never remove data or packs without a second confirmation;
- failed updates restore the pre-change selected versions where the host permits;
- a stale plan cannot apply after profile, release, or installed state changes;
- readiness requires exact post-operation readback.

### R5. Immutable release snapshots

Deliverables:

- `release-lock.json` schema and deterministic builder;
- exact pack IDs, versions, tree hashes, supported hosts, and source commit;
- repository tags such as `release-2026.08.1` applied only to `main`;
- CI verification that a release lock matches repository contents;
- changelog aggregation, provenance/license gate, and release notes;
- update-channel policy (`stable`, later optionally `preview`).

Definition of Done:

- a tag plus release lock reproduces the exact four-pack installation;
- changing any locked pack content without its version bump fails CI;
- a tag cannot be published from a dirty or unverified commit;
- bootstrap records the release tag and lock digest in installation state.

### R6. Public GitHub distribution and clean-user acceptance

Deliverables:

- decision and sanitization audit for public canonical repo versus public release
  mirror;
- public installation source with immutable tags;
- plain-language entry request for Codex and Claude Code applications;
- clean-account acceptance matrix for macOS, Linux, and Windows/WSL where the
  hosts support them;
- private-repo, no-GitHub-auth, offline, proxy, permission, outdated-host, and
  interrupted-download failure routes;
- support bundle that contains no credentials or research content.

Definition of Done:

- a user with no repository knowledge can complete onboarding and installation;
- no terminal command is shown in the normal application flow;
- every failure explains what happened and offers a recoverable next action;
- exact installed IDs and versions are captured as acceptance evidence.

### R7. Application-facing entry experience

Deliverables:

- one canonical installation request/link per host;
- first-run copy, recommendation summary, confirmation, progress, completion,
  retry, update, and removal language in RU and EN;
- host-specific presentation adapters without changing the semantic flow;
- handoff into a new research task after successful installation;
- CLI documentation as a secondary route only.

Definition of Done:

- application flows expose research capabilities, not manifests or shell syntax;
- Codex and Claude Code ask the same semantic questions and produce the same plan;
- free-text input remains available at every question;
- the first research task begins without repeating onboarding.

## Dependency graph and execution lanes

| Release | Modules | Depends on |
|---|---|---|
| R1 | policy, selector, pack contracts, schemas, fixtures | current bootstrap |
| R2 | normalization contract, onboarding skill, evals | R1 |
| R3 | pack catalog, skills, provenance, scenario matrix | R1; uses R2 evals |
| R4 | bootstrap lifecycle, state, host adapters | R1 |
| R5 | release tooling, CI, locks | R1 and stable pack boundaries from R3 |
| R6 | distribution, acceptance | R4 and R5 |
| R7 | application copy and host presentation | R2, R4, R6 |

Parallel lanes after R1:

- Lane A: R2 -> R7.
- Lane B: R3 -> R5.
- Lane C: R4.
- Merge lanes at R6, then finish R7 acceptance.

R2 and R4 both touch onboarding/bootstrap contracts and should use separate
worktrees with an explicit schema ownership boundary. R3 and R5 are sequential
because release locks must describe the final pack split.

## Test plan

```text
SELECTION
  option-only profile
  free-text-normalized profile
  unknown token -> reject
  ambiguous token -> follow-up/no mutation
  overlapping rules -> stable reasons/order
  dependency/conflict/cycle -> deterministic failure

LIFECYCLE
  clean install -> ready
  exact rerun -> all skipped
  version update -> readback exact
  profile shrink -> retain extras
  approved removal -> remove only proposed packs
  interrupted apply -> recover from state
  stale/tampered plan -> reject before host command
  rollback failure -> partial with actionable error

DISTRIBUTION
  release lock -> content hashes match
  public clone without credentials
  Codex clean profile
  Claude Code clean profile
  offline/proxy/permission failures
```

Pure rule evaluation uses unit tests. Selector/profile/lock pipelines use
integration tests. Real Codex and Claude installs are acceptance tests. LLM
normalization changes require deterministic schema tests plus quality evals.

## Failure modes

| Failure | Required handling | Required evidence |
|---|---|---|
| LLM invents a token | reject or preserve as unmapped; no selection change | adversarial eval |
| broad rule over-selects | negative scenario fails CI | selector fixture |
| dependency cycle | stop before plan display | unit test |
| host CLI changes JSON shape | fail readback clearly; never report ready | fake + real host test |
| release tag/lock drift | release job fails | CI fixture |
| profile changes during apply | stale-plan rejection | lifecycle test |
| removal partly fails | `partial`, exact remaining readback, restore guidance | host simulation |
| private or inaccessible repository | explain access boundary without credential handling | clean-user test |

## Implementation tasks

- [x] T1 (P1) Define Selection Policy schema, controlled vocabulary, rule grammar,
  and ordering semantics.
- [x] T2 (P1) Migrate all four packs and selector to policy-driven matching.
- [x] T3 (P1) Add positive/negative/boundary selector fixtures and drift gates.
- [x] T4 (P1) Define normalization input/result schemas and deterministic validator.
- [x] T5 (P1) Add free-text normalization eval suite and injection cases.
- [x] T6 (P2) Produce scenario-to-capability coverage and pack-boundary report.
- [ ] T7 (P2) Implement approved pack splits/additions with provenance and evals.
- [ ] T8 (P1) Implement reconcile/update/retained-extra/remove/restore lifecycle.
- [ ] T9 (P1) Add release-lock builder, hashes, CI, and immutable snapshot tags.
- [ ] T10 (P1) Complete public-source sanitization and clean-user host acceptance.
- [ ] T11 (P2) Finalize RU/EN application-facing installation and recovery copy.
- [ ] T12 (P2) Add secondary CLI documentation and support bundle generation.

## NOT in scope

- OpenAI or Anthropic marketplace approval: controlled by the platform providers.
- Hermes packaging: the active platform scope is Codex and Claude Code.
- Runtime generation of new skills: only reviewed repository artifacts install.
- Silent installation: the complete plan remains visible and explicitly approved.
- Automatic removal after profile changes: removal has a separate confirmation.
- Eager installation of every optional scientific Python dependency: individual
  skills install reviewed, pinned runtime dependencies when first needed.

## Completion gate

The GitHub-first route is complete only when a clean external user can reproduce
an immutable release on both supported hosts, obtain exact readback, retry safely,
change their profile without accidental removal, and start a real research task.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|---|---|---|---:|---|---|
| CEO Review | `/plan-ceo-review` | Scope and strategy | 0 | Not run | Product direction was already fixed by the user |
| Codex Review | `/codex review` | Independent second opinion | 0 | Not run | Local source and real-host evidence used |
| Eng Review | `/plan-eng-review` | Architecture and tests | 1 | CLEAR | 5 issues folded into the plan; 0 critical gaps |
| Design Review | `/plan-design-review` | UI and interaction | 0 | Deferred | Run during R7 application-facing work |
| DX Review | `/plan-devex-review` | Clean-user installation | 0 | Deferred | Run during R6 public acceptance |

**VERDICT:** ENG CLEARED for phased implementation. Full scope is split into
seven bounded releases; R1 is the active implementation unit.

NO UNRESOLVED DECISIONS
