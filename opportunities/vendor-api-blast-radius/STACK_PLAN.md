# Molecular terminal implementation plan

This is the planned product implementation stack after experiment admission. No branch or PR below exists yet.

```text
admitted durable-owner main
└── mvp/01-replay-contract-and-fixtures
    └── mvp/02-typescript-callsite-extractor
        └── mvp/03-openapi-change-normalizer
            └── mvp/04-callsite-impact-join
                └── mvp/05-github-check-and-feedback
                    └── mvp/06-pilot-convergence
```

| Leaf | Single trust boundary | Input | Output | Gate |
|---|---|---|---|---|
| 01 | fixture identity and sealed expectations | repository/spec snapshots | replay manifest + expected relevant changes | no hidden truth in Worker input |
| 02 | source extraction | exact repository commit | anchored calls/client construction | deterministic fixture tests |
| 03 | vendor-change normalization | pinned specs/changelog | canonical operation/field changes | incompatible/unknown changes stay explicit |
| 04 | proprietary relevance join | calls + changes | affected/possible/not-used/unknown receipt | recall/FPR thresholds and negative controls |
| 05 | least-privilege delivery | verified impact receipt | GitHub Check + feedback event | permission and subject continuity |
| 06 | market/technical convergence | interview, replay, pilot receipts | build/reject decision + durable roadmap | independent review + Human Admit |

Shared fixtures, aggregate scorecards and the final roadmap index belong only to Leaf 06. Language/vendor expansions become sibling stacks after the first wedge passes.
