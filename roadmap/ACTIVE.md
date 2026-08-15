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
- **Immutable base corpus:** `2 / 5`.
- **Current real-history gate:** `2 / 5` in the immutable base corpus; append-only evidence is counted separately.
- **Base receipt:** `experiments/agent-contract-evolution-replay/corpus/receipts.json`.
- **Base receipt digest:** `sha256:4ca13352eb596c5ce7ba2bd91132f6ce0a3b976aac03489a926cc0bb1ea4326e`.
- **Aggregate evidence ledger:** `3 / 5`.
- **Remaining historical cases:** `2`.
- **Aggregate ledger:** `experiments/agent-contract-evolution-replay/corpus/ledger.json`.
- **Counted evidence 1:** MCP Registry package JSON casing migration — exact old upstream fixture `PASS`, new contract `FAIL`.
- **Counted evidence 2:** TypeScript SDK `getTaskResult` 1.x → modular 2.x — independent downstream call, exact dependency lock, exact successful typecheck/build CI, old `PASS`, new `FAIL`.
- **Counted evidence 3:** MCP Registry publisher schema revision 2025-09-16 → 2025-09-29 — exact old/new publisher and test blobs, released schemas, exact CI heads, successful required jobs, old `PASS`, new `FAIL` with `schema_revision_not_admitted`.
- **Negative finding:** publisher-controlled `status` removal is `NOT_COUNTED`; unknown-field rejection is not proven by the observed Go decoder/validator path.
- **Unsupported:** 2026-07-28 server identity relocation still requires a `protocol-envelope` adapter and remains `UNSUPPORTED_ADAPTER`.
- **Synthetic evidence:** evaluator tests only; never counts toward the real-history gate.
- **Runtime evidence:** `PENDING_HOSTED_CI` for Issue #22 and its exact PR head/merge subjects.
- **Customer-origin evidence:** `ABSENT`.
- **Paid demand:** `ABSENT`.
- **Promotion gate:** at least 3 qualified teams with recurring pain plus 5 independently adjudicated real historical breakages, acceptable false-positive/unsupported/inconclusive rates, and paid or binding adoption evidence.
- **Durable owner:** `UNSELECTED`.
- **Non-goal:** generic trace viewer, automatic repair, LLM judge, or a false universal MCP/Agent Skills compatibility claim.

## Next evidence work

1. Find two additional independent old-`PASS`/new-`FAIL` cases without splitting one upstream change event into multiple counts.
2. Prefer a public downstream consumer for at least one remaining case to reduce upstream self-fixture bias.
3. Implement `protocol-envelope` only after exact negotiated-era, response metadata, and consumer read-path semantics are specified.
4. Start qualified buyer interviews after hosted replay receipts expose false-positive and unsupported rates.
5. Request paid-pilot commitment before selecting a durable hosted-product owner.

No item is currently in `BUILD`.
