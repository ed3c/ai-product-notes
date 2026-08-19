# Modern Web Architecture — Stage 4 Reverse-Engineering Dossier Canary

This canary consumes the exact public `product-signal@1` packet from
`ed3c/ai-content-notes` PR #73. The local snapshot is a reproducibility copy;
GitHub remains the upstream authority and `external-binding.json` pins the PR
head, blob SHA, path, product-signal digest, and source digest.

## State Machine

```text
PRODUCT_SIGNAL_BOUND
→ SNAPSHOT_BLOB_VERIFIED
→ USER_AND_BUYER_HYPOTHESES_BOUND
→ WORKFLOW_MODELED
→ MECHANISMS_CLASSIFIED
→ CAPABILITY_RIGHTS_GAPS_BOUND
→ MVP_AND_STOP_LOSS_BOUND
→ DOSSIER_DIGESTED
→ VALIDATE | WATCH | BLOCKED | REJECT
```

## Data flow

```text
ai-content-notes PR #73 exact product-signal blob
  → product-signal.input.json + external-binding.json
  → hypotheses.json
  → src/ai_product_notes/reverse_engineering.py
  → dossier.json
  → exact Git read-back + hosted repository tests
```

## Evidence boundary

- `SOURCE_PATTERN` may inform a source-backed mechanism statement.
- `MECHANISM_HYPOTHESIS` remains a hypothesis; it cannot become observed
  named-company architecture.
- `UNKNOWN` claims and unresolved contradictions must survive compilation.
- user, buyer, pain, frequency, cost, workaround, distribution, monetization,
  retention, and defensibility are `HYPOTHESIS | UNKNOWN` until direct evidence.
- rights cannot become `PASS` while legal evidence is absent.
- maximum automated decision is `VALIDATE`.

## Verification

```bash
python3 -m py_compile \
  src/ai_product_notes/reverse_engineering.py \
  scripts/compile_reverse_engineering_dossier.py \
  tests/test_reverse_engineering_dossier.py

python3 -m unittest -q tests/test_reverse_engineering_dossier.py

python3 scripts/compile_reverse_engineering_dossier.py \
  --product-signal evals/reverse-engineering/modern-web-architecture/product-signal.input.json \
  --binding evals/reverse-engineering/modern-web-architecture/external-binding.json \
  --hypotheses evals/reverse-engineering/modern-web-architecture/hypotheses.json \
  --output evals/reverse-engineering/modern-web-architecture/dossier.json

python3 scripts/compile_reverse_engineering_dossier.py \
  --product-signal evals/reverse-engineering/modern-web-architecture/product-signal.input.json \
  --binding evals/reverse-engineering/modern-web-architecture/external-binding.json \
  --hypotheses evals/reverse-engineering/modern-web-architecture/hypotheses.json \
  --output evals/reverse-engineering/modern-web-architecture/dossier.json \
  --check
```

No file in this directory proves named-company internals, license clearance,
runtime quality, user value, paid demand, BUILD, merge, release, or production
readiness.
