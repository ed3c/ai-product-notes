# Vendor API Blast-Radius experiment contract

State: `NOT_EXERCISED`

This directory defines the market and replay experiment. It contains no participant data and no success receipt.

## Receipt rules

Every interview, replay or pilot receipt must bind:

- anonymized participant/fixture ID;
- exact repository/spec subject digest where applicable;
- actor and independent reviewer role;
- timestamp and experiment version;
- observed result, not only a summary;
- metric numerator/denominator;
- exclusions and limitations;
- consent/right to store the sanitized receipt;
- commercial commitment state.

Raw customer conversations, private code, repository URLs, credentials and sensitive logs remain outside this public repository. A public aggregate may be committed only after privacy review and minimum-group protection.

## Interview gate

Use concrete-history questions:

1. What was the last vendor API change that affected your code?
2. How was it discovered, and how long did impact analysis take?
3. Which failure reached production or delayed delivery?
4. Which repository/language/vendor would be the first test?
5. Who owns the budget and what do they pay for adjacent reliability tooling?
6. Would they authorize a paid US$99/repository/month pilot now?

A “sounds useful” answer is not a strong confirmation.

## Replay gate

Metrics:

```text
relevant_recall = detected_relevant / all_adjudicated_relevant
false_positive_rate = false_positive / all_reported
unknown_rate = unknown / all_candidate_mappings
analysis_latency_seconds
review_minutes
```

The fixture author and result evaluator must be separated when practical. Planted negatives must include unused endpoints, renamed local wrappers, dynamic client construction and a vendor change that is breaking globally but irrelevant to the repository.

## Pilot gate

A pilot passes only when technical thresholds pass and the buyer provides a paid or binding commitment. Free usage, a waitlist, social engagement or a competitor price are not payment evidence.

## Current non-claims

- no interviews recorded;
- no repository/spec replay executed;
- no GitHub App installed;
- no hosted CI or production run;
- no paid pilot;
- no market validation.
