# Stacked PR ledger

Epic: [#3 — Market-to-MVP control plane](https://github.com/ed3c/ai-product-notes/issues/3).

## Published graph

```text
main@ab9596ff1df2b44785e28baad650f93f21b9786c
└── agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb
    Issue #4 · Draft PR #7 · base main
    └── agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64
        Issue #5 · Draft PR #8 · base agent/4-market-control-plane
        └── agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f
            Issue #6 · Draft PR #9 · base agent/5-opportunity-compiler
            └── agent/10-exact-head-ci@5b646ec6fe70dd2047734636b8dfd517ee2998b2
                Issue #10 · Draft PR #11 · base agent/6-portfolio-convergence
                + terminal shared-index reconciliation
```

| Leaf | Issue | Branch | Exact PR base | Immutable stage head | PR | Publication state |
|---|---|---|---|---|---|---|
| Governance | [#4](https://github.com/ed3c/ai-product-notes/issues/4) | `agent/4-market-control-plane` | `main@ab9596ff1df2b44785e28baad650f93f21b9786c` | `8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | [#7](https://github.com/ed3c/ai-product-notes/pull/7) | `DRAFT_PUBLISHED` |
| Compiler | [#5](https://github.com/ed3c/ai-product-notes/issues/5) | `agent/5-opportunity-compiler` | `agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | `849b50a011abdbe9940fa52d597a456902601e64` | [#8](https://github.com/ed3c/ai-product-notes/pull/8) | `DRAFT_PUBLISHED` |
| Convergence | [#6](https://github.com/ed3c/ai-product-notes/issues/6) | `agent/6-portfolio-convergence` | `agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64` | `6d88ed1fc26c74d8e5ad0d0e0fdef09e38560d81`; reconciled parent head `83243ba32729a75e953125370a8cb0b61cee197f` | [#9](https://github.com/ed3c/ai-product-notes/pull/9) | `DRAFT_PUBLISHED` |
| CI evidence | [#10](https://github.com/ed3c/ai-product-notes/issues/10) | `agent/10-exact-head-ci` | `agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f` | `5b646ec6fe70dd2047734636b8dfd517ee2998b2` before terminal reconciliation | [#11](https://github.com/ed3c/ai-product-notes/pull/11) | `DRAFT_PUBLISHED / HOSTED_VERIFIED_STAGE` |

## Current-head rule

Git commits cannot truthfully embed their own final SHA. This ledger records immutable stage heads and exact PR bases. The current head of the terminal CI branch is authoritative in PR #11 metadata and the final Issue #10 reconciliation comment. Any later commit must update that external receipt, not invent a self-referential SHA here.

## Path-lease reconciliation

- PR #7 owns repository governance, Agent routing, architecture, State Machine and Git profile paths.
- PR #8 owns compiler, schemas, asset/portfolio fixtures, tests and workflow paths; it does not edit shared indexes.
- PR #9 owns opportunity, experiment, roadmap and portfolio handoff, then reconciles the three-leaf index.
- PR #11 owns CI subject separation and becomes the terminal shared-index owner for that evidence correction.
- All branches remain one-writer and no force update was used.

## Merge order

1. Review and Human Admit PR #7.
2. Merge PR #7, then retarget/reconcile PR #8 to `main` without changing its admitted subject.
3. Merge PR #8, then retarget/reconcile PR #9.
4. Merge PR #9, then retarget/reconcile PR #11.
5. Re-run exact-head and merge-compatibility checks and reconcile this ledger from current remote state.


## Hosted subject evidence

Run `31878162441` is bound to the immutable CI stage head:

| Lane | Subject | Bound lineage | Result |
|---|---|---|---|
| Exact head contracts | `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | explicit checkout ref equals `EXPECTED_SUBJECT` | `PASS`; repository contract, 23 tests, packet reproduction |
| Synthetic merge compatibility | `3bb417881393b5faad2a91056c49c77eefeb3cc8` | base `83243ba32729a75e953125370a8cb0b61cee197f`, head `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | `PASS`; repository contract, 23 tests, packet reproduction |

The earlier single-job PR #8/#9 runs checked synthetic merge commits. They are integration evidence only and are not upgraded to exact-head evidence. The post-reconciliation current head/run must be read from PR #11 and Issue #10.

## Evidence state

```text
branch hierarchy through GitHub API: PUBLISHED
draft PR stack: PUBLISHED (#7 → #8 → #9 → #11)
exact-head stage receipt: PASS (run 31878162441, subject 5b646ec6fe70dd2047734636b8dfd517ee2998b2)
synthetic-merge stage receipt: PASS (run 31878162441, subject 3bb417881393b5faad2a91056c49c77eefeb3cc8)
shared method: DOCUMENTED
exact Git Town executable admission: ABSENT / BLOCKED_POLICY
live Git Town sync: NOT_EXERCISED
worktree, lease and conflict canaries: NOT_EXERCISED
hosted CI: read from exact workflow run; workflow file alone is not PASS
merge/ship/roadmap promotion: HUMAN ADMIT
```

The API-created compatible branch graph proves Git ancestry and PR bases only. It is not evidence that Git Town was installed, configured or executed.
