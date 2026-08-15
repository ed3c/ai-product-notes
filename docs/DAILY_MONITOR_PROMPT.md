# Daily Monitor Contract / 每日監控契約

## Objective

Run one trailing-24-hour AI product and funding monitor, then convert only the strongest signals into versioned opportunity inputs. The output is not a list of exciting launches; it is a delta to the evidence base and, when justified, a falsifiable market-validation packet.

## Procedure

1. Read `README.md`, `docs/CONFIG.md`, `docs/STATE_MACHINES.md`, `docs/MARKET_SIGNAL_CONTRACT.md`, `CONTEXT.md`, `RANK.md`, `data/products/index.json` and current datasets.
2. Search primary launch pages, official company/docs/pricing/changelog sources and reputable funding reporting. Bind `event_date`, `source_date`, official identity and source class.
3. Reject unverifiable dates, stale re-indexing, duplicates and conflicting launch histories. Zero qualified items is valid.
4. Keep at most 5–10 highest-quality signals. Separate vendor claims, independent evidence, customer evidence, experiment evidence and inference.
5. Analyze buyer, painful job, recurrence, budget owner, business model, price/WTP evidence, competition, distribution, operational barrier, margin and narrow wedge.
6. For each high-value candidate, create a `market-signal.v1` input and decompose the workflow into required capabilities.
7. Map candidates to `code | model_weights | datasets | trajectories | hosted_service | third_party_content`. Verify each right from primary evidence. Only direct `PASS` states count.
8. Match required capabilities against `config/public-portfolio.json` and an optional Git-ignored private overlay. Never write private repo names, paths, URLs, code, raw traces, customer data or credentials to public output.
9. Classify `market`, `evidence`, `stack`, `portfolio`, `delivery` and `rights_privacy` gaps. Record `not_found` rather than omitting missing evidence.
10. Run the deterministic opportunity compiler. A high score cannot override a hard gate; missing paid demand caps the decision at `VALIDATE`.
11. Write deep notes for Top-3/evidence-heavy cases, update only true dataset deltas, and preserve historical timestamps and dropped-item notes.
12. Create or update `opportunities/<slug>/` only through the `PRODUCT_CHANGE_LANE`. Routine dated notes/data may use `DATA_INCREMENT_LANE` only when its exact automation is already admitted.
13. Update `roadmap/` only after experiment receipts and Human Admit. Never call a generated packet `market validated`, `paid`, `done` or `shipped`.
14. Never write canonical data to Google Sheets, Google Docs or Excel; never commit secrets or private data.

## Required daily output

- monitor window and qualified count;
- source/evidence table with event date;
- product/ranking delta;
- capability and permissive-asset mapping;
- explicit gaps and `not_found` items;
- opportunity decisions with score and hard gates;
- roadmap impact, normally `none` unless evidence materially changed;
- non-claims and remaining validation work.
