# Modern Web Architecture — Stage 5 Technical Systems Canary

This canary is a true child of `ai-product-notes` PR #54. It consumes the exact Stage 4 dossier by Git commit, blob and dossier digest, then compiles an implementable technical design without claiming that any implementation or runtime exists.

Read `../AGENTS.md` before mutation.

## Stack / traceability index

```text
ed3c/ai-content-notes
PR #52 source registry
└── PR #53 exact PDF adapter
    └── PR #73 product-signal@1
        ↓ exact product-signal blob

ed3c/ai-product-notes
PR #54 Stage 4 reverse-engineering dossier
└── Stage 5 / Issue #51 technical systems packet
    ├── structured-scene-ir          deterministic / must
    ├── constraint-validation        deterministic / must
    └── candidate-rendering-stack    probabilistic / should / excluded from first MVP
```

## State Machine

```text
DOSSIER_BOUND
→ WORKFLOW_DECOMPOSED
→ CAPABILITIES_BOUND
→ TRUE_EDGES_BOUND
→ RIGHTS_SEPARATELY_GATED
→ EVALS_BOUND
→ MVP_TECHNICAL_SLICE_SELECTED
→ PACKET_DIGESTED
→ HOSTED_VERIFIED | BLOCKED
```

## Data flow

```text
Stage 4 dossier.json
+ stage4-binding.json
+ technical-systems-plan.json
→ src/ai_product_notes/technical_systems.py
→ capability DAG + interfaces + component State Machines
→ separate rights matrix
→ positive / negative / mutation / fault / runtime eval plan
→ bounded deterministic MVP technical slice
→ technical-systems-packet.json
→ exact Git read-back + hosted exact-head/synthetic-merge checks
```

## True dependency DAG

```text
structured-scene-ir
└── constraint-validation
    └── candidate-rendering-stack
```

The first MVP intentionally stops before the probabilistic rendering backend. It tests whether structured state and deterministic constraint receipts work before selecting a library, model, provider or hosted service.

## Evidence boundary

- `TECHNICAL_DESIGN_ONLY` is not implementation evidence.
- third-party rendering/model/provider rights remain `UNKNOWN` until exact assets and scopes are reviewed.
- the upstream unknown named-product internals and permissive-vs-LGPL contradiction remain visible.
- the runtime eval is `NOT_EXERCISED`.
- user, paid and legal evidence remain absent.
- maximum automated decision remains `VALIDATE`.

## Verification

```bash
python3 -m py_compile \
  src/ai_product_notes/technical_systems.py \
  scripts/compile_technical_systems_packet.py \
  tests/test_technical_systems_packet.py

python3 -m unittest -q tests/test_technical_systems_packet.py

python3 scripts/compile_technical_systems_packet.py \
  --dossier evals/reverse-engineering/modern-web-architecture/dossier.json \
  --binding evals/technical-systems/modern-web-architecture/stage4-binding.json \
  --plan evals/technical-systems/modern-web-architecture/technical-systems-plan.json \
  --output evals/technical-systems/modern-web-architecture/technical-systems-packet.json \
  --check
```

No file here proves implementation, runtime quality, named-product equivalence, license clearance, user value, paid demand, BUILD, merge, release or production readiness.
