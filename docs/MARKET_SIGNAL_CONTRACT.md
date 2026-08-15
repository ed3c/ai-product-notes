# Market Signal Contract｜市場訊號與藍海機會契約

## Core question

Do not ask only “what launched?” Ask:

> Which repeated, expensive workflow failure is becoming urgent, who controls a budget for it, what narrow outcome can be verified quickly, and which parts can be assembled from commercially usable assets without creating a rights or operations trap?

## Evidence classes

| Class | Examples | What it can prove | What it cannot prove |
|---|---|---|---|
| `PRIMARY_MARKET` | official launch, pricing, changelog, docs | product/event identity and vendor claim | buyer success or independent quality |
| `CUSTOMER` | interview, ticket, incident, signed LOI, paid pilot | buyer pain or direct demand for the exact subject | broad market size by itself |
| `REPUTABLE_SECONDARY` | reporting, analyst study | external context and trend | exact product capability without primary evidence |
| `REPOSITORY` | source, license, release, issue | implementation and project evidence | hosted-service terms or downstream asset rights |
| `EXPERIMENT` | replay, benchmark, pilot receipt | observed outcome for exact fixture/subject | universal market or production proof |
| `INFERENCE` | analyst reasoning | testable hypothesis | admission without validation |

Independent evidence means different decision origins, not multiple pages repeating one announcement.

## Minimum normalized signal

```json
{
  "schema_version": "market-signal.v1",
  "id": "stable-slug",
  "title": "Opportunity title",
  "observed_at": "RFC3339 timestamp",
  "freshness": {
    "event_date": "YYYY-MM-DD",
    "source_date": "YYYY-MM-DD",
    "window_hours": 24,
    "status": "PASS"
  },
  "target_segment": "narrow buyer segment",
  "problem": "expensive repeated failure",
  "wedge": "smallest verifiable outcome",
  "metrics": {
    "pain_intensity": 1,
    "wtp_evidence": 1,
    "recurrence": 1,
    "distribution_reach": 1,
    "market_timing": 1,
    "competition_pressure": 1,
    "evidence_confidence": 1
  },
  "demand_evidence": [],
  "required_capabilities": [],
  "constraints": {},
  "mvp": {}
}
```

Every 1–10 metric must be tied to evidence or explicitly labeled inference.

## Blue-ocean filter

Prefer opportunities where:

1. the costly job is downstream of a crowded platform rather than another general platform;
2. correctness, evidence, governance, integration or migration is harder than generation;
3. the buyer already spends money on the surrounding workflow;
4. the first outcome can be replayed against historical incidents or fixtures;
5. distribution is attached to an existing ecosystem such as GitHub, API providers or creator tooling;
6. the differentiator is a proprietary join, evaluator or workflow contract rather than a thin model wrapper.

## Capability and substitution mapping

For each product feature, produce:

```yaml
capability_id: stable-id
importance: must | should | could
asset_types: [code, model_weights, datasets, trajectories, hosted_service]
accepted_interfaces: []
candidates: []
portfolio_matches: []
gap_state: covered | candidate | gap | blocked
```

A candidate counts toward substitution coverage only when every required asset type has `PASS`. `MIT` or `Apache-2.0` code does not transfer rights to bundled data, model weights, trajectories or managed services.

## Gap taxonomy

- `market`: buyer, urgency, budget, segment or distribution unknown.
- `evidence`: freshness, independence, payment or outcome evidence missing.
- `stack`: required capability has no admitted candidate.
- `portfolio`: reusable capability is absent, weak or unverified.
- `delivery`: no durable owner, test, CI, rollback or observability path.
- `rights_privacy`: license scope, service terms, third-party content or private-data boundary blocks use.

## Decision gate

A high numerical score cannot override a hard `rights_privacy` gap. `BUILD` additionally requires a direct paid-demand signal, at least two independent evidence groups, strong evidence confidence and no uncovered must-have capability. Otherwise a promising subject remains `VALIDATE`.
