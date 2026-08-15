# Agent Contract Evolution Replay CI

State: `VALIDATE / AGGREGATE_PUBLIC_REAL_HISTORY_3_OF_5`

## Hypothesis

A versioned tool, Skill, SDK, registry, publisher, or protocol contract change can be replayed against previously accepted procedural consumers to identify compatibility breaks before a harness upgrade is admitted.

```text
immutable old contract
+ immutable new contract
+ historically accepted consumer
+ subject-bound validation evidence
→ deterministic compatibility receipt
→ append-only aggregate evidence ledger
```

Synthetic cases prove evaluator behavior only. They never count toward the five-case roadmap gate.

## Evidence layers

The original corpus remains immutable:

```text
corpus/manifest.json
corpus/receipts.json
base receipt digest:
sha256:4ca13352eb596c5ce7ba2bd91132f6ce0a3b976aac03489a926cc0bb1ea4326e
base count: 2 / 5
```

New independently admitted cases are appended as extension receipts and combined through:

```text
corpus/ledger-input.json
corpus/ledger.json
aggregate count: 3 / 5
remaining: 2
market state: VALIDATE
```

The aggregate ledger does not rewrite the base manifest or base receipt.

## Current adjudication

| Case | Adapter | Old | New | Decision | Gate |
|---|---|---:|---:|---|---:|
| MCP Registry package JSON casing | `registry-schema` | `PASS` | `FAIL` | `HISTORICAL_BREAKAGE` | counted |
| TypeScript SDK `getTaskResult` 1.x → modular 2.x | `sdk-api` | `PASS` | `FAIL` | `HISTORICAL_BREAKAGE` | counted |
| MCP Registry publisher schema revision 2025-09-16 → 2025-09-29 | `registry-publisher-schema-revision` | `PASS` | `FAIL` | `HISTORICAL_BREAKAGE` | counted |
| 2026-07-28 server identity envelope relocation | `protocol-envelope` | `NOT_EXERCISED` | `NOT_EXERCISED` | `UNSUPPORTED_ADAPTER` | not counted |

## Counted case 1: Registry package field casing

An exact old upstream fixture uses snake-case package fields. It passes the old contract and fails the later camel-case contract. The receipt binds old/new source blobs, the unchanged consumer, and deterministic object-field validation.

## Counted case 2: TypeScript SDK major migration

An independent downstream call:

```text
getTaskResult(capturedTaskId, undefined, requestOptions)
```

is bound to `@modelcontextprotocol/sdk@1.29.0`, an exact dependency lock, and successful downstream typecheck/build CI. The unchanged three-position call is incompatible with the modular `@modelcontextprotocol/client@2.0.0-alpha.0` two-position contract.

This proves compile-time migration incompatibility, not a production outage.

## Counted case 3: Registry publisher schema-revision admission

The publisher changed its pre-authentication admission guard:

```text
old publisher@4962609697de34ee8fcccdc6f9166f5b4cdbad99
  admitted revision: 2025-09-16
  old upstream fixture: PASS
  CI run 18078458326: success

new publisher@b21c6f564d9197f14006a87928181539f57b28ab
  admitted revision: 2025-09-29
  unchanged 2025-09-16 fixture: FAIL
  CI run 18109863200: success
```

The extension binds:

- exact old/new `publish.go` blobs;
- exact old/new `publish_test.go` blobs;
- released `2025-09-16` and `2025-09-29` schema blobs;
- the exact shared CI workflow blob;
- exact old/new CI heads;
- successful `Tests` and `Build, Lint, and Validate` jobs;
- deterministic reason `schema_revision_not_admitted`.

The same upstream event removed publisher-controlled `status`, but that observation is explicitly `NOT_COUNTED`. Go JSON unmarshalling and the observed validator path do not prove unknown-field rejection, so `status` cannot be substituted as the breakage reason.

Canonical extension:

```text
corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/case.json
corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/receipt.json
```

## Unsupported protocol-envelope case

Moving server identity from `DiscoverResult.serverInfo` into result `_meta` requires protocol negotiation, response metadata stamping, and consumer read-path semantics. It remains `UNSUPPORTED_ADAPTER`; reducing it to a field rename would create false confidence.

## Append-only admission laws

- Base `manifest.json` and `receipts.json` are immutable evidence subjects.
- Every extension has an independent self-digest.
- Ledger input pins the expected extension receipt and every source-binding digest.
- Duplicate case IDs fail.
- Duplicate change-event IDs fail, preventing one upstream PR from being split into multiple counts.
- Changelog prose alone cannot count.
- Missing, stale, skipped, or failed CI provenance blocks admission.
- `BUILD` remains false even when the technical count increases.

## Commands

```bash
python3 scripts/replay_contract_history.py \
  experiments/agent-contract-evolution-replay/corpus/manifest.json \
  --check experiments/agent-contract-evolution-replay/corpus/receipts.json

python3 scripts/replay_publisher_schema_revision.py \
  experiments/agent-contract-evolution-replay/corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/case.json \
  --check experiments/agent-contract-evolution-replay/corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/receipt.json

python3 scripts/compile_history_evidence_ledger.py \
  experiments/agent-contract-evolution-replay/corpus/ledger-input.json \
  --check experiments/agent-contract-evolution-replay/corpus/ledger.json

python3 -m unittest discover -s tests -p 'test_*.py'
```

## Promotion gate

Promotion to `BUILD` still requires all of the following:

- at least 5 independently adjudicated real historical breakages;
- at least 3 qualified teams confirming recurring pain;
- acceptable false-positive, unsupported, and inconclusive rates;
- evidence that composing existing schema-diff and replay tools is insufficient;
- paid-pilot or equivalent binding adoption evidence;
- Human Admit for product, security, rights, and delivery scope.

## Evidence boundary

The aggregate ledger proves three countable public compatibility breaks and one unsupported adapter class. It does not prove an observed production outage, universal MCP compatibility, production safety, customer demand, paid adoption, product-market fit, or live Git Town execution.
