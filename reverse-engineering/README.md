# Product Reverse-Engineering Control Plane

This directory routes the repository-owned Product Reverse-Engineering loop. The original Stage 1 packet remains under `runs/` as immutable preparation evidence; current integrated status is owned by the post-merge traceability overlay.

## Current authority

```text
convergence PR     #67
merge              8a63575492b07daf8e1f62432181e6dc2f2b6960
current overlay    docs/traceability/PRODUCT_REVERSE_CLOSURE.md
machine overlay    docs/traceability/product-reverse-closure.json
current handoff    docs/traceability/local-handoff-execution-queue.json
state              POST_MERGE_RECONCILED_WITH_OPEN_PRODUCT_GATES
```

Do not use `runs/prel-2026-08-18-control-binding/` as current implementation state. It records the exact Stage 1 preparation subject and remains useful for provenance, but it predates the merged dossier, technical, closure, planner, SceneSpec, validator, deterministic eval and local runtime artifacts.

## Mandatory read order

1. root `AGENTS.md`;
2. root `README.md`;
3. current Issue #68 and Epic #44;
4. `docs/traceability/PRODUCT_REVERSE_CLOSURE.md`;
5. `docs/traceability/product-reverse-closure.json`;
6. `docs/traceability/local-handoff-execution-queue.json`;
7. the owning `evals/*/AGENTS.md` and exact artifact;
8. current GitHub Issue/PR/check metadata;
9. historical `runs/` or generated matrices only when their captured subject is being audited.

## Directory → State Machine → owner

| Path | Owner | State Machine | Input | Output / receipt | Evidence ceiling |
|---|---|---|---|---|---|
| `runs/` | Control Binder | `REQUEST_BOUND → CONTEXT_ADMISSION_READY` | exact repos/issues/sources | immutable preparation packets | planning only |
| `evals/reverse-engineering/` | Product Reverse Worker | `PRODUCT_SIGNAL_BOUND → DOSSIER_BOUND` | exact product signal | dossier + hypotheses + binding | `VALIDATION_DESIGN_ONLY` |
| `evals/technical-systems/` | Systems Architect | `DOSSIER_BOUND → TECHNICAL_SYSTEMS_BOUND` | dossier | capability DAG, rights/eval plan | `TECHNICAL_DESIGN_ONLY` |
| `evals/problem-closure/` | read-only Shadow | `SUBJECTS_BOUND → CLOSURE_AUDITED` | dossier + technical packet | historical matrix/audit/delta | `FINDINGS_ONLY` |
| `evals/execution-plan/` | Tech Lead | `CLOSURE_AUDITED → EXECUTION_PLANNED` | verified gaps | historical dual-edge DAG/leases/prompts/queue | `PLANNING_ONLY` |
| `scene_spec.py` + schema/tests | C02 Worker | `INTERFACE_BOUND → SCENE_SPEC_BOUND` | deterministic MVP contract | canonical scene bytes/digest | implementation atom only |
| `constraint_validator.py` + tests | K03 Worker | `SCENE_SPEC_BOUND → CONSTRAINT_VALIDATED` | SceneSpec | stable violations and receipt | deterministic implementation only |
| `evals/structured-scene/deterministic/` | E02 Worker | `C/K_BOUND → DETERMINISTIC_EVAL_VERIFIED` | exact C/K bytes | seven-case receipt | deterministic eval only |
| `evals/structured-scene/runtime/` | local X02 Worker | `CLEAN_CHECKOUT → LOCAL_WORKFLOW_VERIFIED` | exact local subject | runtime receipt + cleanup | local runtime atom only |
| `docs/traceability/` | D03 convergence owner | `CURRENT_MAIN_BOUND → POST_MERGE_RECONCILED` | current tree, receipts, issues | current closure and handoff | reconciliation only |

## End-to-end data flow

```text
exact Evidence Plane product-signal
→ reverse-engineering dossier
→ technical systems / capability DAG
→ Shadow closure audit
→ dual-edge Molecular plan
→ SceneSpec C atom
→ deterministic validator K atom
→ fixed E denominator
→ local X runtime receipt
→ PR #67 convergence merge
→ current D03 closure overlay
→ remaining Google / multi-canary / rights / user / paid handoffs
```

## Current real-problem closure

```text
structured AST / SceneSpec        LIVE_WORKFLOW_VERIFIED (bounded local)
deterministic constraints         LIVE_WORKFLOW_VERIFIED (bounded local)
receipt invalidation on mutation  LIVE_WORKFLOW_VERIFIED (bounded local)
bidirectional canvas              NOT_IMPLEMENTED
rendering farm                    NOT_IMPLEMENTED
product grounding/floating        NOT_IMPLEMENTED
perspective/depth correction      NOT_IMPLEMENTED
lighting/contact shadow           NOT_IMPLEMENTED
latency/cost benchmark            NOT_EXERCISED
exact dependency rights           HUMAN_ADMIT_REQUIRED
qualified-user value              ABSENT
paid demand                       ABSENT
```

The source PDF supplies problem/mechanism hypotheses, not observed named-company internals. Exact closure rows and evidence subjects are in `docs/traceability/product-reverse-closure.json`.

## Historical vs current artifacts

- `evals/problem-closure/.../problem-closure-matrix.json` is the Stage 6 captured state before implementation atoms completed.
- `evals/execution-plan/.../local-handoff-queue.json` is the Stage 7 captured queue before local X02 and convergence.
- Both remain valid historical evidence and must not be edited to pretend they were generated later.
- The current overlay and queue under `docs/traceability/` are the only present routing authority.

## Hard boundaries

- Merge of code does not close user, paid, legal or production lanes.
- The X02 receipt covers one local deterministic SceneSpec→validation workflow only.
- No rendering/model/provider dependency was selected or exercised.
- No bidirectional editor/canvas implementation exists.
- Google projection remains separate under Issue #48 and `ai-content-notes#41`.
- Three-product PDF canary coverage remains incomplete under Issue #49.
- `skills-shared#443` remains a local provenance blocker and the first ACTIVE handoff.
