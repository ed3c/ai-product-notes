# Zero-context Worker Packet — PREL-K03

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
atom                PREL-K03 / K
planner subject     b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
parent Stage 6      34f77140968799c0c2669610609848beadf96646
branch              prel/60-constraint-validator
base branch          prel/59-scene-spec-contract
lane                 CLOUD
```

Objective:
Implement deterministic constraint validation over the admitted SceneSpec interface.

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
- `src/ai_product_notes/constraint_validator.py`
- `tests/test_constraint_validator.py`

Consumed paths/contracts:
- `src/ai_product_notes/scene_spec.py`
- `schemas/scene-spec.schema.json`

Start dependencies:
- PREL-C02_INTERFACE_BYTES_READABLE

Completion dependencies:
- PREL-C02_RECEIPT_PASS
- CONSTRAINT_VALIDATOR_RECEIPT_PASS

Oracle:
Valid scenes yield digest-bound PASS receipts; planted missing assets, invalid bounds and conflicting constraints fail with stable rule identifiers.

Negative controls:
- validator cannot mutate SceneSpec
- unknown rules fail closed
- receipt for old scene digest becomes stale
- no probabilistic backend required

Budget:
- maximum hours: 5
- maximum leased path entries: 2

Rollback:
Remove validator paths while retaining the admitted SceneSpec contract.

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
