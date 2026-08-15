# Configuration / 固定參數

## Repository and monitoring

- Canonical repository: `ed3c/ai-product-notes`
- Canonical branch: `main`
- Timezone: `Asia/Taipei`
- Monitor window: trailing 24 hours
- Daily qualified items: up to 5–10; zero is valid
- Top lists: at most 100 active records per category
- Storage: GitHub Markdown + canonical JSON
- Google Sheet / Google Doc / Excel writes: **disabled**
- Update strategy: incremental, read-before-write
- Product identity: normalized product/concept name + canonical official URL
- Preserve `First Added At`; change `Last Updated At` only for real evidence/content changes
- Notes: Traditional Chinese + English
- Secret policy: never commit credentials, private tokens, private repository metadata, customer data or raw sensitive trajectories

## Existing Top-100 scores

`Top 100 Best AI Products`

```text
0.35 * WTP + 0.25 * Funding Scale + 0.20 * User Traction + 0.20 * Market Gap Moat
```

`Top 100 Solopreneur Products`

```text
0.35 * Tech Simplicity + 0.25 * Profit Margin + 0.25 * Gap Size + 0.15 * Distribution Ease
```

These rankings are discovery inputs. They do not authorize product implementation.

## Opportunity compiler score

The compiler uses versioned 1–10 inputs plus calculated portfolio/substitution coverage:

```text
positive =
  0.20 * pain_intensity
+ 0.18 * wtp_evidence
+ 0.12 * recurrence
+ 0.10 * distribution_reach
+ 0.10 * market_timing
+ 0.15 * evidence_confidence
+ 0.08 * portfolio_fit
+ 0.07 * substitution_coverage

score_0_100 = clamp(10 * positive - 1.5 * competition_pressure, 0, 100)
```

Hard privacy, schema or required-right failures force `BLOCKED`. `BUILD` additionally requires direct paid demand and no uncovered must capability. Missing payment evidence caps the decision at `VALIDATE`.

## Delivery policy

### `DATA_INCREMENT_LANE`

An already-admitted bounded automation may update only:

```text
reports/daily/**
notes/**
data/products/**
RANK.md                 # evidence-backed asset/ranking delta only
```

The automation must prove exact workflow identity, allowed paths, incremental read-before-write behavior and validation for the exact subject. Interactive Agents do not use this lane to bypass review. When workflow admission is absent, use a PR.

### `PRODUCT_CHANGE_LANE`

Issue-first reviewable branches are mandatory for:

```text
AGENTS.md
README.md and shared indexes
docs architecture/policy/state/git contracts
config and schemas
src, scripts and tests
workflows
opportunities, experiments and roadmap semantics
```

Use the shared `git-town-stacked-pr-worker` method with repository-owned work packets, path leases, checks and receipts. Exact Git Town executable admission is currently `ABSENT`; live synchronization is `NOT_EXERCISED`; merge/ship remains Human Admit.

## Ranking tie-break

1. score descending;
2. stronger independent market validation;
3. newer `Last Updated At` only when evidence actually changed;
4. stable prior order when evidence does not justify reordering.
