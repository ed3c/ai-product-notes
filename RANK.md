# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品全面開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models、data 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只有 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證；permissive code license 不可外推到 bundled data、external models、cloud services、third-party APIs 或 generated trajectories。

### Verified ranking — 2026-08-22

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
| 11 | Vendo | embedded agent / customer-generated app runtime | PASS / Apache-2.0 repository code | 9 | 9 | 8 | 8 | 10 | 8.8 |
| 12 | OneCLI core | agent credential gateway / policy control plane | PASS core / Apache-2.0; `ee/` enterprise scope separate | 9 | 9 | 8 | 8 | 10 | 8.8 |
| 13 | Paritok gateway + Paritok-4B-v1 | coding-agent context compression | PASS / Apache-2.0 code + adapter; Qwen base Apache-2.0 | 10 | 9 | 9 | 6 | 9 | 8.6 |
| 14 | Prime Agent | self-improving coding/research agent | PASS / MIT | 9 | 8 | 10 | 7 | 9 | 8.6 |
| 15 | BrowserAct Skills | browser automation / agent Skill runtime | PASS / MIT code; managed cloud/proxy scope separate | 10 | 8 | 7 | 8 | 10 | 8.6 |
| 16 | DeepSeek Harness | composable agent harness / plugin runtime | PASS / MIT code | 9 | 8 | 10 | 6 | 10 | 8.6 |
| 17 | HarnessRouter Community Edition | unified agent-harness runtime / protocol | PASS / Apache-2.0 repository code | 9 | 9 | 8 | 7 | 10 | 8.6 |
| 18 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 19 | NVIDIA-NeMo/Switchyard | LLM protocol translation & routing proxy | PASS / Apache-2.0 code | 9 | 9 | 9 | 5 | 10 | 8.4 |
| 20 | Blume | AI-ready Markdown documentation framework | PASS / MIT | 10 | 7 | 8 | 8 | 9 | 8.4 |
| 21 | Balsa UI | agent-readable Vue/React UI component source | PASS / MIT repository code | 10 | 7 | 8 | 8 | 9 | 8.4 |
| 22 | Vercel fx | tiny embeddable coding-agent harness / CLI | PASS / Apache-2.0 repository code | 10 | 7 | 9 | 6 | 10 | 8.4 |
| 23 | @inferock/measure | LLM billing-integrity measurement library | PASS / Apache-2.0 component code | 9 | 8 | 9 | 7 | 8 | 8.2 |
| 24 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 25 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |
| 26 | Aureka OpenDDE | biomolecular foundation model / drug-discovery engine | PASS / Apache-2.0 code + released checkpoints; datasets/search DB scope separate | 7 | 8 | 10 | 5 | 8 | 7.6 |

### 2026-08-22 新增驗證

**OneCLI core**
- Primary repo: https://github.com/onecli/onecli
- Immutable verification commit: `ff7a1921a95943d19066567b274c1d3c9c157c14`
- Primary code license: repository root `LICENSE`, Apache-2.0 at the pinned revision.
- License gate: `PASS core / Apache-2.0`; repository `ee/` enterprise paths are separately licensed and **not** included in this PASS decision.
- 技術價值：transparent credential injection、agent-scoped identity、host/path policy、rate limits、human approval、audit logs、encrypted secret storage，並能包住 Claude Code、Cursor、Codex、Hermes、OpenCode 等 agent process。Gateway 在 agent/LLM 外部執行 policy，是很好的 agent-secret egress、least-privilege、runtime governance reference。
- Business evidence：截至 2026-08-22 09:16 官方 pricing readback，頁面預設顯示 BYOC Team **US$149/month（5 users / 10 agents）**、Scale **US$499/month（10 users / 20 agents）**、Enterprise custom；FAQ 說明 hosted-model pricing 為 Team **US$499/month**、Scale **US$1,999/month**。Self-hosted deployment 目前只列為 Enterprise custom terms，沒有公開固定 US$1,499/month self-host 價格。這些 hosted/commercial terms 是 WTP evidence，不等於 Apache-2.0 license scope。
- Production boundary：TLS interception、credential rotation、IdP、OAuth scopes、third-party API terms、incident response 與 enterprise `ee/` features 都需要獨立 review。核心 code permissive license 不可外推到 hosted service、external models、customer secrets/data 或 trajectories。
- `assets.code`: PASS — core repository code excluding separately licensed `ee/` scope.
- `assets.llm_models`: not_found — external providers only; no bundled model-weight rights inferred.
- `assets.data`: not_found — no reusable independently licensed customer/production dataset verified.
- `assets.trajectories`: not_found — audit/run data is not treated as a reusable licensed trajectory corpus.

