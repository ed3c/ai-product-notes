# Stage 7 Execution-Plan Agent Contract

This directory owns **Tech Lead planning artifacts** compiled from an exact
Stage 6 closure audit. It does not own product implementation, runtime
execution, user/paid validation, rights admission, merge, release or production.

## Mandatory read order

1. repository root `AGENTS.md`;
2. `docs/STATE_MACHINES.md`;
3. owning Issue `#47`, molecular packet `#58`, and current PR/check graph;
4. exact parent Stage 6 PR/head and closure matrix/audit/delta/Shadow receipt;
5. exact `skills-shared` prompt-packet, prompt-catalogue and Molecular Stack contracts;
6. this `AGENTS.md` and the canary README;
7. `planner-input.json`, generated DAG/leases/issues/stack/queue and prompt packets;
8. `src/ai_product_notes/execution_planner.py` and tests.

If the Stage 6 head/blob/audit digest or pinned `skills-shared` subject cannot be
read back, stop with `BLOCKED_STALE_SUBJECT`. Do not re-point the packet to a
newer subject and do not use prior conversation to fill missing evidence.

## State Machine

```text
STAGE6_AUDIT_BOUND
→ SHARED_PLANNER_CONTRACT_BOUND
→ WORK_GAPS_CLASSIFIED
→ MOLECULAR_ATOMS_BOUND
→ DUAL_DEPENDENCIES_BOUND
→ DISJOINT_LEASES_BOUND
→ ISSUE_PLAN_RECONCILED
→ ZERO_CONTEXT_PROMPTS_COMPILED
→ LOCAL_HANDOFF_COMPILED
→ EXACT_HEAD_HOSTED_VERIFIED
→ SYNTHETIC_MERGE_VERIFIED
→ STAGE8_START_ADMITTED | BLOCKED
```

## Hard laws

- start dependencies and completion dependencies are different edge types;
- a child edge is legal only if the child consumes parent-owned bytes/contracts;
- path-disjoint work is not serialized merely for convenience;
- exactly one convergence owner may write shared indexes;
- one mutable branch has one active writer;
- `PROPOSAL_ONLY` Issue plans have no authority to create/close/merge work by themselves;
- prompt packets and queue entries do not prove a Session or Worker executed;
- existing market/adoption/owner/runtime Issues are reconciled, not duplicated;
- Stage 7 cannot promote implementation, runtime, user, paid, legal or production evidence;
- merge, release, rights, customer truth, commercial truth, production and semantic conflict remain Human-owned.

## Writer boundary

For Issue #58, writes are limited to:

```text
src/ai_product_notes/execution_planner.py
scripts/compile_execution_plan.py
schemas/execution-plan-instance.schema.json
tests/test_execution_plan.py
evals/execution-plan/**
```

Do not write Stage 4/5/6 parent paths, root README/AGENTS, roadmap indexes or
shared Git indexes from this Worker.

## Downstream handoff

A hosted-verified Stage 7 plan may admit the first Stage 8 contract atom only.
It does not admit all atoms simultaneously and it does not satisfy any atom's
completion dependencies. Local execution remains separately receipted.
