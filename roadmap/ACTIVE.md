# Active opportunity roadmap｜2026-08-15

## 1. Vendor API Blast-Radius CI

- **State:** `VALIDATE / SATURATED_RELOCK_REQUIRED`
- **Score:** `62.06 / 100` (historical compiler score; not upgraded by this relock)
- **Canonical packet:** `opportunities/vendor-api-blast-radius/opportunity.json`
- **Experiment:** `experiments/vendor-api-blast-radius/README.md`
- **Current conclusion:** spec-level API breaking-change detection is already served by mature tools; do not build another generic detector.
- **Potential remaining value:** call-site impact joining may survive only if it proves materially better than composing existing diff tools with repository analysis.
- **Blocking market gap:** no customer-origin evidence and no direct paid-pilot receipt.
- **Blocking technical gap:** `callsite-impact-join` has no real historical replay receipt.
- **Stop-loss:** do not expand language/vendor scope to rescue weak differentiation.

## 2. Agent Contract Evolution Replay CI

- **State:** `VALIDATE`
- **Market relock:** `docs/MARKET_SATURATION_RELOCK_2026-08-15.md`
- **Experiment:** `experiments/agent-contract-evolution-replay/README.md`
- **Thin slice:** old contract + new contract + known-good trajectory → deterministic compatibility receipt.
- **First checks:** removed tool, newly-required argument, enum narrowing, historical undeclared tool.
- **Current evidence:** public synthetic fixtures only.
- **Runtime evidence:** `PENDING_HOSTED_CI` until exact branch and synthetic-merge runs pass.
- **Customer-origin evidence:** `ABSENT`.
- **Paid demand:** `ABSENT`.
- **Promotion gate:** at least 3 qualified teams with recurring pain plus at least 5 independently adjudicated real historical breakages, acceptable false-positive/unknown rates, and paid/binding adoption evidence.
- **Durable owner:** `UNSELECTED`.
- **Non-goal:** generic trace viewer, automatic repair, LLM judge, universal MCP/Agent Skills compatibility.

No item is currently in `BUILD`.
