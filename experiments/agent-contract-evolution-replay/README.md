# Agent Contract Evolution Replay CI

State: `VALIDATE / PUBLIC_REAL_HISTORY_CORPUS_2_OF_5`

## Hypothesis

A versioned tool, Skill, SDK, registry or protocol contract change can be replayed against previously accepted procedural consumers to identify compatibility breaks before a harness upgrade is admitted.

The evidence loop is:

```text
immutable old contract
+ immutable new contract
+ historically accepted consumer
+ subject-bound validation evidence
→ deterministic compatibility receipt
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
| TypeScript SDK `getTaskResult` 1.x → modular 2.x | `sdk-api` | `PASS` | `FAIL` | `HISTORICAL_BREAKAGE` | yes |
| 2026-07-28 server identity envelope relocation | `protocol-envelope` | `NOT_EXERCISED` | `NOT_EXERCISED` | `UNSUPPORTED_ADAPTER` | no |

## Counted case 1: MCP Registry field casing

This case binds:

- exact old and new `pkg/model/types.go` blobs;
- an old upstream passing test fixture;
- a normalized unchanged JSON consumer;
- old `snake_case` and new `camelCase` contracts.

The unchanged historical consumer passes the old contract and fails the new one.

## Counted case 2: TypeScript SDK major package migration

The independent downstream consumer is:

```text
adcontextprotocol/adcp-client
commit: ff88581e741c79cfbb5f6ddb827b90f39447be71
path: src/lib/protocols/mcp-tasks.ts
call: getTaskResult(capturedTaskId, undefined, requestOptions)
```

The consumer is not counted from source text alone. Its admission binds all of the following:

```text
package-lock.json
  @modelcontextprotocol/sdk@1.29.0
  exact SHA-512 integrity

legacy upstream tag
  v1.29.0
  @modelcontextprotocol/sdk
  getTaskResult(taskId, resultSchema?, options?)

modular target contract
  @modelcontextprotocol/client@2.0.0-alpha.0
  getTaskResult(taskId, options?)

downstream CI/CD Pipeline run 31865385554
  exact head == downstream consumer commit
  TypeScript Typecheck: success
  Typecheck & Build: success
  Test & Build: success
```

The historical `undefined` second argument is an omitted optional `resultSchema` placeholder used to reach the third `requestOptions` position. Under the modular 2.x contract, that placeholder occupies the `options` position and the historical third argument becomes an extra positional argument.

This proves a compile-time **SDK major package migration incompatibility**. It does not prove an observed production outage.

## Unsupported case: protocol envelope relocation

Moving server identity from `DiscoverResult.serverInfo` into result `_meta`, while changing request-envelope requirements, requires negotiated-era and cross-message semantics. Treating it as a plain field rename would create a false confidence signal, so it remains `UNSUPPORTED_ADAPTER`.

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
optional validation bundle
compiled corpus receipt
```

For a countable `sdk-api` migration, the validation bundle must also bind:

- exact downstream dependency lock;
- exact downstream workflow blob;
- exact old and new package manifests;
- workflow run ID and head SHA;
- successful typecheck, build and terminal aggregate jobs;
- explicit `sdk-major-package-migration` identity.

Missing or stale provenance blocks counting. Changelog prose may explain a change but cannot by itself produce `HISTORICAL_BREAKAGE`.

## Adapters

### `registry-schema`

Validates required and allowed object fields against an exact historical consumer.

### `sdk-api`

Validates positional argument roles and arity against exact package-version contracts. Countable downstream cases additionally require dependency-lock and subject-bound CI provenance.

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
- source and validation bindings remain immutable;
- both counted cases remain old `PASS` and new `FAIL`;
- missing locks, stale CI heads, skipped jobs and package-identity conflation fail closed;
- a compatible two-argument consumer is not mislabeled as a historical breakage;
- the protocol-envelope case cannot be silently upgraded;
- the roadmap stays `VALIDATE`.

Promotion to `BUILD` still requires:

- at least 5 independently adjudicated real historical breakages;
- at least 3 qualified teams confirming recurring pain;
- acceptable false-positive, unsupported and inconclusive rates;
- evidence that composing existing schema-diff and replay tools is insufficient;
- paid-pilot or equivalent binding adoption evidence.

## Evidence boundary

This corpus currently proves two countable public compatibility breakages and one adapter gap. It does not prove production safety, universal MCP compatibility, customer demand, paid adoption, semantic equivalence or an observed production incident.
