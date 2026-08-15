# Portfolio Integration｜公開能力與私有能力邊界

## Integration decision

Combine repositories through **versioned capability contracts and receipts**, not source copying or one giant monorepo. `ai-product-notes` is the Market Signal and Opportunity Decision Plane. It asks other owners for evidence only after a product hypothesis identifies a concrete capability need.

## Public repository roles

| Public repository | Role in the loop | Reusable contract | Must not be inferred |
|---|---|---|---|
| `ed3c/ai-product-notes` | fresh signal, ranking, stack map, gap ledger, MVP packet and roadmap | `market-signal.v1`, `opportunity-packet.v1` | product-market fit |
| `ed3c/ai-content-notes` | source-constrained research cards and knowledge projections | evidence/source-pack handoff | market demand or runtime qualification |
| `ed3c/truth-verify-loop` | current-source capture and evidence closure | claim/evidence/closure receipt | business value from provenance alone |
| `ed3c/openwiki-source-anchoring` | repository understanding and exact source anchors | evaluation manifest and anchor evidence | semantic relevance from lexical validity |
| `ed3c/Skill.md-native` | runtime/evidence/security/compatibility cells | Run Artifact and qualification contracts | customer demand or production admission |
| `ed3c/agent-skills-repo` | independent Skill qualification and admission | qualification receipt | implementation ownership |

Public URLs and evidence are allowed because these repositories are already public. Each capability state remains subject-bound.

## Private provider contract

A private system may be connected locally, but this public repository receives only:

```json
{
  "capability_id": "stable-capability-id",
  "contract_version": "capability.v1",
  "state": "PLANNED | MATERIALIZED | TESTED | VERIFIED | ADMITTED | BLOCKED | NOT_EXERCISED",
  "evidence_label": "technical_equivalent | candidate | inference | human_required",
  "receipt_digest": "sha256:<64 hex>",
  "exportable": true,
  "limitations": ["non-sensitive limitation"]
}
```

Forbidden in the envelope or committed output:

- private repository/owner names;
- local or remote paths and URLs;
- code, patches or internal architecture details;
- raw traces, prompts, model responses or customer datasets;
- account identity, email, token, credential or secret;
- customer names, repository identities or contractual terms.

The local overlay lives at Git-ignored `config/private-portfolio.json` or `.private/`. The compiler rejects forbidden keys and URL/path/account-like values. Only the sanitized envelope may reach an opportunity packet.

## Routing rules

1. Reuse a public capability when its exact contract is `TESTED` or stronger and matches the required subject.
2. Treat `MATERIALIZED` as a candidate, not technical equivalence.
3. Query a private provider only when the capability need is explicit and the public boundary is preserved.
4. Keep research, verification, qualification, security and market evidence in separate lanes.
5. Select a durable product owner only after the MVP experiment passes; do not force every opportunity into an existing repository.
6. Return outcome receipts to this repository as aggregates/pointers, not copied private runtime data.

## Vendor API opportunity mapping

Current reusable public capabilities cover source anchoring and current-claim verification. Permissive upstream assets cover source parsing, OpenAPI diff and GitHub publication. The missing product-specific capability is the `callsite-impact-join`. It should be implemented in the admitted durable product owner, then qualified by the appropriate evidence/security systems without making those systems the product UI.
