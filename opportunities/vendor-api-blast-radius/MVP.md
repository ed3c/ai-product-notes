# Vendor API Blast-Radius CI｜14-Day Market Validation MVP

## Decision snapshot

```text
decision: VALIDATE
score: 62.06 / 100
portfolio_fit: 3.33 / 10
commercial substitution coverage: 5.00 / 10
paid demand: ABSENT
customer-origin evidence: ABSENT
uncovered must capability: callsite-impact-join
```

The current evidence supports a bounded test, not product build-out. Official vendor change surfaces and a direct competitor make the problem legible and recurrent, but they do not prove that this exact buyer segment will pay.

## Target segment

Start with **10–100 engineer B2B SaaS teams** that:

- ship TypeScript services;
- depend on at least one fast-changing AI-model API;
- review changes in GitHub pull requests;
- have experienced deprecation, model/version, schema or SDK migration work;
- can name the person who owns reliability or developer-platform budget.

Avoid agencies with no owned runtime, hobby repositories, teams unable to provide a sanitized fixture, and enterprises that require broad procurement before a two-week design-partner test.

## Narrow wedge

```text
one TypeScript repository
+ one AI-model API family
+ one historical vendor change feed/spec snapshot pair
→ used endpoint/field map
→ exact source anchors
→ relevance classification
→ one evidence-linked GitHub Check
```

The MVP reports impact. It does not automatically edit code.

## User workflow

1. A design partner installs a least-privilege GitHub App or supplies a sanitized fixture.
2. The tool extracts API client construction and calls from the exact commit.
3. A pinned vendor spec/changelog snapshot is compared with the previous snapshot.
4. The proprietary join maps changed API surface to observed call-sites.
5. A GitHub Check reports only relevant changes with file/symbol evidence and limitations.
6. The developer marks each finding `relevant`, `false_positive`, `missed` or `unknown`.
7. The experiment records quality, time saved, repeat intent and price response.

## Stack map

| Layer | Candidate | Right state | Role | Remaining gap |
|---|---|---|---|---|
| TypeScript/source parsing | Tree-sitter core at `dff1fd8…` and/or ts-morph at `699815f…` | code `PASS` / MIT | syntax and TypeScript call-site extraction | dynamic factories, wrappers and aliases need fixtures |
| Vendor schema diff | OpenAPI Diff at `63850d8…` | code `PASS` / Apache-2.0 | classify endpoint/field changes | vendor specs may be incomplete |
| GitHub delivery | Octokit REST.js at `cd9cb8c…` | code `PASS` / MIT | publish authorized Check output | GitHub App permissions/service terms remain separate |
| Source evidence | public repository-source-anchoring capability | `TESTED` candidate for exact anchors | path/quote/subject binding | lexical evidence is not semantic impact |
| Current claim capture | public current-claim-verification capability | `TESTED` candidate | re-fetch and receipt vendor evidence | provenance is not relevance |
| Call-site × vendor-change join | no admitted public/private capability | `GAP` | product differentiator | must be implemented and replay-tested |
| Python expansion | LibCST at `d9a2558…` | code `PASS`; permissive file-scoped licenses | later language support | excluded from first wedge |

All listed `PASS` states cover repository code only. Model, dataset, trajectory, hosted-service, trademark, patent and third-party-content rights remain separately scoped.

## Proprietary value layer

The moat is not the parser or OpenAPI diff. It is the evidence-preserving join:

```text
repository commit
→ client construction and call-site graph
→ normalized API operation/field identity
→ versioned vendor-change event
→ relevance rule + confidence + limitations
→ developer feedback and replay corpus
```

The first version may use bounded rules and manually reviewed fixtures. It must not hide uncertain mappings behind an LLM-generated confident answer.

## 14-day execution

### Days 1–2 — Problem and buyer gate

- Interview 10 qualified teams.
- Ask for the last concrete vendor API change, detection path, engineering time, production risk and budget owner.
- Obtain at least 3 strong confirmations of the exact call-site impact problem.
- Ask for permission to use a sanitized repository/spec fixture.

### Days 3–5 — Replay fixture

- Select one TypeScript SDK shape and one AI API family.
- Bind two vendor snapshots/changelog events and known affected call-sites.
- Build the source extractor and canonical operation identity.
- Record misses instead of hand-editing expected outputs after seeing results.

### Days 6–8 — Impact join

- Join source usage to vendor changes.
- Emit `affected`, `possibly_affected`, `not_used` and `unknown` with evidence.
- Run two bounded repair passes only against declared failure categories.

### Days 9–10 — Delivery surface

- Publish a read-only GitHub Check on a fixture/design-partner PR.
- Include exact source anchors, vendor evidence, confidence and a feedback action.
- No automatic patch, merge, deployment or permission widening.

### Days 11–12 — Historical replay

- Replay at least 12 months of changes across up to 10 repositories/fixtures.
- Require at least 5 relevant detected breakages.
- Measure false positives, misses, analysis time and reviewer effort.

### Days 13–14 — Price gate

- Demonstrate the result to design partners.
- Present **US$99/repository/month** and a bounded paid pilot.
- Request payment, preorder or signed pilot commitment; compliments and waitlist entries do not satisfy this gate.

## Success metrics

- 10 qualified interviews and at least 3 strong pain confirmations.
- At least 5 relevant historical breakages found.
- False-positive rate below 10% on the admitted fixture set.
- First-wedge impact report in under 5 minutes.
- Two paid pilots or equivalent binding commitments at US$99/repository/month.

## Stop-loss

- Stop after 10 interviews when fewer than 3 confirm the exact problem.
- Narrow or stop when false-positive rate remains 20% or higher after two bounded repairs.
- Stop when the replay contains fewer than 3 relevant historical changes.
- Stop when the required vendor evidence cannot be acquired under acceptable rights/terms.
- Stop when the buyer values generic changelog summaries but not repository-specific impact.

## Non-goals

- automatic code repair;
- every language, SDK or vendor;
- a universal API knowledge graph;
- production write access;
- private repository ingestion into this public repository;
- declaring market validation before paid-pilot receipts exist.

## Graduation

`VALIDATE → BUILD` requires all of the following:

1. direct paid-demand receipt;
2. two or more independent demand origins, including customer-origin evidence;
3. replay thresholds passed on exact subjects;
4. the `callsite-impact-join` capability materialized and independently tested;
5. a durable implementation owner selected;
6. Human Admit of scope, rights, security and delivery boundaries.
