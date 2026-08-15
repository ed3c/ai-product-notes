# Git and Stacked PR governance

This directory is the repository-owned binding for the shared `git-town-stacked-pr-worker` method. The shared Skill owns the portable method; this repository owns its profile, Issues, branch graph, path leases, checks, workflows and receipts.

Read in order:

1. `REPO_PROFILE.md`
2. `WORKER_PROTOCOL.md`
3. `STACKED_PRS.md`
4. `GIT_TOWN_ADMISSION.md`
5. the assigned Issue/work packet

Current boundary:

```text
shared Skill binding: DOCUMENTED
repository profile: MATERIALIZED
Issue/path-lease graph: MATERIALIZED
remote branch/PR graph: PLANNED until published
exact Git Town admission: ABSENT / BLOCKED_POLICY
live Git Town sync: NOT_EXERCISED
worktree/lease/conflict canaries: NOT_EXERCISED
hosted CI: NOT_EXERCISED until a subject-bound run exists
merge/ship: HUMAN ADMIT
```

Do not infer stronger states from branch names or documentation.
