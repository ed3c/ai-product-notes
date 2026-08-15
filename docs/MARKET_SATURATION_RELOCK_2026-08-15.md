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

## Current market evidence

| Surface | Current evidence | Implication |
|---|---|---|
| OpenAPI breaking-change detection | [OASDiff breaking-change engine](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md) is explicitly designed for CI breaking/changelog detection | spec diff is not a defensible standalone wedge |
| Protobuf breaking-change detection | [Buf breaking-change tooling](https://github.com/marketplace/actions/buf-breaking) provides CI detection and PR annotations | schema compatibility is already a mature category |
| GitHub Marketplace | [Detect Breaking Changes](https://github.com/marketplace/actions/detect-breaking-changes) compares OpenAPI specs in PR CI | another generic GitHub Action has low differentiation |
| Generic agent trace replay | [agent-replay](https://github.com/clay-good/agent-replay) records/replays traces and provides structural CI regression gates | generic trajectory replay is also not unique |
| Agent snapshot / simulation | [eval-view](https://github.com/hidai25/eval-view) provides golden traces, record/replay cassettes and CI simulation | the wedge must be narrower than generic agent eval/replay |

These links are competitive-substitution evidence only. They do not prove buyer demand for this repository's narrower candidate.

## Why this is different

Generic agent replay products already compare traces, tool inputs and outcomes. The candidate here is not another trace viewer. It treats **contract evolution** as the changed subject and historical successful trajectories as executable compatibility evidence.

The intended join is:

```text
contract delta
× historically exercised procedural calls
× exact runtime subject
→ affected behavior set
```

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
3. **Substitution evidence** — at least one evaluation demonstrates that composing generic replay tooling with existing schema-diff tooling does not already solve the workflow with similar accuracy and review effort.

## Stop-loss

Reject or reduce the scope if generic replay tools already solve the contract-evolution workflow without meaningful integration cost, or if real teams cannot provide recurring historical contract failures that materially affected delivery.

## Evidence boundary

This document records a market relock decision. It is not customer evidence, a paid pilot, production validation, or proof that the replay algorithm is correct.