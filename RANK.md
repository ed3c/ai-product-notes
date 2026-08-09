# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權。

### Verified ranking — 2026-08-09

| Rank | Asset | Type | License gate | Hackathon MVP | Business | Research | Production | Stack compatibility | Avg |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | LiteLLM core | model gateway | PASS core / MIT; enterprise scope separate | 10 | 9 | 8 | 9 | 10 | 9.2 |
| 2 | vLLM | inference serving | PASS / Apache-2.0 | 8 | 9 | 10 | 10 | 9 | 9.2 |
| 3 | OpenTelemetry Collector | observability | PASS / Apache-2.0 | 8 | 9 | 9 | 10 | 9 | 9.0 |
| 4 | SGLang | inference/agent serving | PASS / Apache-2.0 | 8 | 9 | 10 | 9 | 9 | 9.0 |
| 5 | MLflow | experiment/eval lifecycle | PASS / Apache-2.0 | 9 | 8 | 10 | 9 | 9 | 9.0 |
| 6 | Promptfoo | LLM/agent evaluation | PASS / MIT | 10 | 8 | 9 | 8 | 10 | 9.0 |
| 7 | Temporal | durable execution | PASS / MIT | 8 | 9 | 8 | 10 | 9 | 8.8 |
| 8 | LangChain | agent/RAG framework | PASS / MIT | 10 | 8 | 8 | 8 | 10 | 8.8 |
| 9 | LlamaIndex | data/RAG framework | PASS / MIT | 10 | 8 | 9 | 8 | 9 | 8.8 |
| 10 | Open Policy Agent | policy engine | PASS / Apache-2.0 | 8 | 9 | 8 | 10 | 9 | 8.8 |
| 11 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |

`MemoryCustodian` 是本次新增研究候選：repository-native Markdown memory、manifest routing、Codex/Claude/Gemini adapters、offline-first CLI 與 reproducible evaluation artifacts 對 agent memory / trajectory governance 有直接參考價值，但 production maturity 仍低於成熟 infrastructure projects。

### Conditional / excluded from formal rank

- `Spine-AI/medley`: `CONDITIONAL`。Repository plugin shim 是 MIT，但 LICENSE 明確指出 Medley engine 是 proprietary/closed source，且產品本身不是 open source，因此不能視為完整可替代產品的 OSS implementation asset。

## English

Only `PASS` entries receive a formal rank. Code, model weights, datasets, and trajectories require separate license verification. A permissive code license never proves that bundled data or model assets are commercially reusable.

Evaluation dimensions: Hackathon MVP speed, Business monetization leverage, Research/reproducibility value, Production maturity, and compatibility with common production AI stacks.

`MemoryCustodian` is the newest verified candidate in this revision. It is attractive for repository-native project memory and cross-agent interoperability, but receives a lower Production score until broader operational evidence exists. `Spine-AI/medley` remains conditional because only its plugin shim is MIT while the engine is proprietary.
