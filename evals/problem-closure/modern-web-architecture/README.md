# Modern Web Architecture — Stage 6 Product Problem-Closure Canary

Read `../AGENTS.md` before mutation.

This canary asks one bounded question: **which real problems in the Stage 4 dossier and Stage 5 technical design are actually closed, and which cheaper evidence lanes are being mistaken for closure?**

## Exact inputs

```text
Stage 5 parent
repo    ed3c/ai-product-notes
PR      #55
head    72e89c89f1961db3735231a32efc5f4ac852d670
packet  evals/technical-systems/modern-web-architecture/technical-systems-packet.json
blob    2d102fee6123be9aefabd1471a3d1d386f2fe912
digest  sha256:a34e80908f193962db9770681eaee0aba46eeb0cbbd376b81bd6d1229a26f6d7
CI      32271087668 / PASS

Portable Shadow method
repo    ed3c/skills-shared
commit  4ca9417b1da5ff32f1d4d3e7af64a15908749024
tree    58545c4807b774a364be9ac7cd20a97ae0b1d669
matrix schema blob  cefdaa8b1060504ca7c08db94bf9ac755cd216c0
audit schema blob   29a8e5be6c3a932128ec2db281955bb17fd4741f
shadow module blob  4343aaf44e2a9ae2ce4058d032327bc21849e12b
```

## Stack / DAG

```text
ai-content-notes
PR #52 source registry
└── PR #53 PDF source
    └── PR #73 product-signal@1

ai-product-notes
PR #54 Stage 4 dossier
└── PR #55 Stage 5 technical design
    └── Issue #56 / Stage 6 closure audit
        └── Issue #47 Stage 7 planner  [start only after Stage 6 exact receipt]
```

`#46` remains the Stage 6 owner. `#56` is the molecular implementation packet and may close only its materialization milestone.

## State Machine

```text
EXACT_STAGE5_BOUND
→ EXACT_SHARED_METHOD_BOUND
→ MATERIAL_PROBLEMS_BOUND
→ CLOSURE_RUNG_CLASSIFIED
→ HIGHEST_EARNED_LEVEL_RECOMPUTED
→ REOPENED_OBLIGATIONS_EMITTED
→ ISSUE_DELTA_EMITTED
→ EXACT_GIT_READBACK
→ HOSTED_FIRST_GREEN
```

## Current computed closure

```text
PRB-001 recurring user pain                  SOURCE_ANCHORED
PRB-002 structured compiler mechanism        MECHANISM_BOUND
PRB-003 deterministic MVP implementation     MECHANISM_BOUND
PRB-004 rendering/backend rights             SOURCE_ANCHORED
PRB-005 user value / paid adoption           MECHANISM_BOUND
PRB-006 named-product internal architecture  SOURCE_ANCHORED
```

No row reaches `IMPLEMENTED`, `TECH_VERIFIED`, `LIVE_WORKFLOW_VERIFIED`, `USER_VALIDATED`, or `PAID_VALIDATED`.

## Data flow

```text
exact Stage 5 technical packet
+ exact skills-shared closure contracts
+ closure-plan.json
→ subject/digest/authority gates
→ seven-rung evidence classification
→ longest-PASS-prefix computation
→ problem-closure-matrix.json
→ product-closure-audit.json
→ issue-delta.json
→ exact Git read-back + hosted repository gates
```

## Matrix summary

The matrix keeps eight proof obligations distinct:

```text
USER          recurring pain interview                 ABSENT
DETERMINISTIC scene IR round-trip                      NOT_IMPLEMENTED
DETERMINISTIC planted-invalid constraint failures      NOT_IMPLEMENTED
DETERMINISTIC stale-receipt mutation                   NOT_IMPLEMENTED
BEHAVIORAL    exact owned runtime canary                NOT_EXERCISED
HUMAN_ADMIT   six-lane rendering rights                 HUMAN_ADMIT_REQUIRED
USER          bounded workflow outcome                  ABSENT
PAID          paid pilot / admitted commercial proof    ABSENT
```

## First-green law

Stage 5 hosted CI is evidence that the exact **design/compiler repository subject** passed its owned deterministic contracts. It is not product implementation evidence. The Stage 6 audit therefore reopens `NOT_IMPLEMENTED` and `NOT_EXERCISED` obligations by name instead of inheriting them from a green parent.

## Verification

```bash
python3 -m py_compile \
  src/ai_product_notes/problem_closure.py \
  scripts/compile_problem_closure.py \
  tests/test_problem_closure.py

python3 -m unittest -q tests/test_problem_closure.py

python3 scripts/compile_problem_closure.py \
  --plan evals/problem-closure/modern-web-architecture/closure-plan.json \
  --skills-binding evals/problem-closure/modern-web-architecture/skills-binding.json \
  --stage5-binding evals/problem-closure/modern-web-architecture/stage5-binding.json \
  --technical-packet evals/technical-systems/modern-web-architecture/technical-systems-packet.json \
  --matrix evals/problem-closure/modern-web-architecture/problem-closure-matrix.json \
  --audit evals/problem-closure/modern-web-architecture/product-closure-audit.json \
  --delta evals/problem-closure/modern-web-architecture/issue-delta.json \
  --check
```

## Authority boundary

The audit is `READ_ONLY_FINDINGS_ONLY`. Its issue delta has `NO_WRITE_AUTHORITY`. Rights, customer truth, commercial truth, merge and release remain `HUMAN_ADMIT_REQUIRED`. No artifact here proves an implementation exists, a live workflow ran, users received value, payment occurred, named-product internals are known, or production is ready.
