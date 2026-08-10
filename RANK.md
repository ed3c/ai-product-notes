# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權。

### Verified ranking — 2026-08-10

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
| 11 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 12 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 13 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |

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

### New verified assets — 2026-08-10

**AgentConnect** is Apache-2.0 and enters at rank 11. It is a strong reference implementation for vendor-neutral multi-agent collaboration, identity/permissions, placement, shared channels, and heterogeneous runtimes. Production risk remains around security boundaries, credential handling, public ingress, and fast-moving runtime integrations.

**Soup CLI** is Apache-2.0 and enters at rank 13. It is useful for local fine-tuning/post-training workflows and integrates with common training and serving stacks. Its flagship layer-streaming path is explicitly BETA. The project states that the published RTX 3050 4 GB throughput numbers predate a correctness repair and have not yet been re-measured on that card, so those numbers are treated as historical measurement evidence rather than current-release benchmark proof.

`MemoryCustodian` remains attractive for repository-native project memory and cross-agent interoperability but has lower production evidence. `Spine-AI/medley` remains conditional because only its plugin shim is MIT while the engine is proprietary.
