# MVP Roadmap｜從訊號到快速市場驗證

## Portfolio strategy

Build one reusable decision engine in this repository, then test narrow external products. Do not create a new implementation repository for every daily signal.

### Priority 0 — Opportunity Compiler

- Normalize market evidence and freshness.
- Decompose product workflows into capabilities.
- Gate commercially usable code/model/data/trajectory/service candidates.
- Match public capabilities and sanitized private envelopes.
- Emit explicit gaps, deterministic score and experiment packet.

### Priority 1 — Vendor API Blast-Radius CI

Target API-heavy SaaS teams. The first wedge should support one language family and one vendor category, then answer:

> Which used endpoint/field changed, which call-sites are affected, and what evidence should block or warn the pull request?

Do not start with universal SDK inference, automatic code repair or every vendor.

### Priority 2 — Expert Outcome QA

Validate generated assessment/output fidelity against an expert-owned rubric and approved examples. Pursue only after a design partner supplies a real methodology and error cost.

### Priority 3 — Harness Compatibility Lab

Test plugin/runtime compatibility, breaking changes, replay and security boundaries. This aligns strongly with the portfolio but should not displace the first paid-market experiment.

## Stage gates

| Gate | Required evidence | Allowed next state |
|---|---|---|
| Problem | 10 interviews or equivalent incident corpus; at least 3 strong confirmations | `WATCH` or `VALIDATE` |
| Workflow | one narrow end-to-end user job and manual baseline | `VALIDATE` |
| Technical | historical replay with known changes and call-sites | `VALIDATE` |
| Quality | relevant-change recall and false-positive thresholds | `BUILD_CANDIDATE` |
| Payment | two paid pilots, preorder or equivalent binding commitment | `BUILD` |
| Retention | repeated use across multiple change cycles | durable product roadmap |

## Standard 14-day experiment

1. Days 1–2: recruit the narrow segment and bind the top failure cases.
2. Days 3–5: construct a manual or thin vertical slice over exact fixtures.
3. Days 6–8: replay historical changes and tune only declared rules.
4. Days 9–10: expose one delivery surface, such as a GitHub Check.
5. Days 11–12: run design-partner tasks and capture friction/error receipts.
6. Days 13–14: present the price and request a paid pilot or binding commitment.

Every experiment defines metrics, budget, forbidden weakening and stop-loss before execution.

## Roadmap refresh

New daily signals may update evidence and ranking, but they do not automatically replace an active experiment. Reprioritization requires a materially stronger opportunity packet or failure of the current stop-loss contract. Historical decisions remain traceable.
