# Structured Product Compiler

This document is the PREL-D02 convergence surface for one deterministic
structured-state → constraint-validation wedge. It records implementation and
evidence that can be read back from exact Git subjects. It does not select a
renderer or model provider and does not prove users, paid demand, rights,
release, or production fitness.

`PREL-C02/K03/E02/X02/D02` are immutable Stage 7 atom identifiers: contract,
core validator, deterministic evaluation, local execution, and documentation
convergence respectively. `Hosted` means GitHub Actions evidence for one exact
published subject; `local` means evidence produced in the bound clean worktree.

## Boundary

```text
SceneSpec canonical contract (C02)
  → deterministic constraint validator (K03)
  → fixed positive/negative/mutation denominator (E02)
  → clean-checkout local runtime canary (X02)
  → documentation/index convergence (D02)
```

Rendering, probabilistic generation, provider choice, customer validation,
commercial validation, and rights admission remain separate lanes.

Runtime data moves through this bounded path:

```text
canonical input.json
→ SceneSpec.from_json (schema + canonical digest)
→ validate_scene (deterministic constraints)
→ validation receipt bytes + digest
→ bounded worker stdout/stderr/exit receipt
→ committed X02 runtime receipt
```

## Exact atom ledger

| Atom | Issue / PR | Exact parent | Exact implementation subject | Evidence | State |
|---|---|---|---|---|---|
| Stage 7 plan | #58 / draft PR #59 | `34f77140968799c0c2669610609848beadf96646` | head `2a37430337a87380afae6fc2617cd41692d9fd75` | run `32278487238` | `PASS_READBACK / HOSTED_VERIFIED` |
| PREL-C02 | #60 / draft PR #61 | `2a37430337a87380afae6fc2617cd41692d9fd75` | head `b0f59c7afad5b9acdbffbe9c87c1d86507237ea0`; tree `c72a4312d569daeb88d4f0fc6ca3f88794a50e42` | Issue #60 completion receipt; run `32282464736` | `MATERIALIZED / HOSTED_VERIFIED` |
| PREL-K03 | #62 / draft PR #63 | `b0f59c7afad5b9acdbffbe9c87c1d86507237ea0` | head `dd185109378a34109313b3a6fa150af9de0b76cf`; tree `c25f2da1aa527661129fde58eac1039a27058ae3` | Issue #62 completion receipt; run `32283106495` | `MATERIALIZED / HOSTED_VERIFIED` |
| PREL-E02 | #64 / draft PR #65 | `dd185109378a34109313b3a6fa150af9de0b76cf` | head `f840f37582e925759bdf89290d7a5da1122d21d1`; tree `ce18049a9b9f5db656666c2d076cab573292cf0d` | committed eval receipt blob `cca27c2a67c84381deabce8aa73a6ee87e1de419`; run `32283489448` | `MATERIALIZED / HOSTED_VERIFIED` |
| PREL-X02 | #66 / no PR | `f840f37582e925759bdf89290d7a5da1122d21d1` | candidate `4a61e14d3f0892efeb3d1a251ff0a1fa24f48021`, tree `2e6a5decb11ec73c5334bfe5c206910d4f7bbaa0`; receipt commit `7225ca1b23d749f79ed1a98426dbcfd5302385be` | receipt blob `919303fce89e5247a34d0d0b03836eff358f2dd6`; file SHA-256 `a192a2bd1f5981ae81ee8934a9d223cb5296521afd6953e3163032cc9a979193` | `PHYSICALLY_EXECUTED / LOCAL_VERIFIED / UNPUBLISHED` |
| PREL-D02 | #47 / no PR | `7225ca1b23d749f79ed1a98426dbcfd5302385be` | branch `prel/63-structured-product-convergence`; exact subject is supplied by the convergence commit and later PR metadata | this document plus `docs/git/STACKED_PRS.md` read-back | `MATERIALIZING_LOCAL / UNPUBLISHED` |

The C02 and K03 completion receipts live in their GitHub Issue comments rather
than repository files. Their exact heads and hosted runs are therefore public
metadata evidence, not local runtime evidence. E02 has both an Issue receipt
and committed deterministic receipt bytes. X02 is the only local runtime lane.

