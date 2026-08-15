# Git Town admission

No Git Town executable is admitted for this repository at this snapshot. Therefore this repository intentionally does not commit `.git-town.toml` or a sync wrapper.

## Required evidence before admission

- upstream source and immutable version/tag/commit;
- platform and architecture;
- binary/package checksum;
- provenance or package-manager lock;
- direct license bytes and digest;
- transitive dependency/SBOM review;
- required notices and service/host terms;
- repository policy for feature-history rewriting;
- worktree support and one-writer lease canary;
- dry-run/no-push synchronization canary;
- deterministic conflict that fails closed;
- cleanup/residue evidence;
- publication guard and exact-head ancestry check.

## Current state

| Evidence | State |
|---|---|
| Exact version | `ABSENT` |
| Executable checksum/provenance | `ABSENT` |
| License/SBOM admission | `ABSENT` |
| Repository config | `ABSENT_BY_POLICY` |
| Local worktree canary | `NOT_EXERCISED` |
| No-push sync canary | `NOT_EXERCISED` |
| Conflict canary | `NOT_EXERCISED` |
| GitHub publication gate | `NOT_IMPLEMENTED` |
| Human merge authority | `REQUIRED` |

Documentation and a branch hierarchy may proceed, but no completion report may upgrade these states without subject-bound receipts.
