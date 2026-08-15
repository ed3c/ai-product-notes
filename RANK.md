# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權。

### Verified ranking — 2026-08-15

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
| 13 | BrowserAct Skills | browser automation / agent Skill runtime | PASS / MIT code; managed cloud/proxy scope separate | 10 | 8 | 7 | 8 | 10 | 8.6 |
| 14 | DeepSeek Harness | composable agent harness / plugin runtime | PASS / MIT code | 9 | 8 | 10 | 6 | 10 | 8.6 |
| 15 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 16 | NVIDIA-NeMo/Switchyard | LLM protocol translation & routing proxy | PASS / Apache-2.0 code | 9 | 9 | 9 | 5 | 10 | 8.4 |
| 17 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 18 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |
| 19 | Aureka OpenDDE | biomolecular foundation model / drug-discovery engine | PASS / Apache-2.0 code + released checkpoints; datasets/search DB scope separate | 7 | 8 | 10 | 5 | 8 | 7.6 |

### 2026-08-15 新增驗證

**BrowserAct Skills**
- Primary repo: https://github.com/browser-act/skills
- Immutable verification commit: `8f287271faa0c1df79a44578cb059102ff004da2`
- Primary code license: https://github.com/browser-act/skills/blob/8f287271faa0c1df79a44578cb059102ff004da2/LICENSE
- License gate: `PASS / MIT` **for repository code only**.
- 技術價值：agent-oriented browser automation CLI / Skills，支援 local Chrome state reuse、isolated stealth sessions、parallel sessions、human handoff、CAPTCHA helper、compact indexed state，以及 Claude Code、Cursor、OpenCode、OpenClaw、Codex、Gemini CLI 等 agent surfaces。Repository 在本次驗證時約 5.4k GitHub stars，具備比純 prototype 更強的 adoption evidence。
- Business boundary：BrowserAct Cloud、managed proxy、paid browser infrastructure 與其他 hosted services 不因 repository MIT license 而自動取得相同授權；third-party website terms、content/data rights 也必須獨立處理。
- Production caution：anti-bot / CAPTCHA success claims 主要來自 upstream 與使用者 testimonials；不把這些數值視為獨立 benchmark。Production score 因 real users、multi-platform compatibility 與可本機執行而給 8/10，但不是 security/compliance certification。

**DeepSeek Harness**
- Primary repo: https://github.com/deepseek-ai/deepseek-harness
- Immutable verification commit: `47f943859bef60e4160492346772ded9b24f765a`
- Primary code license: https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/LICENSE
- Architecture: https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/architecture.md
- License gate: `PASS / MIT` **for repository code only**.
- 技術價值：Cordis-based「everything is a plugin」runtime，model adapter、tool registry、session log、agent loop、sandbox/approval policy、credentials、telemetry 與 UI 都可組合/替換。Append-only durable `SessionEvent` log 支援 replay、fork/resume、recovery 與 telemetry，且 upstream 定義 `Model-visible means logged` invariant，使其很適合作為 harness architecture、trace/eval、plugin compatibility 與 agent-runtime research reference。
- Production risk：upstream 明確標示 **developer preview** 並警告會有 compatibility-breaking changes，所以 Production score 僅 6/10。這個風險同時創造 plugin compatibility / regression certification 的商業切入點。
- Asset boundary：MIT code license 不代表 DeepSeek model weights、external datasets、third-party plugins 或 trajectories 自動為 MIT；本次只將 runtime code 列為 PASS。

### 2026-08-14 新增驗證

**Aureka OpenDDE**
- Primary repo: https://github.com/aurekaresearch/OpenDDE
- Immutable verification commit: `d42760d264637a4518c0ab56d021451b9888d1f9`
- Primary code license: https://github.com/aurekaresearch/OpenDDE/blob/d42760d264637a4518c0ab56d021451b9888d1f9/LICENSE
- Model repository: https://huggingface.co/aurekaresearch/OpenDDE
- License gate: `PASS / Apache-2.0` for repository code and the released OpenDDE checkpoints according to Aureka's release statement and model repository. **No commercial-rights inference is made for training datasets, external sequence/template search databases, or third-party biological data.**
- 技術價值：open-source all-atom biomolecular foundation model，涵蓋 proteins、nucleic acids、small molecules 的 co-folding；提供 Python package、CLI、Docker、CPU/GPU inference、released checkpoints 與 multi-GPU Fold-CP。適合作為 drug-discovery research / evaluation / model-serving reference stack，而不是通用 LLM infrastructure。
- Research value：training code、inference pipeline、checkpoints、benchmarks 與 technical report 可用於 reproduction 與 comparative research；upstream 同時提供固定 checkpoint hashes / runtime setup。
- Production risk：README 明確標示 preview release、released checkpoints/API 可能變更、predictions 跨 release 不保證 reproducibility，且 **not yet intended for production pipelines**，因此 Production score 僅 5/10。
- Data/trajectory boundary：本次未找到一個可獨立再利用、具明確 permissive license 的 training dataset 或 trajectory corpus，因此 `data` / `trajectory` 不列為 PASS asset。

