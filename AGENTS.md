# Repository Agent Instructions

<!-- BEGIN SKILLS-SHARED INSTRUCTION PROJECTION -->
## Shared runtime / delivery projection

Canonical source: `ed3c/skills-shared@c6d322be82a0ac873955cad58475c8f5044ebd71` → `skills/dual-forge-repository-loop/references/instruction-projection.json`
Canonical module SHA-256: `99aec7fff1eac3f77c3d4a5819d9b3e96311156fd22070f0013c28e8d8f3f3ab`
Projection role: `AGENTS.md` — Cross-host repository entrypoint. Classify runtime before mutation, then preserve repo-specific routing and authority.

Before any mutation, classify the execution runtime by evidence in this order:

1. trusted explicit AGENT_RUNTIME/AGENT_HOST override
2. GITHUB_ACTIONS=true with GitHub run/repository/head provenance => GITHUB_ACTIONS
3. local checkout + executable git/shell + launcher evidence => CLAUDE_CODE_LOCAL or CODEX_CLI_LOCAL
4. Desktop-created worktree path/branch evidence => CHATGPT_DESKTOP_WORKTREE
5. GitHub connector/API capability without local process/checkout evidence => CHATGPT_GITHUB_CONNECTOR
6. otherwise => UNKNOWN

Mandatory laws:

- Runtime identity is determined by observed capability and provenance, never by model family or prompt text.
- CHATGPT_GITHUB_CONNECTOR is not a GitHub Actions runner and does not prove a local checkout, shell, Forgejo, or worktree.
- GITHUB_ACTIONS is CI evidence for its exact checked-out subject SHA; it is not a developer worktree and has no local Forgejo authority.
- Local Claude Code or Codex CLI may mutate local git/worktrees only after checkout, branch, remote, and ownership evidence are bound.
- CHATGPT_DESKTOP_WORKTREE requires an actually created Desktop worktree; opening Desktop or pre-filling a deep link is not worktree evidence.
- UNKNOWN fails closed for irreversible delivery actions.
- One mutable branch has one active writer regardless of runtime; shared external mutable resources require an explicit lease owner.
- Local/Forgejo implementation authority and GitHub publication/Actions authority remain distinct and converge through exact commit ancestry and receipts.
- Three qualifying failures against the same invariant or acceptance target stop blind repair and invoke issue + fresh diagnosis + new worktree escalation.
- Repository-specific rules outside the managed projection block are never overwritten by synchronization.
- AGENTS.md is the cross-host repository procedure; repo CLAUDE.md is a Claude host adapter; global ~/.claude/CLAUDE.md is local host policy only.
- Cloud and local freshness are separate evidence lanes. Neither environment may fabricate verification of the other.
- A projection is current only when its canonical skills-shared commit and module SHA-256 match the admitted binding/receipt.
- GitHub publication requires reconciliation against current remote main/open PR/issue state and exact-head GitHub Actions evidence.

Do not edit this managed block manually. Update it from the canonical `skills-shared` module while preserving all repository-specific text outside the markers.
<!-- END SKILLS-SHARED INSTRUCTION PROJECTION -->

Read the repository README, architecture, tests, workflows, nearest local instructions and exact Issue/receipt subjects before implementation.

## Repository-owned control planes

This public repository owns two related but distinct surfaces:

1. **Market-to-MVP Opportunity Compiler** — market signals, demand gates, opportunity scoring, experiments and roadmap admission.
2. **Product Reverse-Engineering Control Plane** — exact product signals, dossiers, capability DAGs, closure audits, molecular implementation plans and bounded technical/runtime receipts.

Neither surface owns customer truth, paid truth, legal admission, every downstream runtime, merge, release or production promotion.

## Mandatory read order

### Common entry

1. `README.md` — current materialization, directory ownership, data flow and current Stack indexes.
2. `docs/STATE_MACHINES.md` and `docs/ARCHITECTURE.md`.
3. The exact owning Issue, current PR graph and checked subject.
4. The nearest `AGENTS.md` and README for every writable path.

### Market-to-MVP work

1. `docs/CONFIG.md`.
2. `docs/MARKET_SIGNAL_CONTRACT.md`.
3. `CONTEXT.md`, `RANK.md`, `docs/DATA_MODEL.md`.
4. `docs/MVP_ROADMAP.md`, `docs/PORTFOLIO_INTEGRATION.md`.
5. `docs/git/README.md`, `REPO_PROFILE.md`, `WORKER_PROTOCOL.md`, `STACKED_PRS.md`.