**Vercel fx**
- Primary repo: https://github.com/vercel-labs/fx
- Immutable verification commit: `df7e6245e1992758d4060c97477ceafa27770551`
- Freshness evidence: commit authored 2026-08-21T20:42:03Z; merge message prepares `v0.0.5`.
- Primary code license: Apache-2.0 at the pinned revision.
- License gate: `PASS / Apache-2.0` **for repository code**.
- 技術價值：Zig-based tiny native coding-agent harness / CLI，model-agnostic，支援 local/cloud inference；可透過 `fx acp`、`createFxAgent()` / WebAssembly SDK 嵌入其他 hosts，並提供 skills、MCP、subagents、sessions、permissions。v0.0.5 新增 Codex/Grok subscription authentication、provider switching、skills roots 與多項 permission/security hardening。
- Business boundary：fx 本身是 experimental open-source developer substrate，Business 7 表示 implementation leverage，不代表已有獨立 SaaS revenue。
- Production boundary：upstream README 明確標示 `Experimental. Use at your own risk.`；v0.0.5 亦包含 breaking changes。Production score 因此僅 6。
- `assets.code`: PASS — repository code at pinned commit.
- `assets.llm_models`: not_found — Codex/Grok/Gateway model terms are external.
- `assets.data`: not_found — no separately licensed reusable production dataset verified.
- `assets.trajectories`: not_found — saved sessions/traces are user runtime artifacts, not a licensed trajectory corpus.

### 2026-08-20 新增驗證

**Balsa UI**
- Primary repo: https://github.com/pedrobalsa/balsa-ui
- Immutable verification commit: `20115e0bb47c9ec1e7c65c0ef81a5896d520c9c7`
- License gate: `PASS / MIT` for repository code.
- 技術價值：editable Vue 3 / React 19 component source、同 source compiler 衍生的 machine-readable specs、intent search、MCP、`llms.txt`、catalog metadata、read-only diff，以及保留 local edits 的 update flow。
- Production boundary：app-level accessibility、browser behavior、security、framework upgrades、local modifications 與 third-party assets 仍需獨立驗證。

### 2026-08-18 新增驗證

**Vendo**
- Primary repo: https://github.com/runvendo/vendo
- Immutable verification commit: `5cb079e62730d4b4fa133176f2a18c9fa34399c8`
- License gate: `PASS / Apache-2.0` for repository code.
- 技術價值：B2B SaaS embedded customization layer；signed-in user 身分經 host API 執行，生成 views / micro-apps / automations；central policy/approval/grant/breaker/audit choke point，搭配 sandboxed generated UI。
- Business evidence：官方已有 Pro / Teams paid packaging；hosted terms 與 customer data 不屬於 Apache-2.0 scope。

### Previously verified assets — current boundaries

