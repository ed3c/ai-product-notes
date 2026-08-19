# Product Reverse-Engineering Preparation

This directory is the repository-owned Product Control Plane workspace for the
cross-repository Product Reverse-Engineering Closure Loop.

## Current exact preparation

```text
run_id: prel-2026-08-18-control-binding
control issue: #52
parent main: dcef8e57a4ec74be3ff843defa82d53e213719af
parent tree: ef43f7a7a35f14ede0e56edefc05a6e0ff6e5d36
runtime: CHATGPT_GITHUB_CONNECTOR
state: CONTEXT_ADMISSION_READY_WITH_DECLARED_GAPS
```

The exact Draft branch head and tree are recorded in Pull Request metadata and
the Issue #52 handoff comment. They are not self-embedded into repository bytes.

## Mandatory read order

1. root `AGENTS.md`;
2. root `README.md`;
3. Issue #52 and parent Epic #44;
4. this README;
5. the current run artifacts under `runs/prel-2026-08-18-control-binding/`;
6. current GitHub Issues, PRs, checks and exact subjects;
7. the owning repository's nearest instructions before any downstream mutation.

## Directory → State Machine → authority

| Path | Owner | State Machine | Inputs | Outputs | Evidence ceiling |
|---|---|---|---|---|---|
| `runs/prel-2026-08-18-control-binding/run-contract.json` | Stage 1 Control Binder | `REQUEST_BOUND → CONTEXT_ADMISSION_READY` | request, exact repos, issues, sources | bounded run contract | connector read-back and Draft publication |
| `repo-role-map.json` | Tech Lead | `REPOSITORIES_OBSERVED → ROLE_OWNERS_BOUND` | exact commits/trees/PR inventory | five-plane ownership | no runtime or market proof |
| `source-pointer-registry.json` | Evidence routing | `SOURCE_REFERENCED → POINTER_BOUND` | Drive/GitHub URLs and revisions | source pointers and authority ceilings | not source admission |
| `closure-targets.json` | Shadow + Tech Lead | `CLAIM_BOUND → MINIMUM_LANE_BOUND` | claims and evidence classes | required closure levels | findings only |
| `capability-plan.json` | Tech Lead | `CAPABILITY_PLAN_COMPILED → CONTEXT_ADMISSION_READY` | required tools and runtime | selected/fallback capabilities | no unavailable capability promotion |
| `execution-dag.json` | Tech Lead | `ISSUES_BOUND → DUAL_EDGES_BOUND` | existing issues | start/completion DAG | plan only |
| `path-leases.json` | Tech Lead | `WRITER_IDENTIFIED → LEASE_ADMITTED` | tree/PR inventory | active/proposed leases | one Draft writer |
| `shadow-baseline.json` | read-only Shadow | `SUBJECT_BOUND → FINDINGS_HANDOFF` | exact repos, docs and source | contradictions/blockers | same-context advisory |
| `prompt-packets/` | Tech Lead | `TASK_BOUND → WORKER_PACKET_READY` | run contract and Issue | zero-context Worker prompt | no execution proof |

## Data flow

```text
exact GitHub repositories + Issue graph + Google Doc revision + PDF pointer
→ read-only Shadow contradiction and evidence-lane audit
→ exact repository roles and closure targets
→ capability plan with unavailable lanes preserved
→ dual-edge Issue DAG and disjoint path leases
→ Stage 2 / Stage 3 zero-context Worker packets
→ Draft publication and Git read-back
→ typed local validation handoff
```

## Hard boundaries

- Google Docs and PDFs are source/projection inputs, not completion authority.
- Product-internal technology mappings from the PDF remain source statements or
  hypotheses until independently observed.
- Stage 1 preparation does not implement the Evidence Plane or Product compilers.
- Local tests, Git Town, Forgejo, independent Shadow, provider execution,
  customer evidence, paid adoption, merge and release remain separate.
- Root README, root AGENTS and shared indexes are owned by convergence Issue #50.
