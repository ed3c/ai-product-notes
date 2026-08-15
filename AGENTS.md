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

Read the repository README, architecture, tests, workflows, and nearest local instructions before implementation. Preserve repository-specific evidence and authority boundaries.

## Repository-specific Market-to-MVP routing

This public repository owns **market-signal normalization, opportunity compilation, roadmap admission and privacy-preserving implementation handoff**. It does not own every downstream runtime, private capability, security system, Skill qualification harness or product deployment.

### Mandatory read order

1. `README.md` — current materialization, directory ownership, data flow and Stack PR index.
2. `docs/CONFIG.md` — fixed monitoring, scoring, privacy and delivery policy.
3. `docs/STATE_MACHINES.md` — allowed transitions and fail-closed edges.
4. `docs/MARKET_SIGNAL_CONTRACT.md` — demand evidence, stack decomposition and license gates.
5. `CONTEXT.md`, `RANK.md`, `docs/DATA_MODEL.md` — existing research and asset evidence.
6. `docs/git/README.md`, `docs/git/REPO_PROFILE.md`, `docs/git/WORKER_PROTOCOL.md`, `docs/git/STACKED_PRS.md` — branch graph and Worker authority.
7. The assigned Issue/work packet and the nearest README for every writable path.

### Operating laws

- Classify the requested change as `DATA_INCREMENT_LANE` or `PRODUCT_CHANGE_LANE` before writing.
- A launch, funding announcement, pricing page or GitHub star count is a signal; it is not paid demand.
- Bind freshness, independent evidence groups, buyer pain, recurrence, willingness-to-pay evidence and distribution before promoting an opportunity.
- Decompose each product into capabilities. Validate code, model weights, datasets, trajectories, hosted services and third-party content rights separately.
- Only a direct `PASS` right may count toward substitution coverage. `CONDITIONAL`, `UNKNOWN`, `REJECT`, `NOT_APPLICABLE` and `NOT_EXERCISED` remain distinct.
- A commercially permissive top-level code license is not proof that bundled models, data, trajectories, hosted services, patents, trademarks or third-party content are reusable.
- Public outputs may contain only public repository facts and sanitized private capability envelopes. Never emit private repository names, paths, URLs, code, raw traces, customer data, credentials, tokens or secret-bearing receipts.
- Private capability envelopes may expose only: `capability_id`, `contract_version`, `state`, `evidence_label`, `receipt_digest`, `exportable`, and non-sensitive `limitations`.
- Portfolio matching proves candidacy, not technical equivalence. A candidate becomes equivalent only after the owning runtime produces subject-bound evidence.
- Generated MVP packets remain `VALIDATE` until buyer/pilot receipts satisfy the declared success metrics. Do not manufacture `BUILD`, `PAID`, `MARKET_VALIDATED` or `DONE`.
- Architecture, schemas, code, tests, roadmap policy and shared indexes use Issue-first reviewable branches. Routine data automation may use the bounded data lane only when its exact workflow, file scope and verification are already admitted.
- Git Town is a synchronization engine, not merge authority. No `.git-town.toml`, live-sync claim or automated ship is allowed while exact executable admission and live canaries are absent.
- One Worker owns one mutable branch and path lease. Independent writable paths are sibling branches; shared indexes have one convergence owner.
- Preserve these evidence states: `ABSENT`, `PLANNED`, `MATERIALIZED`, `TESTED`, `PUBLISHED`, `MERGED`, `PHYSICALLY_EXECUTED`, `VERIFIED`, `ADMITTED`, `BLOCKED`, `NOT_EXERCISED`.

### Required completion report

Every product-change completion report must include the exact Issue, branch, parent, head SHA, path lease, validation commands/results, negative controls, publication state, remaining gaps, non-claims and rollback subject. GitHub publication, hosted CI, live Git Town sync, market validation and Human Admit are separate lanes.
