# Agent Contract Evolution Replay CI

State: `VALIDATE / NOT_EXERCISED_ON_REAL_HISTORY`

## Hypothesis

A versioned tool/skill/harness contract change can be replayed deterministically against previously successful trajectories to identify compatibility breaks before the changed contract is admitted.

## Inputs

```text
old_contract.json
new_contract.json
known_good_trajectory.json
```

The public experiment uses synthetic fixtures only. Private repository names, customer data, raw production traces, credentials and proprietary prompts are forbidden from committed fixtures.

## First replay rules

A historical call is impacted when any of these is true:

1. the called tool no longer exists;
2. the new contract adds a required argument that the historical successful call did not provide;
3. a historical enum value is no longer admitted;
4. the trajectory calls a tool absent from the declared historical contract.

## Receipt

A replay receipt must bind:

```text
old contract digest
new contract digest
trajectory digest
replayed tool-call count
impact count
per-step reason
PASS | BREAKING
```

The receipt must be canonical and deterministic for identical inputs.

## Runtime gate

The thin slice is only technically admitted when hosted CI proves:

- planted removed-tool breakage is detected;
- planted required-argument breakage is detected;
- planted enum drift is detected;
- a compatible contract evolution returns PASS;
- repeated execution produces byte-identical receipt output.

## Market gate

Technical PASS is not `BUILD`. Promotion requires at least:

- 3 qualified teams confirming recurring contract-evolution pain;
- 5 independently adjudicated real historical breakages;
- acceptable false-positive and unknown rates;
- evidence that the workflow is not already sufficiently solved by generic replay/eval products;
- paid pilot or equivalent binding commitment according to the repository market contract.

## Non-goals

- semantic tool equivalence;
- automatic migration or repair;
- LLM-based judging;
- production interception;
- universal MCP/Agent Skills/provider compatibility;
- storing private trajectories in this public repository.