## Runtime receipt

The X02 receipt binds:

- base `f840f37582e925759bdf89290d7a5da1122d21d1`;
- candidate head `4a61e14d3f0892efeb3d1a251ff0a1fa24f48021` and tree
  `2e6a5decb11ec73c5334bfe5c206910d4f7bbaa0`;
- normalized input file SHA-256
  `63084a3602ae520ec4ed342fd617865fb6901704cccd72abd89c587cc3a3744d`;
- SceneSpec digest
  `6040b0ad8cd1b16edb539288e8a7bff8db150740287a27685d9d09af61683653`;
- deterministic validation receipt digest
  `46a15398c70a4117e76cd0b0fd8f7c7869ee55f39db7c6a2c492e491f7bb4f35`;
- a bounded worker with exit `0`, empty stderr digest, and exact stdout digest;
- a clean pre-run tree, receipt-only first-run residue, and a second clean
  verification returning `workspace=CLEAN cleanup=PASS`.

The local verifier rejects hosted Actions, missing launcher provenance, dirty
workspaces, path traversal/symlink escape, out-of-lease history, stale receipt
subjects, non-receipt follow-up commits, and exit zero without a durable
receipt.

## Evidence reduction

1. **Physical anchors:** exact Git commit/tree/blob identities, executable exit
   codes, deterministic digests, focused negative controls, and clean-worktree
   checks are the non-prose evidence.
2. **Human lever:** labels such as `PASS`, Issue closure, Draft PR state, and a
   count of green tests can be relabelled or denominator-selected; none is used
   alone as completion proof.
3. **Microscopic cost:** C02, K03, E02, and X02 each retain their own subject,
   lane, tests or receipt, negative controls, and gaps. A green downstream atom
   does not erase an upstream missing receipt or an external evidence lane.
4. **Reduced result:** after removing status labels that are not tied to those
   anchors, the defensible result is deterministic implementation/evaluation
   plus one exact local runtime PASS. Hosted X02/D02, queue advancement, users,
   paid demand, rights, merge, and production remain unproved.

## State machine

```text
PLANNED
→ C02_MATERIALIZED_AND_HOSTED_VERIFIED
→ K03_MATERIALIZED_AND_HOSTED_VERIFIED
→ E02_MATERIALIZED_AND_HOSTED_VERIFIED
→ X02_PHYSICALLY_EXECUTED_AND_LOCAL_VERIFIED
→ D02_CONVERGED_LOCAL
→ PUBLICATION_PENDING
→ HUMAN_ADMIT_REQUIRED
→ MERGED | BLOCKED
```

`HOSTED_VERIFIED` is subject-specific. X02 and D02 have no hosted state until
their exact published heads run. `HUMAN_ADMIT_REQUIRED` is not implied by green
tests.

## Queue discrepancy

The committed Stage 7 `local-handoff-queue.json` is a planning snapshot. It
still shows `LH-S7-VERIFY ACTIVE` and `LH-S8-C02 BLOCKED_BY_PREDECESSOR`, while
later Issue receipts and exact branch history show C02/K03/E02 completion and
the local X02 receipt above. D02's two-path lease does not authorize rewriting
that generated queue. The discrepancy remains explicit and the queue must not
be cited as current execution state.

## Evidence states and non-claims

```text
deterministic contract/core/eval  MATERIALIZED / TESTED
hosted C02/K03/E02 subjects       VERIFIED (exact historical subjects only)
local X02 runtime                 PHYSICALLY_EXECUTED / VERIFIED
D02 convergence                   LOCAL_ONLY until exact-head publication
rendering/model/provider          NOT_EXERCISED
user evidence                     ABSENT
paid evidence                     ABSENT
rights admission                  HUMAN_ADMIT_REQUIRED
Git Town executable/sync          NOT_EXERCISED
merge/release/production          HUMAN_ADMIT_REQUIRED
```

Rollback D02 by reverting only its two documentation paths. Preserve every
implementation and receipt commit. Roll back X02 separately to
`f840f37582e925759bdf89290d7a5da1122d21d1` only if its owning atom is rejected.