### Product Reverse work

1. `docs/traceability/PRODUCT_REVERSE_CLOSURE.md` — current post-merge truth overlay.
2. `docs/traceability/product-reverse-closure.json` — machine-readable current closure.
3. `docs/traceability/local-handoff-execution-queue.json` — current executable continuation queue.
4. `reverse-engineering/README.md`.
5. `evals/reverse-engineering/AGENTS.md` and exact dossier packet.
6. `evals/technical-systems/AGENTS.md` and exact technical packet.
7. `evals/problem-closure/AGENTS.md` and the immutable captured Stage 6 packet.
8. `evals/execution-plan/AGENTS.md` and the immutable captured Stage 7 plan.
9. `evals/structured-scene/deterministic/` and `evals/structured-scene/runtime/receipt.json`.
10. `docs/git/STACKED_PRS.md` only as historical delivery evidence.

If the current closure overlay disagrees with an older generated matrix or queue, preserve the old artifact as its captured historical subject and use the current overlay for present routing. Do not silently rewrite historical evidence.

## Market-to-MVP laws

- Classify every change as `DATA_INCREMENT_LANE` or `PRODUCT_CHANGE_LANE` before writing.
- Launch, funding, pricing and GitHub stars are signals, not paid demand.
- Bind freshness, independent evidence groups, buyer pain, recurrence, willingness-to-pay and distribution before promotion.
- Validate code, model weights, datasets, trajectories, hosted services and third-party content rights separately.
- Only direct `PASS` rights count toward substitution coverage.
- Public outputs may contain only public facts and sanitized private capability envelopes.
- Portfolio matching proves candidacy, not technical equivalence.
- Generated MVP packets remain `VALIDATE` until declared buyer/pilot receipts pass.

## Product Reverse laws

- `source statement != observed company truth`.
- A PDF/article product-internal mapping defaults to `SOURCE_STATEMENT`, `HYPOTHESIS` or `UNKNOWN`; it cannot become observed architecture from repetition or compiler output.
- `architecture/design != implementation`.
- `implementation != TECH_VERIFIED` without an exact deterministic oracle and receipt.
- `hosted CI != local runtime`; `local runtime != user validation`; `user validation != paid validation`.
- Structured SceneSpec and deterministic constraint validation have one bounded local workflow receipt. Do not generalize that receipt to bidirectional canvas, rendering, visual quality, provider performance or production.
- Product floating, perspective mismatch, lighting/contact-shadow discontinuity and latency/cost remain open until exact implementations and subject-bound visual/benchmark receipts exist.
- The PDF's “100% permissive” claim remains blocked by its LGPL/MIT qualification until exact selected artifacts and transitive rights are reviewed.
- Historical PRs #53/#54/#55/#57/#59/#61/#63/#65 were superseded as publication vehicles by convergence PR #67. Do not report them as individually merged.
- Historical Stage 6/7 generated files are immutable captured-state evidence. Current state belongs in `docs/traceability/`.
- Exactly one current Local Handoff queue item may be `ACTIVE`.
- Google Docs/Sheets are human projections, never implementation, completion, market, merge or release authority.

## Delivery and writer laws

- Architecture, schemas, code, tests, roadmap policy, root docs and current traceability indexes require Issue-first reviewable branches.
- One Worker owns one mutable branch and path lease.
- Independent writable paths are siblings; shared indexes have one convergence owner.
- Start and completion dependencies are separate. Readable interfaces can open a start edge; only exact receipts close completion edges.
- Git Town is synchronization infrastructure, not merge authority. Do not claim live Git Town execution without executable admission and runtime receipts.
- Preserve these states literally: `PASS`, `FAIL`, `ABSENT`, `NOT_IMPLEMENTED`, `NOT_EXERCISED`, `SKIPPED_BY_POLICY`, `HUMAN_ADMIT_REQUIRED`, `BLOCKED`.
- Merge, semantic conflict, rights/legal admission, customer truth, paid truth, release and production remain externally owned.

## Required completion report

Every product change must report:

```text
Issue / atom / owner
exact base, head and tree
consumed parent subjects
changed paths and lease
commands and results
positive, negative, mutation, fault and runtime evidence states
receipt/blob/digest identities
open contradictions and non-claims
rollback subject
next owner and Local Handoff state
```

Prior conversation, Issue prose, a green badge or a generated prompt is not a completion receipt.
