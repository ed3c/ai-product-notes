# Structured Product Compiler — Stage 7 Execution Plan

Read `../AGENTS.md` before mutation.

This canary consumes the exact hosted-verified Stage 6 closure audit and compiles
a **planning-only** Molecular Stack. It does not execute the product.

## Exact input

```text
Stage 6 PR/head   #57 / 34f77140968799c0c2669610609848beadf96646
audit digest      sha256:d221ec2b1b4dee513352571fd10572ce54f5e72e6f081f4491db98498f175b1a
matrix blob       f33e4c41d85086ef307f8507a02ae39657b8bd3d
audit blob        2df084ca9d6e4afdecad392a0918636810d004cc
delta blob        2ce7a4723282fa1f9e552a4b0597d32942696cfc
Shadow blob       9646bc10015d21d5256ef866a2627b7e62f71f45
hosted run        32276039761 / PASS

skills-shared     4ca9417b1da5ff32f1d4d3e7af64a15908749024
prompt schema     34a53c57d7f8bebb5add25e97e87e27be1436c25
prompt catalogue  95eaa6a2d69ee53aa4c3d34a84b180cb0b619f2d
stack schema      2fb9eb4ecf5d641dd96189f581296b6c6541a734
```

## State Machine

```text
STAGE6_AUDIT_BOUND
→ MOLECULAR_ATOMS_BOUND
→ DUAL_DEPENDENCY_DAG_BOUND
→ DISJOINT_PATH_LEASES_BOUND
→ ISSUE_RECONCILIATION_BOUND
→ ZERO_CONTEXT_PROMPTS_BOUND
→ LOCAL_HANDOFF_BOUND
→ HOSTED_VERIFIED | BLOCKED
```

## Planned Molecular Stack

```text
PREL-C02 SceneSpec contract / canonical digest
└── PREL-K03 deterministic constraint validator
    └── PREL-E02 positive + negative + mutation controls
        └── PREL-X02 owned local runtime canary
            └── PREL-D02 single documentation/index convergence owner
```

The probabilistic rendering/provider adapter is deliberately **not admitted**
into this MVP Stack. It remains a future adapter/right-selection problem.

## Dual-edge rule

Each atom carries two independent lists:

```text
start_dependencies
completion_dependencies
```

A readable parent interface may permit a child to start. It cannot make the
parent complete. `GitHub blocked-by` is suitable only for completion
dependencies; `execution-dag.json` preserves both classes.

## Existing Issue reconciliation

The planner binds existing #33, #34, #35, #38 and #43 rather than cloning them.
#33/#34 currently target the existing Agent Contract Evolution Replay product,
so they cannot be reused as evidence for this structured-product canary.
#35/#38 remain global hosted/runtime policy references. #43 remains a repository
meta-index. Any future market/adoption issue for this canary requires a separate
product-admission decision rather than silent reuse or duplication.

## Outputs

```text
run-contract.json
execution-dag.json
issue-plan.json
path-leases.json
stack-plan.json
prompt-packets/*.md
local-handoff-queue.json
shadow-review.json
```

Planner subject digest:

```text
b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
```

Run contract digest:

```text
e8555b5f98d73c29d2976b37d5695e96fb2b3a964591111bb37ecbd2eb0c078f
```

DAG digest:

```text
8882635fc7d0c227d234f66de31c8b8572a019195ff36b834d717ad0aa378b18
```

## Local Handoff

Exactly one item is active:

```text
LH-S7-VERIFY  ACTIVE
LH-S8-C02     BLOCKED_BY_PREDECESSOR
```

Hosted CI and a zero-context prompt packet are not local execution receipts.

## Evidence boundary

Stage 7 may prove only that a deterministic planning packet exists and passes its
owned repository contracts. `IMPLEMENTED`, runtime, user, paid, rights, merge,
release and production remain outside this stage.
