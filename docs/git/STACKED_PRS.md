# Stacked PR ledger

Epic: [#3 — Market-to-MVP control plane](https://github.com/ed3c/ai-product-notes/issues/3).

## Original molecular graph

```text
main@ab9596ff1df2b44785e28baad650f93f21b9786c
└── agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb
    Issue #4 · PR #7 · original base main
    └── agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64
        Issue #5 · PR #8 · original base agent/4-market-control-plane
        └── agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f
            Issue #6 · PR #9 · original base agent/5-opportunity-compiler
            └── agent/10-exact-head-ci@ac66cc60963b77c5f5872d0825c40319c2bfa855
                Issue #10 · PR #11 · original base agent/6-portfolio-convergence
```

The graph above preserves the historical Git Town-compatible branch ancestry. The branches were initially `DRAFT_PUBLISHED`; that historical state remains part of the audit trail rather than being rewritten.

## Human Admit and merge reconciliation

The repository owner supplied Human Admit in the current task. Parent leaves were merged with the `merge` method so their original commits remain ancestors of the child branches. Each child PR was then retargeted to `main` before admission.

```text
main
├── PR #7 merge  bfe03383e96183d6b6eebd24462742090c733811
├── PR #8 merge  3fc46a25cc0089e092373b1a0c92a0780f91a5a2
└── PR #9 merge  fe7e03557f07b7c9ae91210d0405745b870dafcc
    └── PR #11 head ac66cc60963b77c5f5872d0825c40319c2bfa855
        retargeted base main@fe7e03557f07b7c9ae91210d0405745b870dafcc
        + this terminal ledger reconciliation commit
```

| Leaf | Issue | Branch | Original exact PR base | Immutable stage head | PR | Current publication state |
|---|---|---|---|---|---|---|
| Governance | [#4](https://github.com/ed3c/ai-product-notes/issues/4) | `agent/4-market-control-plane` | `main@ab9596ff1df2b44785e28baad650f93f21b9786c` | `8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | [#7](https://github.com/ed3c/ai-product-notes/pull/7) | `MERGED@bfe03383e96183d6b6eebd24462742090c733811` |
| Compiler | [#5](https://github.com/ed3c/ai-product-notes/issues/5) | `agent/5-opportunity-compiler` | `agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | `849b50a011abdbe9940fa52d597a456902601e64` | [#8](https://github.com/ed3c/ai-product-notes/pull/8) | `MERGED@3fc46a25cc0089e092373b1a0c92a0780f91a5a2` |
| Convergence | [#6](https://github.com/ed3c/ai-product-notes/issues/6) | `agent/6-portfolio-convergence` | `agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64` | `6d88ed1fc26c74d8e5ad0d0e0fdef09e38560d81`; reconciled parent head `83243ba32729a75e953125370a8cb0b61cee197f` | [#9](https://github.com/ed3c/ai-product-notes/pull/9) | `MERGED@fe7e03557f07b7c9ae91210d0405745b870dafcc` |
| CI evidence | [#10](https://github.com/ed3c/ai-product-notes/issues/10) | `agent/10-exact-head-ci` | `agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f`; retargeted to `main@fe7e03557f07b7c9ae91210d0405745b870dafcc` | `5b646ec6fe70dd2047734636b8dfd517ee2998b2`; reconciled head before this commit `ac66cc60963b77c5f5872d0825c40319c2bfa855` | [#11](https://github.com/ed3c/ai-product-notes/pull/11) | `READY_FOR_REVIEW / HOSTED_VERIFIED_PRE_RETARGET`; final retarget run required |

## Current-head rule

A Git commit cannot truthfully embed its own final SHA. This ledger therefore records immutable stage heads, the parent head of this reconciliation commit, exact PR bases, merge commits and external workflow run IDs. The current terminal branch head is authoritative in PR #11 metadata and its workflow run.

## Path-lease reconciliation

- PR #7 owned repository governance, Agent routing, architecture, State Machine and Git profile paths.
- PR #8 owned compiler, schemas, asset/portfolio fixtures, tests and workflow paths; it did not edit shared indexes.
- PR #9 owned opportunity, experiment, roadmap and portfolio handoff, then reconciled the three-leaf index.
- PR #11 owns CI subject separation and the terminal shared-index reconciliation.
- All branches kept one active writer. No force update was used.

## Admission sequence

1. `PASS` — PR #7 merged into `main` as `bfe03383e96183d6b6eebd24462742090c733811`.
2. `PASS` — PR #8 retargeted to `main` and merged as `3fc46a25cc0089e092373b1a0c92a0780f91a5a2`.
3. `PASS` — PR #9 retargeted to `main` and merged as `fe7e03557f07b7c9ae91210d0405745b870dafcc`.
4. `RUNNING` — PR #11 retargeted to current `main`; exact-head and synthetic-merge contracts must pass on the new terminal head before merge.
5. `PENDING` — after PR #11 merge, create a separate Issue-first reconciliation leaf for final merged-state README/index updates if any self-referential state remains.

## Hosted subject evidence

Run `31878162441` is bound to the immutable CI stage head:

| Lane | Subject | Bound lineage | Result |
|---|---|---|---|
| Exact head contracts | `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | explicit checkout ref equals `EXPECTED_SUBJECT` | `PASS`; repository contract, 23 tests, packet reproduction |
| Synthetic merge compatibility | `3bb417881393b5faad2a91056c49c77eefeb3cc8` | base `83243ba32729a75e953125370a8cb0b61cee197f`, head `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | `PASS`; repository contract, 23 tests, packet reproduction |

Run `31878346277` subsequently proved the pre-retarget terminal head `ac66cc60963b77c5f5872d0825c40319c2bfa855` and synthetic merge `c2336332cc279142194beaae39a04b248f45b7ed` with 24 tests in both lanes. Those receipts remain valid for their exact subjects, but the retargeted PR requires a fresh run because its base parent changed.

The earlier single-job PR #8/#9 runs checked synthetic merge commits. They remain integration evidence only and are not upgraded to exact-head evidence.

## Evidence state

```text
historical branch hierarchy through GitHub API: PUBLISHED
historical draft PR stack: DRAFT_PUBLISHED (#7 → #8 → #9 → #11)
parent leaves merged: PASS (#7, #8, #9)
terminal PR retargeted to main: PASS
exact-head stage receipt: PASS (run 31878162441, subject 5b646ec6fe70dd2047734636b8dfd517ee2998b2)
synthetic-merge stage receipt: PASS (run 31878162441, subject 3bb417881393b5faad2a91056c49c77eefeb3cc8)
pre-retarget terminal receipt: PASS (run 31878346277)
final retarget exact-head + synthetic-merge receipt: PENDING_WORKFLOW
shared method: DOCUMENTED
exact Git Town executable admission: ABSENT / BLOCKED_POLICY
live Git Town sync: NOT_EXERCISED
worktree, lease and conflict canaries: NOT_EXERCISED
hosted CI: read from exact workflow run; workflow file alone is not PASS
market validation and paid demand: ABSENT
roadmap state: VALIDATE
```

The API-created compatible branch graph proves Git ancestry, PR bases and merge commits only. It is not evidence that Git Town was installed, configured or executed.