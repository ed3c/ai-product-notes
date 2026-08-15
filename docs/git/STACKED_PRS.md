# Stacked PR ledger

Epic: #3 — Market-to-MVP control plane.

## Planned graph

```text
main@ab9596ff1df2b44785e28baad650f93f21b9786c
└── agent/4-market-control-plane
    └── agent/5-opportunity-compiler
        └── agent/6-portfolio-convergence
```

| Leaf | Issue | Branch | Parent / PR base | Path owner | PR | State |
|---|---:|---|---|---|---:|---|
| Governance | #4 | `agent/4-market-control-plane` | `main` | Agent/docs/git contracts | TBD | `ISSUE_SCOPED` |
| Compiler | #5 | `agent/5-opportunity-compiler` | Leaf 01 | compiler/schemas/assets/tests | TBD | `ISSUE_SCOPED` |
| Convergence | #6 | `agent/6-portfolio-convergence` | Leaf 02 | opportunity/roadmap/shared indexes | TBD | `ISSUE_SCOPED` |

## Merge order

1. Review and admit Leaf 01.
2. Retarget/reconcile Leaf 02 to `main` after Leaf 01 merges.
3. Retarget/reconcile Leaf 03 after Leaf 02 merges.
4. Update the ledger from exact remote state.

## Git Town status

```text
branch hierarchy: PLANNED
shared method: DOCUMENTED
exact executable admission: ABSENT / BLOCKED_POLICY
live sync: NOT_EXERCISED
worktree and lease canaries: NOT_EXERCISED
Draft PR publication: NOT_EXERCISED
merge/ship: HUMAN ADMIT
```

A manually created compatible branch graph is not evidence that Git Town was installed or run.
