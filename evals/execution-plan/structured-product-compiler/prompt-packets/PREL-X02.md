# Zero-context Worker Packet — PREL-X02

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
atom                PREL-X02 / X
planner subject     b14da457a71456bfa27e814b6e92fa9468b86095480daa7b8abf61705904c349
parent Stage 6      34f77140968799c0c2669610609848beadf96646
branch              prel/62-structured-scene-runtime-canary
base branch          prel/61-scene-deterministic-evals
lane                 LOCAL
```

Objective:
Exercise one bounded owned local workflow using only the deterministic SceneSpec and validator.

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
- `scripts/run_structured_scene_canary.py`
- `evals/structured-scene/runtime/**`

Consumed paths/contracts:
- `src/ai_product_notes/scene_spec.py`
- `src/ai_product_notes/constraint_validator.py`
- `evals/structured-scene/deterministic/**`

Start dependencies:
- PREL-E02_RECEIPT_READABLE
- LOCAL_CLEAN_CHECKOUT_AVAILABLE

Completion dependencies:
- PREL-E02_RECEIPT_PASS
- LOCAL_RUNTIME_RECEIPT_PASS

Oracle:
A clean local checkout executes one complete structured-state→validation workflow and emits an exact input/output/receipt digest with cleanup.

Negative controls:
- hosted CI cannot impersonate local runtime
- exit zero without receipt is insufficient
- dirty workspace blocks execution
- rendering/provider remains out of scope

Budget:
- maximum hours: 2
- maximum leased path entries: 3

Rollback:
Delete runtime canary artifacts and keep deterministic C/K/E receipts unchanged.

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
