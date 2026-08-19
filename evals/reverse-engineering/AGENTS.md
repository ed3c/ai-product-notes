# Reverse-Engineering Eval Agent Contract

This directory owns **source-constrained product reverse-engineering canaries**.
It does not own root repository convergence, shared indexes, market validation,
merge, release, or production promotion.

## Mandatory read order

Before changing a canary under this directory, read:

1. repository root `AGENTS.md`;
2. `docs/STATE_MACHINES.md`;
3. the owning GitHub Issue and current PR/branch/check graph;
4. the target canary `README.md`;
5. `external-binding.json` and the exact upstream packet it names;
6. `product-signal.input.json`;
7. `hypotheses.json`;
8. `dossier.json` and `shadow-review.json` if materialized;
9. `src/ai_product_notes/reverse_engineering.py` and its tests.

If the external Git subject, blob, digest, source digest, or current upstream PR
head cannot be read back, stop with `BLOCKED_STALE_SUBJECT`. Do not infer
freshness from issue comments, PR prose, or prior chat context.

## State Machine

```text
EXTERNAL_PACKET_REFERENCED
→ EXACT_GIT_BLOB_BOUND
→ LOCAL_SNAPSHOT_VERIFIED
→ HYPOTHESES_BOUND
→ DOSSIER_COMPILED
→ NEGATIVE_CONTROLS_PASS
→ EXACT_HEAD_HOSTED_VERIFIED
→ SYNTHETIC_MERGE_VERIFIED
→ DOWNSTREAM_START_ADMITTED | BLOCKED
```

## Evidence laws

- An upstream `SOURCE_PATTERN` may remain a source-backed mechanism statement.
- `MECHANISM_HYPOTHESIS` cannot become observed named-product architecture.
- `UNKNOWN` claims and unresolved contradictions cannot disappear.
- user, buyer, pain, frequency, cost, workaround, distribution, monetization,
  retention, and defensibility remain `HYPOTHESIS | UNKNOWN` until direct
  evidence is bound.
- rights cannot become `PASS` without the corresponding direct legal/right
  evidence lane.
- `VALIDATE` is the maximum automated decision for the current Stage 4 canary.
- CI green proves only the exact repository subject and owned deterministic
  contracts. It cannot prove source truth, runtime quality, user value, paid
  demand, PMF, merge, release, or production readiness.

## Writer boundary

One Worker owns one mutable branch. For Issue #45 the current implementation
lease is limited to:

```text
src/ai_product_notes/reverse_engineering.py
scripts/compile_reverse_engineering_dossier.py
schemas/reverse-engineering-*.schema.json
tests/test_reverse_engineering_dossier.py
evals/reverse-engineering/**
```

Root `README.md`, root `AGENTS.md`, roadmap indexes, shared Git indexes, and
other Issue-owned paths are convergence-owner surfaces and must not be edited by
this Worker.

## Downstream handoff

A hosted-verified exact dossier may satisfy only the **start dependency** of the
technical-systems stage. The downstream Worker must consume the dossier by exact
Git blob/digest and create its own completion receipt. Start admission is not
implementation completion.