### 2026-08-12 新增驗證

**NVIDIA-NeMo/Switchyard**
- Primary repo: https://github.com/NVIDIA-NeMo/Switchyard
- Immutable verification commit: `58f355a132d6fdd95191501aaa8522e100e06834`
- Primary license: https://github.com/NVIDIA-NeMo/Switchyard/blob/58f355a132d6fdd95191501aaa8522e100e06834/LICENSE
- License gate: `PASS / Apache-2.0` **for repository code only**.
- 產品價值：Rust-based LLM traffic proxy/library，可在 OpenAI Chat、OpenAI Responses、Anthropic Messages 之間做 protocol translation，並把 Claude Code / Codex 等 client 導向 vLLM、NVIDIA NIM、Ollama 或 OpenAI-compatible backends。提供 classifier/stage/escalation/random routing 與 Prometheus metrics，適合作為 multi-model routing、A/B benchmark、fallback 與 agent protocol interoperability 的 reference implementation。
- Evidence boundary：本次沒有把任何 Nemotron model weights、training data 或 trajectory 視為同一授權資產；這些必須另外讀 model card / dataset license 才能進榜。
- Production risk：upstream README 明確標示 **pre-alpha / experimental / not for production use**，因此 Production score 僅 5/10。API 與 routing algorithms 在 v1.0 前可能有大幅變更。

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

### New verified assets — 2026-08-15

**BrowserAct Skills** enters at rank 13 with an internal 8.6 average. Repository code was verified at commit `8f287271faa0c1df79a44578cb059102ff004da2` under MIT. It is a high-leverage browser automation and agent-Skill reference with local browser reuse, session isolation, human handoff, compact agent-oriented state, and broad coding-agent compatibility. The MIT decision covers repository code only; BrowserAct Cloud, managed proxy/browser services, third-party site terms, and collected-data rights remain separate.

**DeepSeek Harness** enters at rank 14 with an internal 8.6 average. Repository code was verified at commit `47f943859bef60e4160492346772ded9b24f765a` under MIT. Its Cordis architecture makes the model adapter, tool registry, session log, agent loop, policy/sandbox layer, and UI replaceable plugins. The durable session event log and model-visible logging invariant make it a strong harness, replay, audit, and compatibility research asset. Production maturity is deliberately scored lower because upstream labels the project a developer preview and warns of compatibility-breaking changes. No model-weight, dataset, plugin, or trajectory license is inferred from the runtime code license.

### New verified asset — 2026-08-14

**Aureka OpenDDE** is now rank 19 after new 2026-08-15 entries, while retaining an internal 7.6 average. Repository code was verified at commit `d42760d264637a4518c0ab56d021451b9888d1f9` under Apache-2.0. Aureka's release statement and the Hugging Face model repository also identify the released OpenDDE checkpoints as Apache-2.0. This decision does not extend to training datasets, external search databases, or third-party biological data. OpenDDE is a strong research and reproduction asset for all-atom co-folding and drug-discovery workflows, but its production score is intentionally low because upstream labels it a preview release and explicitly says it is not yet intended for production pipelines.

### Previous verified assets

**NVIDIA-NeMo/Switchyard** is now rank 16 at 8.4 after the new entries. Its repository code remains Apache-2.0 and useful for protocol translation and model routing, but upstream still labels it pre-alpha and not for production.

**Paritok gateway + Paritok-4B-v1** remains rank 11 at 8.6. Repository code/gateway and the adapter are Apache-2.0; the training trajectories remain excluded as a reusable data asset until a separate license is verified.

**Prime Agent** remains rank 12 at 8.6 under MIT. It is useful for persistent and self-improving agent patterns but requires mutation governance and rollback.

**AgentConnect** is now rank 15 at 8.4 under Apache-2.0 and remains a strong reference for heterogeneous multi-agent collaboration and permission-aware control planes.

**Soup CLI** remains useful for local post-training, with layer streaming explicitly treated as BETA rather than production-proven.

`MemoryCustodian` remains attractive for repository-native project memory and cross-agent interoperability but has lower production evidence. `Spine-AI/medley` remains conditional because only its plugin shim is MIT while the engine is proprietary.
