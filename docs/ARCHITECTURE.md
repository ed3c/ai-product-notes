# Architecture｜Market-to-MVP Control Plane

## Purpose

The repository separates market intelligence from product execution. It compiles current signals into auditable decisions and hands admitted work to a durable implementation owner. It must not become a monolith that duplicates research acquisition, truth verification, security evaluation, Skill qualification, private portfolio code or production deployment.

## Planes

### 1. Signal Plane

Owns freshness, deduplication, official identity, source class and dated evidence. Existing `notes/`, `reports/` and `data/products/` remain inputs, not proof of demand.

### 2. Decision Plane

Owns capability decomposition, per-asset rights gates, portfolio matching, gaps, deterministic scoring and the `BUILD | VALIDATE | WATCH | REJECT | BLOCKED` decision.

### 3. Experiment Plane

Owns falsifiable hypotheses, a narrow wedge, budget, success metrics, stop-loss and receipt shapes. It does not own production code by default.

### 4. Portfolio Plane

Consumes public capability contracts and optional private capability envelopes. Public and private evidence are never merged into one opaque score.

### 5. Delivery Plane

Uses the canonical shared `git-town-stacked-pr-worker` method plus repository-owned Issues, profiles, path leases, tests, workflows and receipts. Git Town synchronization and GitHub publication are separate evidence lanes.

## Trust boundaries

```text
UNTRUSTED / EXTERNAL
market claims, launch pages, pricing, changelogs, competitor messaging
        │
        ▼
TRUSTED NORMALIZATION
freshness + identity + evidence class + immutable source pointers
        │
        ▼
TRUSTED DECISION CORE
capabilities + rights + portfolio + gaps + deterministic score
        │
        ▼
UNPROVEN HYPOTHESIS
MVP packet and price test
        │
        ▼
EXTERNAL EXECUTION
interviews, historical replay, pilot, product runtime
        │
        ▼
TRUSTED RECEIPT REVIEW
exact subject + actor + time + metric + limitation
        │
        ▼
HUMAN ADMIT
roadmap or durable-owner promotion
```

## Ownership rules

- `ai-product-notes` owns the opportunity packet and roadmap state.
- Public companion repositories may supply source verification, repository understanding, runtime qualification or security evidence through versioned contracts.
- A private provider may supply only a sanitized capability envelope. The provider keeps its repository identity, code, raw evidence and customer data private.
- The durable implementation owner is chosen after validation. Until then, this repository does not create false coupling to a product repo.

## Hard architectural laws

1. No score can compensate for a hard privacy or rights failure.
2. No model-generated judgment is the sole authority for demand, license or experiment success.
3. Historical signals and decisions are append-only or explicitly superseded; they are not silently rewritten.
4. Inputs and outputs are versioned, canonical JSON where machine-readable, and deterministic when the same evidence is supplied.
5. Private data never enters public fixtures, logs, Issue bodies, PR descriptions or receipts.
6. `VALIDATE` is the default for a strong hypothesis without direct payment evidence.
7. A change to shared indexes belongs to one convergence branch.
