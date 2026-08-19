# Technical Systems Eval Agent Contract

This directory owns Stage 5 technical-systems packets compiled from exact Stage 4 dossiers. It does not own root repository convergence, roadmap admission, merge, release, production promotion, user validation, or legal approval.

## Mandatory read order

1. repository root `AGENTS.md`;
2. `docs/STATE_MACHINES.md`;
3. owning Issue and current PR/branch/check graph;
4. the exact Stage 4 dossier and its nearest `AGENTS.md` / README;
5. this directory `AGENTS.md`;
6. target canary README, binding, plan, packet and Shadow review;
7. `src/ai_product_notes/technical_systems.py` and tests.

If the parent dossier commit, blob, digest, or current parent PR head cannot be read back, stop with `BLOCKED_STALE_SUBJECT`.

## State Machine

```text
DOSSIER_REFERENCED
→ EXACT_DOSSIER_BOUND
→ WORKFLOW_DECOMPOSED
→ CAPABILITIES_BOUND
→ TRUE_EDGES_BOUND
→ RIGHTS_SEPARATELY_GATED
→ EVALS_BOUND
→ MVP_TECHNICAL_SLICE_SELECTED
→ PACKET_DIGESTED
→ EXACT_HEAD_HOSTED_VERIFIED
→ SYNTHETIC_MERGE_VERIFIED
→ DOWNSTREAM_START_ADMITTED | BLOCKED
```

## Evidence laws

- Stage 5 may design an implementable packet; it cannot claim the implementation exists.
- Every capability must have owner, inputs, outputs, boundary, transitions, oracle, failure state and rollback.
- Dependencies must form a DAG. Independent capabilities remain siblings.
- Rights for code, model weights, datasets, trajectories, hosted services and third-party content are evaluated separately.
- A `PASS` right requires direct evidence for that exact asset/scope; unresolved rights remain `UNKNOWN` or `NOT_APPLICABLE`.
- Runtime probes marked `NOT_EXERCISED` cannot satisfy technical verification.
- The MVP technical slice must test the dossier's riskiest assumption and remain bounded; optional rendering/provider scope cannot rescue a weak deterministic wedge.
- `VALIDATE` is the maximum automated decision for this canary.
- CI green proves only the exact repository subject and owned deterministic contracts.

## Writer boundary

For Issue #51 the writable lease is limited to:

```text
src/ai_product_notes/technical_systems.py
scripts/compile_technical_systems_packet.py
schemas/technical-systems-*.schema.json
tests/test_technical_systems_packet.py
evals/technical-systems/**
```

Root `README.md`, root `AGENTS.md`, roadmap indexes, shared Git indexes and other Issue-owned paths remain convergence-owner surfaces.
