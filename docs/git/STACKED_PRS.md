# Stacked PR ledger

Epic: [#3 — Market-to-MVP control plane](https://github.com/ed3c/ai-product-notes/issues/3).
Final reconciliation work packet: [Issue #12](https://github.com/ed3c/ai-product-notes/issues/12).

## Original molecular graph

The following graph is the immutable delivery history. Every leaf was initially `DRAFT_PUBLISHED`, used one branch writer, and targeted its exact parent branch.

```text
main@ab9596ff1df2b44785e28baad650f93f21b9786c
└── agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb
    Issue #4 · DRAFT_PUBLISHED PR #7 · base main
    └── agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64
        Issue #5 · DRAFT_PUBLISHED PR #8 · base agent/4-market-control-plane
        └── agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f
            Issue #6 · DRAFT_PUBLISHED PR #9 · base agent/5-opportunity-compiler
            └── agent/10-exact-head-ci@e37bf18dd39f91f207753d6aaad546125b62a6f1
                Issue #10 · DRAFT_PUBLISHED PR #11 · original base agent/6-portfolio-convergence
```

The graph is Git Town-compatible branch ancestry. It is not a receipt for an installed Git Town executable or a live `git town sync`.

## Human Admit and merged result

The repository owner supplied Human Admit. The stack was merged bottom-up with merge commits so the original leaf commits remain in ancestry. Each child PR was retargeted to current `main` only after its parent merged.

```text
main
├── PR #7  merge bfe03383e96183d6b6eebd24462742090c733811
├── PR #8  merge 3fc46a25cc0089e092373b1a0c92a0780f91a5a2
├── PR #9  merge fe7e03557f07b7c9ae91210d0405745b870dafcc
└── PR #11 merge 0e2654f6a89c6110728950161d968b233c7e96b4
    └── agent/12-final-stack-reconciliation
        Issue #12 · final README and ledger reconciliation
```

| Leaf | Issue | Branch | Original exact PR base | Immutable stage/current head | PR | Admitted result |
|---|---|---|---|---|---|---|
| Governance | [#4](https://github.com/ed3c/ai-product-notes/issues/4) | `agent/4-market-control-plane` | `main@ab9596ff1df2b44785e28baad650f93f21b9786c` | `8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | [#7](https://github.com/ed3c/ai-product-notes/pull/7) | `MERGED@bfe03383e96183d6b6eebd24462742090c733811` |
| Compiler | [#5](https://github.com/ed3c/ai-product-notes/issues/5) | `agent/5-opportunity-compiler` | `agent/4-market-control-plane@8ae076852bce7f1abe3344b8db0d6b2df42c61eb` | `849b50a011abdbe9940fa52d597a456902601e64` | [#8](https://github.com/ed3c/ai-product-notes/pull/8) | `MERGED@3fc46a25cc0089e092373b1a0c92a0780f91a5a2` |
| Convergence | [#6](https://github.com/ed3c/ai-product-notes/issues/6) | `agent/6-portfolio-convergence` | `agent/5-opportunity-compiler@849b50a011abdbe9940fa52d597a456902601e64` | stage `6d88ed1fc26c74d8e5ad0d0e0fdef09e38560d81`; reconciled head `83243ba32729a75e953125370a8cb0b61cee197f` | [#9](https://github.com/ed3c/ai-product-notes/pull/9) | `MERGED@fe7e03557f07b7c9ae91210d0405745b870dafcc` |
| CI evidence | [#10](https://github.com/ed3c/ai-product-notes/issues/10) | `agent/10-exact-head-ci` | `agent/6-portfolio-convergence@83243ba32729a75e953125370a8cb0b61cee197f`; retargeted to `main@fe7e03557f07b7c9ae91210d0405745b870dafcc` | stage `5b646ec6fe70dd2047734636b8dfd517ee2998b2`; final head `e37bf18dd39f91f207753d6aaad546125b62a6f1` | [#11](https://github.com/ed3c/ai-product-notes/pull/11) | `MERGED@0e2654f6a89c6110728950161d968b233c7e96b4` |
| Final reconciliation | [#12](https://github.com/ed3c/ai-product-notes/issues/12) | `agent/12-final-stack-reconciliation` | `main@0e2654f6a89c6110728950161d968b233c7e96b4` | current head is authoritative in PR metadata | final reconciliation PR | `IN_REVIEW` until subject-bound CI and merge |

## Admission sequence

1. `PASS` — PR #7 merged as `bfe03383e96183d6b6eebd24462742090c733811`.
2. `PASS` — PR #8 was retargeted to `main` and merged as `3fc46a25cc0089e092373b1a0c92a0780f91a5a2`.
3. `PASS` — PR #9 was retargeted to `main` and merged as `fe7e03557f07b7c9ae91210d0405745b870dafcc`.
4. `PASS` — PR #11 was retargeted to `main`, revalidated in both CI lanes, and merged as `0e2654f6a89c6110728950161d968b233c7e96b4`.
5. `RUNNING` — Issue #12 reconciles merged-state documentation. Its exact PR number, head, workflow and merge receipt are authoritative in GitHub metadata because a commit cannot truthfully embed its own final SHA.

No force-update, automatic conflict resolution, `git town ship`, production promotion or roadmap upgrade occurred.

## Hosted subject evidence

### Stage receipt

Run `31878162441` is bound to the immutable CI stage head:

| Lane | Subject | Bound lineage | Result |
|---|---|---|---|
| Exact head contracts | `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | explicit checkout ref equals `EXPECTED_SUBJECT` | `PASS`; repository contract, 23 tests, packet reproduction |
| Synthetic merge compatibility | `3bb417881393b5faad2a91056c49c77eefeb3cc8` | base `83243ba32729a75e953125370a8cb0b61cee197f`, head `5b646ec6fe70dd2047734636b8dfd517ee2998b2` | `PASS`; repository contract, 23 tests, packet reproduction |

### Pre-retarget terminal receipt

Run `31878346277` proved exact head `ac66cc60963b77c5f5872d0825c40319c2bfa855` and synthetic merge `c2336332cc279142194beaae39a04b248f45b7ed` with 24 tests and packet reproduction in both lanes. It remains evidence only for those exact subjects.

### Final retarget receipt

Run `31881831160` proved the actual PR #11 subjects after its base changed to admitted `main`:

| Lane | Subject | Bound lineage | Result |
|---|---|---|---|
| Exact head contracts | `e37bf18dd39f91f207753d6aaad546125b62a6f1` | explicit checkout ref equals the PR head | `PASS`; repository contract, 24 tests, packet reproduction |
| Synthetic merge compatibility | `3fad2f88232fc489bc1cf0af4a68d2779944451b` | base `fe7e03557f07b7c9ae91210d0405745b870dafcc`, head `e37bf18dd39f91f207753d6aaad546125b62a6f1` | `PASS`; parent assertions, repository contract, 24 tests, packet reproduction |

All three are `HOSTED_VERIFIED` receipts for their exact subjects. The earlier single-job PR #8/#9 runs checked synthetic merge commits only and are not relabeled as exact-head evidence.

## Path-lease reconciliation

- PR #7 owned repository governance, Agent routing, architecture, State Machine and Git profile paths.
- PR #8 owned compiler, schemas, asset/portfolio fixtures, tests and workflow paths.
- PR #9 owned opportunity, experiment, roadmap and portfolio handoff, then reconciled the first three leaves.
- PR #11 owned exact-head/synthetic-merge separation and terminal CI index updates.
- Issue #12 owns only `README.md` and `docs/git/STACKED_PRS.md` for final merged-state reconciliation.
- All leaves used one active branch writer and explicit parent/path scope.

## Evidence state

```text
historical branch hierarchy through GitHub API: PUBLISHED
historical draft PR stack: DRAFT_PUBLISHED (#7 → #8 → #9 → #11)
parent and terminal implementation leaves merged: PASS (#7, #8, #9, #11)
control-plane main merge: PASS (0e2654f6a89c6110728950161d968b233c7e96b4)
exact-head stage receipt: PASS (run 31878162441, subject 5b646ec6fe70dd2047734636b8dfd517ee2998b2)
synthetic-merge stage receipt: PASS (run 31878162441, subject 3bb417881393b5faad2a91056c49c77eefeb3cc8)
pre-retarget terminal receipt: PASS (run 31878346277)
final retarget receipt: PASS (run 31881831160)
final documentation reconciliation: IN_REVIEW (Issue #12)
shared Git Town method: DOCUMENTED
exact Git Town executable admission: ABSENT / BLOCKED_POLICY
live Git Town sync: NOT_EXERCISED
worktree, lease and conflict canaries: NOT_EXERCISED
hosted CI: read from exact workflow run; workflow file alone is not PASS
customer-origin evidence: ABSENT
paid demand and revenue: ABSENT
market decision: VALIDATE
```

## Non-claims

- The API-created branch graph proves Git ancestry and PR bases, not a live Git Town execution.
- A permissive code license does not establish rights to model weights, datasets, trajectories, hosted services or third-party content.
- A portfolio match is a candidate integration contract, not technical equivalence.
- A deterministic opportunity packet and merged control plane do not prove buyer demand.
- `VALIDATE` is not `BUILD`, paid pilot, market validation, production release or revenue.
