# Zero-context Worker Packet — PREL-E02

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
atom                PREL-E02 / E
planner subject     b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
parent Stage 6      34f77140968799c0c2669610609848beadf96646
branch              prel/61-scene-deterministic-evals
base branch          prel/60-constraint-validator
lane                 CLOUD
```

Objective:
Run positive, negative and mutation controls for the deterministic scene compiler wedge.

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
- `tests/test_structured_scene_e2e.py`
- `evals/structured-scene/deterministic/**`

Consumed paths/contracts:
- `src/ai_product_notes/scene_spec.py`
- `src/ai_product_notes/constraint_validator.py`

Start dependencies:
- PREL-K03_INTERFACE_BYTES_READABLE

Completion dependencies:
- PREL-C02_RECEIPT_PASS
- PREL-K03_RECEIPT_PASS
- DETERMINISTIC_EVAL_RECEIPT_PASS

Oracle:
All three canonical edits pass round-trip and all planted invalid/mutation cases fail with the expected stable receipt state.

Negative controls:
- green unit tests cannot satisfy runtime lane
- one passing edit cannot satisfy three-case denominator
- mutation must invalidate old receipt
- failure cases remain in denominator

Budget:
- maximum hours: 4
- maximum leased path entries: 3

Rollback:
Remove deterministic eval artifacts without changing C/K implementation bytes.

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
