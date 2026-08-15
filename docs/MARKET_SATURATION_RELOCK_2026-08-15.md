# Market Saturation Relock — 2026-08-15

## Decision

The generic `Vendor API Blast-Radius CI` wedge remains `VALIDATE`, but is now classified as `SATURATED_RELOCK_REQUIRED`.

Fresh market review found mature substitutes for spec-level breaking-change detection, including OASDiff, Buf and existing GitHub Marketplace actions. Building another generic API diff product would therefore duplicate an established category.

The narrower candidate is **Agent Contract Evolution Replay CI**:

```text
known-good agent trajectory
+ old tool / skill / harness contract
+ candidate new contract
→ deterministic replay
→ identify historical procedural calls that no longer satisfy the contract
→ subject-bound regression receipt
→ admit or reject the harness upgrade
```

## Why this is different

Generic agent replay products already compare traces, tool inputs and outcomes. The candidate here is not another trace viewer. It treats **contract evolution** as the changed subject and historical successful trajectories as executable compatibility evidence.

The first thin slice only detects contract-level breakage:

- tool removed;
- newly required argument missing from an old successful call;
- previously used enum value no longer admitted;
- historical tool call absent from the declared contract.

It intentionally does not infer semantic equivalence, repair calls, invoke an LLM, or claim production safety.

## Market state

```text
Vendor API generic detector: SATURATED_RELOCK_REQUIRED
Agent Contract Evolution Replay CI: VALIDATE
customer-origin evidence: ABSENT
paid demand: ABSENT
real historical replay receipts: ABSENT
hosted product: NOT_ADMITTED
```

## Promotion gate

Do not promote the replay candidate to `BUILD` until both sides of the thesis pass:

1. **Problem evidence** — at least 3 qualified teams confirm recurring pain from agent/tool/skill contract evolution and identify a budget owner or equivalent binding adoption path.
2. **Runtime evidence** — at least 5 independently adjudicated historical breakages are detected from exact contract + trajectory subjects with acceptable false-positive/unknown rates.

## Stop-loss

Reject or reduce the scope if generic replay tools already solve the contract-evolution workflow without meaningful integration cost, or if real teams cannot provide recurring historical contract failures that materially affected delivery.

## Evidence boundary

This document records a market relock decision. It is not customer evidence, a paid pilot, production validation, or proof that the replay algorithm is correct.