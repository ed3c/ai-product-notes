# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權。

### Verified ranking — 2026-08-17

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
| 15 | HarnessRouter Community Edition | unified agent-harness runtime / protocol | PASS / Apache-2.0 repository code | 9 | 9 | 8 | 7 | 10 | 8.6 |
| 16 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 17 | NVIDIA-NeMo/Switchyard | LLM protocol translation & routing proxy | PASS / Apache-2.0 code | 9 | 9 | 9 | 5 | 10 | 8.4 |
| 18 | Blume | AI-ready Markdown documentation framework | PASS / MIT | 10 | 7 | 8 | 8 | 9 | 8.4 |
| 19 | @inferock/measure | LLM billing-integrity measurement library | PASS / Apache-2.0 code | 9 | 8 | 9 | 7 | 8 | 8.2 |
| 20 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 21 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |
| 22 | Aureka OpenDDE | biomolecular foundation model / drug-discovery engine | PASS / Apache-2.0 code + released checkpoints; datasets/search DB scope separate | 7 | 8 | 10 | 5 | 8 | 7.6 |

### 2026-08-17 新增驗證

**HarnessRouter Community Edition**
- Primary repo: https://github.com/HarnessRouter/harnessrouter
- Immutable verification commit: `902c2c2146fb4e4ce5f2c666836a0c203ed706a1`
- Primary code license: https://github.com/HarnessRouter/harnessrouter/blob/902c2c2146fb4e4ce5f2c666836a0c203ed706a1/LICENSE
- License gate: `PASS / Apache-2.0` **for repository code**.
- 技術價值：以 Unified Harness Protocol（UHP）把 Codex、Claude Code、Hermes 等 harness 放在共同 Agent API 後面；提供 session、streaming、files、artifacts、cancellation、failure handling，以及 versioned HTTP contract、OpenAPI 3.1、JSON Schema 2020-12 與 52 runnable conformance checks。Community Edition 將 Gateway、Runner、Console、SQLite state 與 workspace volume 放在 self-hosted container，適合 harness portability、protocol interoperability、cross-harness evaluation 與 self-hosted agent runtime reference。
- Business evidence：Community Edition 免費；managed Cloud 公開方案為 US$20 / US$100 / US$200 monthly tiers 加 Enterprise，提供 direct monetization evidence，但不是 Community Edition 本身的 license proof。
- Production / license boundary：repository README 明確區分第三方 harness CLI 的授權。Codex 為 Apache-2.0；Claude Code 受 Anthropic terms 約束；Hermes 的 upstream licensing 需另行確認。Apache-2.0 **不可外推**到這些外部 agent CLIs、model provider terms、production kits 或 user trajectories。Self-host deployment 仍需處理 auth、network exposure、provider secrets 與 sandbox boundary。
- Asset boundary：本次沒有把任何 model weights、dataset 或 trajectory corpus 列為 PASS；只驗證 HarnessRouter repository code。

**Blume**
- Primary repo: https://github.com/haydenbleasel/blume
- Immutable verification commit: `5d0c14e638a333c9f8bcf6184726493d78858cc3`
- Primary code license: https://github.com/haydenbleasel/blume/blob/5d0c14e638a333c9f8bcf6184726493d78858cc3/LICENSE
- License gate: `PASS / MIT`.
- 技術價值：Markdown-first docs framework，內建 raw Markdown、`llms.txt`、read-only MCP docs tools、AI skills、OpenAPI / AsyncAPI、search、versioning、validation/audit、translation checks 與 `blume eval` agent-facing docs evaluation。適合作為 agent-readable documentation、MCP documentation surface 與 docs-eval reference implementation。
- Business boundary：Blume 官方定位 free/open source、sponsor-supported；Business score 反映 implementation leverage 與 developer adoption potential，而不是 subscription WTP。
- Production gap：machine-readable docs 與 agent eval 不代表 docs 一定和 code/API behavior 同步；launch discussion 也直接暴露 staleness/drift 仍是上層 CI 問題。因此它強化 `Agent-Readable Docs Drift Monitor` 的需求，而不是取代 drift verification layer。
- Asset boundary：本次沒有發現可獨立再利用的 model weights、training dataset 或 trajectory corpus；只將 MIT repository code 列為 PASS。

