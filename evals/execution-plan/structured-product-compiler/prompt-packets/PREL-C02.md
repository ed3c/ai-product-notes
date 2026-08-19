# Zero-context Worker Packet — PREL-C02

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
surface             STAGE_8_MOLECULAR_WORKER
atom                PREL-C02 / C
planner subject     b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
parent Stage 6      34f77140968799c0c2669610609848beadf96646
branch              prel/59-scene-spec-contract
base branch          prel/58-execution-plan
lane                 CLOUD
```

Objective:
Materialize owned SceneSpec schema, canonical serialization and digest contract.

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
- `schemas/scene-spec.schema.json`
- `src/ai_product_notes/scene_spec.py`
- `tests/test_scene_spec_contract.py`

Consumed paths/contracts:
- `evals/execution-plan/structured-product-compiler/run-contract.json`
- `evals/technical-systems/modern-web-architecture/technical-systems-packet.json`

Start dependencies:
- STAGE7_EXACT_PLAN_READABLE

Completion dependencies:
- SCENE_SPEC_CONTRACT_RECEIPT_PASS

Oracle:
Three canonical scene objects serialize byte-stably, round-trip without state repair, and reproduce the same SHA-256 digest.

Negative controls:
- unknown scene fields rejected
- canonical key ordering cannot drift
- digest changes after semantic mutation
- no rendering/provider dependency enters the core

Budget:
- maximum hours: 4
- maximum leased path entries: 3

Rollback:
Delete the candidate SceneSpec paths and return to the Stage 7 planning subject.

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
