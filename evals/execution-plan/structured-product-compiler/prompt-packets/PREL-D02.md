# Zero-context Worker Packet — PREL-D02

## Common system envelope

You are executing a bounded Product Reverse-Engineering implementation packet.
Do not use prior conversation as contract evidence. Read repository `AGENTS.md`,
the owning Issue, nearest README, and exact Stage 7 plan before mutation.
Preserve `PASS`, `FAIL`, `ABSENT`, `NOT_IMPLEMENTED`, `NOT_EXERCISED`,
`SKIPPED_BY_POLICY`, and `HUMAN_ADMIT_REQUIRED` as distinct states.
Do not reveal private chain of thought. Findings and receipts only.
You have no merge, permission, secret, rights, production, user-truth,
commercial-truth, or release authority.

## Packet

```text
surface             STAGE_9_CONVERGENCE_OWNER
atom                PREL-D02 / D
planner subject     b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
parent Stage 6      34f77140968799c0c2669610609848beadf96646
branch              prel/63-structured-product-convergence
base branch          prel/62-structured-scene-runtime-canary
lane                 CLOUD
```

Objective:
Converge README/AGENTS/State Machine/DAG/Stack indexes after admitted implementation receipts exist.

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
- `docs/architecture/STRUCTURED_PRODUCT_COMPILER.md`
- `docs/git/STACKED_PRS.md`

Consumed paths/contracts:
- `schemas/scene-spec.schema.json`
- `src/ai_product_notes/scene_spec.py`
- `src/ai_product_notes/constraint_validator.py`
- `evals/structured-scene/deterministic/**`
- `evals/structured-scene/runtime/**`

Start dependencies:
- ALL_ADMITTED_LEAF_RECEIPTS_READABLE

Completion dependencies:
- PREL-C02_RECEIPT_PASS
- PREL-K03_RECEIPT_PASS
- PREL-E02_RECEIPT_PASS
- LOCAL_RUNTIME_RECEIPT_PASS
- CONVERGENCE_READBACK_PASS

Oracle:
Every documented state, branch and receipt resolves to an exact subject; no remaining lane is promoted beyond its evidence.

Negative controls:
- shared index has exactly one writer
- missing receipt stays missing
- user/paid/rights remain separate
- no merge/release claim

Budget:
- maximum hours: 2
- maximum leased path entries: 2

Rollback:
Revert only the convergence documentation commit; preserve implementation and receipts.

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