### 2026-08-16 新增驗證

**@inferock/measure**
- Primary repo: https://github.com/inferock/inferock-bench
- Immutable verification commit: `e170a84e8aa55e062b646452474d45e3fcb45f9f`
- Component path: https://github.com/inferock/inferock-bench/tree/e170a84e8aa55e062b646452474d45e3fcb45f9f/packages/measure
- Primary code license: https://github.com/inferock/inferock-bench/blob/e170a84e8aa55e062b646452474d45e3fcb45f9f/packages/measure/LICENSE
- License gate: `PASS / Apache-2.0` **for the `packages/measure` component only**.
- 技術價值：提供 canonical provider event types、OpenAI / Anthropic / Gemini / OpenRouter usage normalization、broken-output / billed-empty / refusal / latency / token-count / billing-integrity detectors、pricing helpers，以及 receipt-ready spent/loss/recovery/exposure fields。適合 LLM FinOps、billing reconciliation、provider-independent receipts 與 regression measurement。
- Evidence boundary：repository root 明確是 multi-license。完整 `apps/inferock-bench` CLI 使用 `FSL-1.1-ALv2`（之後轉 Apache-2.0），`spec` 使用 CC-BY-4.0；因此不能把 `@inferock/measure` 的 Apache-2.0 自動外推到完整產品。Full CLI 目前只列 `CONDITIONAL`，不進正式排行。
- Production caution：Anthropic output-token recount 仍依 provider-assisted `count_tokens` + pinned local estimator calibration；upstream 自己把該 evidence 限制在 grade B。Maker 在 2026-08-15 Product Hunt launch 也明確表示尚無可公開的 provider-credit recovery 成功案例，因此 Business / Production 分數不因 launch headline 高估。
- Asset boundary：本次沒有驗證任何 reusable model weights、training dataset 或 trajectory corpus；只將 Apache-2.0 measurement library 列為 PASS。

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

- `inferock-bench` CLI: `CONDITIONAL`。Repository root 明確標示 `apps/inferock-bench` 為 `FSL-1.1-ALv2`、之後轉 Apache-2.0；目前不是本 policy 下的即時 permissive PASS。只有 `packages/measure` 被獨立驗證為 Apache-2.0 並正式入榜。
- `Spine-AI/medley`: `CONDITIONAL`。Repository plugin shim 是 MIT，但 LICENSE 明確指出 Medley engine 是 proprietary/closed source，且產品本身不是 open source，因此不能視為完整可替代產品的 OSS implementation asset。

## English

Only `PASS` entries receive a formal rank. Code, model weights, datasets, and trajectories require separate license verification. A permissive code license never proves that bundled data or model assets are commercially reusable.

Evaluation dimensions: Hackathon MVP speed, Business monetization leverage, Research/reproducibility value, Production maturity, and compatibility with common production AI stacks.

### New verified assets — 2026-08-17

**HarnessRouter Community Edition** enters at rank 15 with an internal 8.6 average. Repository code was verified at commit `902c2c2146fb4e4ce5f2c666836a0c203ed706a1` under Apache-2.0. UHP provides a versioned agent-harness contract, OpenAPI 3.1, JSON Schema 2020-12 and 52 runnable conformance checks, while Community Edition packages Gateway, Runner and Console in a self-hosted container. The license decision covers repository code only. Claude Code, Hermes, provider/model terms, production kits and generated trajectories require separate rights review. Protocol conformance also does not prove task-level behavioral parity.

**Blume** enters at rank 18 with an internal 8.4 average. Repository code was verified at commit `5d0c14e638a333c9f8bcf6184726493d78858cc3` under MIT. It is a strong implementation reference for Markdown-first agent-readable documentation with raw Markdown, `llms.txt`, read-only MCP tools, AI skills, OpenAPI/AsyncAPI and agent-facing docs evals. Its business score is lower because the project is free/open source rather than a paid SaaS. The key unresolved production problem is docs drift: machine-readable delivery does not prove that documentation still matches live code/API behavior.

