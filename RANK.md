# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權。

### Verified ranking — 2026-08-11

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
| 11 | Paritok gateway + Paritok-4B-v1 | coding-agent context compression | PASS / Apache-2.0 code + adapter; Qwen base Apache-2.0 | 10 | 9 | 9 | 6 | 9 | 8.6 |
| 12 | Prime Agent | self-improving coding/research agent | PASS / MIT | 9 | 8 | 10 | 7 | 9 | 8.6 |
| 13 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 14 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 15 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |

### 2026-08-11 新增驗證

**Paritok gateway + Paritok-4B-v1**
- Primary repo: https://github.com/Paritok-official/paritok-4b-v1
- Primary code license: https://github.com/Paritok-official/paritok-4b-v1/blob/main/LICENSE
- Adapter/model card: https://huggingface.co/paritok/paritok-4b-v1
- Base model: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- License gate: `PASS` for repository code/gateway and Paritok adapter under Apache-2.0; Qwen base model card also states Apache-2.0.
- 產品價值：drop-in context-compression gateway，針對 tool schemas、file/tool outputs、stale history 做可回復壓縮，適合 Claude Code、Codex、Cursor、OpenHands 與 OpenAI/Anthropic-compatible agents。
- Evidence caution：compression / SWE-bench quality 數字為 upstream self-reported。45K training trajectory samples 的完整可再利用 dataset + independent commercial data license 尚未驗證，因此 **trajectory/data 不列為 PASS asset**。
- Production risk：identifier loss、語言/程式語言 distribution 偏差、agent protocol churn、provider caching interaction。

**Prime Agent**
- Primary repo: https://github.com/PrimeIntellect-ai/prime-agent
- Primary license: https://github.com/PrimeIntellect-ai/prime-agent/blob/main/LICENSE
- License gate: `PASS / MIT`
- 產品價值：persistent Python REPL、recursive subagents、daemon-backed sessions、persistent goals、heartbeats/schedules，以及可把 trajectory evidence 轉為 prompts / memories / skills / subagent specs 的 Continual Harness。
- Safety boundary：upstream README 明確指出 worker/kernel isolation 不是 security sandbox；agent 執行 model-generated Python 與 project commands 時具有使用者權限。Self-refinement 因此需要 mutation audit、regression gate 與 rollback。
- Scope caution：MIT code license 不代表外接 models、datasets、skills、extensions 自動具有相同權利，必須逐項驗證。

### 2026-08-10 新增驗證

**AgentConnect**
- Primary repo: https://github.com/agentconnect-md/agentconnect
- Primary license: https://github.com/agentconnect-md/agentconnect/blob/main/LICENSE
- License gate: `PASS / Apache-2.0`
- 產品價值：將 Claude Code、Codex、Gemini CLI 與 ACP-compatible agents 接進 Slack/Telegram/Discord/GitHub，並提供 per-agent runtime/model/workspace/memory/tools/skills/permissions/placement 與 centralized control plane。
- 生產風險：安全邊界、daemon/credential handling、SSO/public ingress 與 runtime churn 需要更完整的 production evidence。

**Soup CLI**
- Primary repo: https://github.com/MakazhanAlpamys/Soup
- Primary license: https://github.com/MakazhanAlpamys/Soup/blob/main/LICENSE
- License gate: `PASS / Apache-2.0`
- 產品價值：統一 SFT/DPO/GRPO/KTO、eval/gating/export 與多種 serving/training stack；layer streaming 可讓 frozen base 從 RAM/NVMe 逐 layer 進 GPU，目標是降低本機 fine-tuning VRAM 門檻。
- 驗證限制：官方明確將 layer streaming 標為 BETA；公開的 RTX 3050 4 GB throughput 數字早於 v0.73.0 correctness repair，官方也註明尚未在該卡重新測量，因此不得把舊 throughput 當成當前 release 的已重驗 performance claim。

`MemoryCustodian` 仍適合 repository-native Markdown memory、manifest routing、cross-agent adapters 與 reproducible evaluation artifacts，但 production maturity 低於成熟 infrastructure projects。

### Conditional / excluded from formal rank

- `Spine-AI/medley`: `CONDITIONAL`。Repository plugin shim 是 MIT，但 LICENSE 明確指出 Medley engine 是 proprietary/closed source，且產品本身不是 open source，因此不能視為完整可替代產品的 OSS implementation asset。

## English

Only `PASS` entries receive a formal rank. Code, model weights, datasets, and trajectories require separate license verification. A permissive code license never proves that bundled data or model assets are commercially reusable.

Evaluation dimensions: Hackathon MVP speed, Business monetization leverage, Research/reproducibility value, Production maturity, and compatibility with common production AI stacks.

### New verified assets — 2026-08-11

**Paritok gateway + Paritok-4B-v1** enters at rank 11 with an internal 8.6 average. The repository code/gateway and Paritok adapter are Apache-2.0, and the Qwen3-4B-Instruct-2507 base model card also states Apache-2.0. Its strongest value is a reversible, drop-in context-compression layer for coding agents. Upstream benchmark and savings numbers are treated as self-reported evidence. The 45K training trajectories are not ranked as a reusable trajectory/data asset because an independently licensed public dataset was not verified.

**Prime Agent** enters at rank 12 with an internal 8.6 average. The repository is MIT licensed. Its persistent REPL, recursive subagents, daemon-backed continuity, and Continual Harness are strong reference patterns for long-running and self-improving agents. Production scoring is deliberately lower because the upstream project explicitly warns that it is not a security sandbox and self-modifying harness state creates new governance and rollback requirements.

### Previous verified assets — 2026-08-10

**AgentConnect** is Apache-2.0 and remains a strong reference implementation for vendor-neutral multi-agent collaboration, identity/permissions, placement, shared channels, and heterogeneous runtimes. Production risk remains around security boundaries, credential handling, public ingress, and fast-moving runtime integrations.

**Soup CLI** is Apache-2.0 and remains useful for local fine-tuning/post-training workflows. Its flagship layer-streaming path is explicitly BETA, and historical throughput results are not treated as current-release benchmark proof.

`MemoryCustodian` remains attractive for repository-native project memory and cross-agent interoperability but has lower production evidence. `Spine-AI/medley` remains conditional because only its plugin shim is MIT while the engine is proprietary.
