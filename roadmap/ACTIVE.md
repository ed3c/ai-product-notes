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
- **Public corpus:** `experiments/agent-contract-evolution-replay/corpus/manifest.json`
- **Canonical receipt:** `experiments/agent-contract-evolution-replay/corpus/receipts.json`
- **Current real-history gate:** `2 / 5`.
- **Counted evidence 1:** MCP Registry package JSON casing migration — an exact old upstream fixture passes the old contract and fails the new contract.
- **Counted evidence 2:** TypeScript SDK `getTaskResult` 1.x → modular 2.x migration — an independent downstream three-argument call is bound to `@modelcontextprotocol/sdk@1.29.0`, exact successful downstream typecheck/aggregate CI, and the exact incompatible `@modelcontextprotocol/client@2.0.0-alpha.0` contract.
- **Incident boundary:** the SDK case proves compile-time migration incompatibility, not an observed production outage.
- **Unsupported:** 2026-07-28 server identity relocation requires a `protocol-envelope` adapter; it remains `UNSUPPORTED_ADAPTER`.
- **Synthetic evidence:** evaluator tests only; never counts toward the real-history gate.
- **Runtime evidence:** `PENDING_HOSTED_CI` for the downstream-CI provenance leaf.
- **Customer-origin evidence:** `ABSENT`.
- **Paid demand:** `ABSENT`.
- **Promotion gate:** at least 3 qualified teams with recurring pain plus at least 5 independently adjudicated real historical breakages, acceptable false-positive/unsupported/inconclusive rates, and paid or binding adoption evidence.
- **Durable owner:** `UNSELECTED`.
- **Non-goal:** generic trace viewer, automatic repair, LLM judge, or a false universal MCP/Agent Skills compatibility claim.

## Next evidence work

1. Find a third independently adjudicated public downstream or upstream-fixture breakage with exact old `PASS` and new `FAIL`.
2. Implement a narrowly scoped `protocol-envelope` adapter only after defining exact negotiated-era, response metadata and consumer read-path semantics.
3. Keep dependency locks and subject-bound CI receipts mandatory for countable SDK migration cases.
4. Run qualified buyer interviews and request a paid-pilot commitment only after false-positive and unsupported rates are visible.

No item is currently in `BUILD`.
