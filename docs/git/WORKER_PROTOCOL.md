# Worker protocol

## Task admission

A Worker starts only after the Issue defines:

- goal and non-goals;
- exact parent branch/SHA;
- branch name and PR base;
- disjoint path lease;
- required state transition;
- validation commands;
- planted negative controls;
- evidence boundary and non-claims;
- cleanup and rollback subject.

Missing input is `ABSENT`; do not infer it.

## One-writer law

One mutable branch has one active writer. A Worker may edit only its leased paths. Independent leaves use sibling branches. When multiple leaves need README, aggregate indexes or generated manifests, one convergence leaf owns those files.

## Sync and conflict policy

- No background push.
- No automatic semantic resolution.
- No automatic `continue`, `skip`, `undo`, `ship`, merge or force-update.
- Dirty worktree, wrong parent, overlapping lease, prompt, timeout, ancestry drift or conflict stops the Worker and preserves state.
- `git town sync` exit `0`, when eventually exercised, proves synchronization only.

## Publication

Draft PR publication requires exact parent/head reconciliation and validation receipts. Ready-for-review, merge and roadmap promotion are separate Human Admit decisions. Hosted CI status must be read from its exact run; absence is `NOT_EXERCISED` or `BLOCKED`, never PASS.

## Completion packet

```yaml
issue: null
branch: null
parent: null
head: null
path_lease: []
validation: []
negative_controls: []
publication: NOT_EXERCISED
hosted_ci: NOT_EXERCISED
git_town_sync: NOT_EXERCISED
human_admit: REQUIRED
remaining_gaps: []
non_claims: []
rollback_subject: null
```
