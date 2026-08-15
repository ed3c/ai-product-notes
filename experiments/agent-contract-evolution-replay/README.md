# Agent Contract Evolution Replay CI

State: `VALIDATE / PUBLIC_REAL_HISTORY_CORPUS_1_OF_5`

## Hypothesis

A versioned tool, Skill, SDK, registry or protocol contract change can be replayed against previously accepted procedural consumers to identify compatibility breaks before a harness upgrade is admitted.

The repository now has two evidence layers:

```text
synthetic contract-rule fixtures
+
public immutable upstream history
→ deterministic compatibility receipts
```

Synthetic cases prove evaluator behavior only. They never count toward the five-case roadmap gate.

## Public real-history corpus

Canonical subjects:

```text
experiments/agent-contract-evolution-replay/corpus/manifest.json
experiments/agent-contract-evolution-replay/corpus/receipts.json
```

Current adjudication:

| Case | Adapter | Old result | New result | Decision | Counts toward 5-case gate |
|---|---|---:|---:|---|---:|
| MCP Registry package field casing | `registry-schema` | `PASS` | `FAIL` | `HISTORICAL_BREAKAGE` | yes |
| TypeScript SDK `getTaskResult` positional role | `sdk-api` | `PASS` | `FAIL` | `CONTRACT_BREAKAGE_NOT_COUNTED` | no |
| 2026-07-28 server identity envelope relocation | `protocol-envelope` | `NOT_EXERCISED` | `NOT_EXERCISED` | `UNSUPPORTED_ADAPTER` | no |

### Why only one case counts

The MCP Registry case binds:

- exact old and new `pkg/model/types.go` blobs;
- an old upstream passing test fixture;
- a normalized unchanged JSON consumer;
- old `snake_case` and new `camelCase` contracts.

The unchanged historical consumer passes the old contract and fails the new one, so it is admitted as one public historical breakage.

The TypeScript SDK case proves the exported positional contract changed from:

```text
getTaskResult(taskId, resultSchema?, options?)
```

to:

```text
getTaskResult(taskId, options?)
```

The second historical argument role therefore fails against the new call contract. It is not counted because the current corpus binds an upstream self-consumer/call surface rather than an independent downstream failure fixture.

The protocol-envelope case is deliberately unsupported. Moving server identity from `DiscoverResult.serverInfo` into result `_meta`, while also changing request-envelope requirements, requires negotiated-era and cross-message semantics. Treating that as a plain object-field rename would create a false confidence signal.

## Evidence contract

Every case records separate digests for:

```text
old source binding
new source binding
consumer source binding
change source binding
old normalized contract
new normalized contract
consumer payload
compiled corpus receipt
```

An immutable source binding contains a repository, 40-character commit, path and Git blob SHA. Changelog prose may explain a change but cannot by itself produce `HISTORICAL_BREAKAGE`.

## Adapters

### `registry-schema`

Validates required and allowed object fields against an exact historical consumer.

### `sdk-api`

Validates positional argument roles against an exported API call contract. A positional slot changing from `result_schema` to `request_options` is reported explicitly.

### `protocol-envelope`

Currently returns `UNSUPPORTED_ADAPTER`. A future implementation must model protocol negotiation, request/result envelope identity, metadata stamping and consumer read paths without collapsing them into isolated schema checks.

### `mcp-tool`

The original synthetic tool-call replay remains available through `scripts/replay_agent_contract.py`. It is not used to inflate the public-history count.

## Commands

```bash
python3 scripts/replay_contract_history.py \
  experiments/agent-contract-evolution-replay/corpus/manifest.json \
  --check experiments/agent-contract-evolution-replay/corpus/receipts.json

python3 -m unittest tests.test_contract_history_corpus
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Runtime and market gate

Technical admission requires exact-head and synthetic-merge hosted CI to prove:

- committed receipts reproduce byte-for-byte;
- old/new/consumer source lanes remain immutable;
- Registry old PASS and new FAIL remain stable;
- SDK positional-role drift remains visible but not counted;
- the unsupported protocol case cannot be silently upgraded;
- the roadmap stays `VALIDATE`.

Promotion to `BUILD` still requires:

- at least 5 independently adjudicated real historical breakages;
- at least 3 qualified teams confirming recurring pain;
- acceptable false-positive, unsupported and inconclusive rates;
- evidence that composing existing schema-diff and replay tools is insufficient;
- paid-pilot or equivalent binding adoption evidence.

## Evidence boundary

This corpus does not prove production safety, universal MCP compatibility, customer demand, paid adoption or semantic equivalence. It currently proves one countable public historical breakage, one exact contract breakage that is intentionally not counted, and one adapter gap.