### New verified asset — 2026-08-16

**@inferock/measure** is now rank 19 after newer entries, retaining an internal 8.2 average. The component was verified at commit `e170a84e8aa55e062b646452474d45e3fcb45f9f` under Apache-2.0. It provides canonical provider-event types, token/cost checks, billing-integrity detectors, pricing helpers and receipt-ready loss/recovery fields useful for AI FinOps and provider-independent billing reconciliation.

The license decision is intentionally component-scoped. The repository root is multi-license: `apps/inferock-bench` uses FSL-1.1-ALv2 and the `spec` directory uses CC-BY-4.0, so the full CLI is `CONDITIONAL`, not a formal PASS asset. No model, dataset or trajectory rights are inferred. Production and business scores remain conservative because the project documents provider-assisted evidence limits for some token checks and the maker stated during the August 15 Product Hunt launch that there is not yet a provider-credit recovery case to cite.

### New verified assets — 2026-08-15

**BrowserAct Skills** remains rank 13 with an internal 8.6 average. Repository code was verified at commit `8f287271faa0c1df79a44578cb059102ff004da2` under MIT. It is a high-leverage browser automation and agent-Skill reference with local browser reuse, session isolation, human handoff, compact agent-oriented state, and broad coding-agent compatibility. The MIT decision covers repository code only; BrowserAct Cloud, managed proxy/browser services, third-party site terms, and collected-data rights remain separate.

**DeepSeek Harness** remains rank 14 with an internal 8.6 average. Repository code was verified at commit `47f943859bef60e4160492346772ded9b24f765a` under MIT. Its Cordis architecture makes the model adapter, tool registry, session log, agent loop, policy/sandbox layer, and UI replaceable plugins. The durable session event log and model-visible logging invariant make it a strong harness, replay, audit, and compatibility research asset. Production maturity is deliberately scored lower because upstream labels the project a developer preview and warns of compatibility-breaking changes. No model-weight, dataset, plugin, or trajectory license is inferred from the runtime code license.

### New verified asset — 2026-08-14

**Aureka OpenDDE** is now rank 22 after newer entries, while retaining an internal 7.6 average. Repository code was verified at commit `d42760d264637a4518c0ab56d021451b9888d1f9` under Apache-2.0. Aureka's release statement and the Hugging Face model repository also identify the released OpenDDE checkpoints as Apache-2.0. This decision does not extend to training datasets, external search databases, or third-party biological data. OpenDDE is a strong research and reproduction asset for all-atom co-folding and drug-discovery workflows, but its production score is intentionally low because upstream labels it a preview release and explicitly says it is not yet intended for production pipelines.

### Previous verified assets

**NVIDIA-NeMo/Switchyard** is now rank 17 at 8.4. Its repository code remains Apache-2.0 and useful for protocol translation and model routing, but upstream still labels it pre-alpha and not for production.

**Paritok gateway + Paritok-4B-v1** remains rank 11 at 8.6. Repository code/gateway and the adapter are Apache-2.0; the training trajectories remain excluded as a reusable data asset until a separate license is verified.

**Prime Agent** remains rank 12 at 8.6 under MIT. It is useful for persistent and self-improving agent patterns but requires mutation governance and rollback.

**AgentConnect** is now rank 16 at 8.4 under Apache-2.0 and remains a strong reference for heterogeneous multi-agent collaboration and permission-aware control planes.

**MemoryCustodian** is now rank 20 and remains attractive for repository-native project memory and cross-agent interoperability but has lower production evidence.

**Soup CLI** is now rank 21 and remains useful for local post-training, with layer streaming explicitly treated as BETA rather than production-proven.

`Spine-AI/medley` remains conditional because only its plugin shim is MIT while the engine is proprietary.