- **HarnessRouter Community Edition** — commit `902c2c2146fb4e4ce5f2c666836a0c203ed706a1`, Apache-2.0 repository code. UHP 提供 versioned HTTP contract、OpenAPI 3.1、JSON Schema 2020-12 與 runnable conformance checks；protocol conformance 不等於 task-level behavioral parity。
- **Blume** — commit `5d0c14e638a333c9f8bcf6184726493d78858cc3`, MIT. Agent-readable docs、MCP、`llms.txt`、OpenAPI/AsyncAPI 與 docs eval；machine-readable docs 不代表與 live behavior 永遠同步。
- **@inferock/measure** — commit `e170a84e8aa55e062b646452474d45e3fcb45f9f`, Apache-2.0 for `packages/measure` only. Repository root multi-license；full CLI 不列 formal PASS。
- **BrowserAct Skills** — commit `8f287271faa0c1df79a44578cb059102ff004da2`, MIT repository code. Managed cloud/proxy、website terms、collected-data rights separate.
- **DeepSeek Harness** — commit `47f943859bef60e4160492346772ded9b24f765a`, MIT repository code. Developer-preview / breaking-change 狀態使 Production score 保守；models/data/plugins/trajectories separate.
- **Aureka OpenDDE** — commit `d42760d264637a4518c0ab56d021451b9888d1f9`, Apache-2.0 code + released checkpoints；training datasets / external biological DB excluded，upstream 仍為 preview。
- **NVIDIA-NeMo/Switchyard** — commit `58f355a132d6fdd95191501aaa8522e100e06834`, Apache-2.0 code；pre-alpha / experimental / not-for-production。
- **Paritok gateway + Paritok-4B-v1** — Apache-2.0 code/adapter；Qwen base model card Apache-2.0；training trajectories excluded pending separate license evidence.
- **Prime Agent** — MIT code；persistent/self-improving patterns useful，但 worker/kernel isolation 不是 security sandbox；external models/data/skills separate.
- **AgentConnect** — Apache-2.0 code；heterogeneous multi-agent collaboration / permission control-plane reference；credential/public-ingress hardening separate.
- **Soup CLI** — Apache-2.0；SFT/DPO/GRPO/KTO/local post-training；layer streaming remains BETA.
- **MemoryCustodian** — MIT；repo-native Markdown memory / manifest routing / cross-agent adapters；production maturity lower than established infrastructure.

### Conditional / excluded from formal rank

- `inferock-bench` full CLI: `CONDITIONAL`; root multi-license includes FSL-1.1-ALv2 for CLI and CC-BY-4.0 for spec material. Only `packages/measure` is formally ranked as Apache-2.0.
- `Spine-AI/medley`: `CONDITIONAL`; plugin shim is MIT but Medley engine is proprietary/closed source.
- OneCLI `ee/`: separately licensed enterprise scope; excluded from the core Apache-2.0 PASS decision.

## English

Only `PASS` entries receive a formal rank. Code, model weights, datasets, and trajectories require separate license verification. A permissive code license never proves that bundled data, hosted services, external models, customer information, or generated trajectories are commercially reusable.

Evaluation dimensions: Hackathon MVP speed, Business monetization leverage, Research/reproducibility value, Production maturity, and compatibility with common production AI stacks.

### New verified assets — 2026-08-22

**OneCLI core** enters at rank 12 with an internal 8.8 average. Core repository code was verified at commit `ff7a1921a95943d19066567b274c1d3c9c157c14` under Apache-2.0. Separately licensed `ee/` enterprise paths are excluded. OneCLI is a strong reference for credential injection, external policy enforcement, agent-scoped identity, approvals, and audit across coding agents and autonomous workflows. The current pricing page defaults to BYOC at **US$149/month for Team (5 users / 10 agents)** and **US$499/month for Scale (10 users / 20 agents)**; its FAQ states hosted-model pricing of **US$499/month / US$1,999/month**. Self-hosting is currently Enterprise custom. Public pricing provides clear monetization evidence, but hosted service terms, external providers, customer secrets/data, and trajectories are separate from the code license.

**Vercel fx** enters at rank 22 with an internal 8.4 average. Repository code was verified at commit `df7e6245e1992758d4060c97477ceafa27770551` under Apache-2.0. The same commit prepares v0.0.5 and is dated 2026-08-21T20:42:03Z. fx is a small Zig-based, model-agnostic coding-agent harness that can run natively or through WebAssembly/ACP embedding and supports skills, MCP, subagents, sessions, and explicit permission controls. Production is scored conservatively because upstream explicitly labels the project experimental and v0.0.5 contains breaking changes.

The PASS decisions cover repository code only. No external model, service, dataset, credential, or agent-trajectory rights are inferred.
