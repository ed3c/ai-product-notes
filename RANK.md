# RANK.md — Commercially Usable Open Asset Ranking / 可商用開放資產排行

Scoring is an internal 1–10 decision score, not a claim by upstream projects.

## 繁體中文

### License gate

- `PASS`: primary license 明確允許 commercial use，且不強制採用者的產品開源。
- `CONDITIONAL`: 部分 scope 可用，但其他目錄、assets、models 或 engine 有不同條款。
- `REJECT`: commercial use 或必要元件不符合目前政策。
- `UNKNOWN`: 尚未完成 primary-license 驗證。

只對 `PASS` 進正式排行。Code、model weights、dataset、trajectory 必須分別驗證授權；permissive code license 不可外推到 bundled data、model weights、third-party services 或 generated trajectories。

### Verified ranking — 2026-08-20

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
| 12 | Paritok gateway + Paritok-4B-v1 | coding-agent context compression | PASS / Apache-2.0 code + adapter; Qwen base Apache-2.0 | 10 | 9 | 9 | 6 | 9 | 8.6 |
| 13 | Prime Agent | self-improving coding/research agent | PASS / MIT | 9 | 8 | 10 | 7 | 9 | 8.6 |
| 14 | BrowserAct Skills | browser automation / agent Skill runtime | PASS / MIT code; managed cloud/proxy scope separate | 10 | 8 | 7 | 8 | 10 | 8.6 |
| 15 | DeepSeek Harness | composable agent harness / plugin runtime | PASS / MIT code | 9 | 8 | 10 | 6 | 10 | 8.6 |
| 16 | HarnessRouter Community Edition | unified agent-harness runtime / protocol | PASS / Apache-2.0 repository code | 9 | 9 | 8 | 7 | 10 | 8.6 |
| 17 | AgentConnect | multi-agent collaboration/control plane | PASS / Apache-2.0 | 9 | 8 | 8 | 7 | 10 | 8.4 |
| 18 | NVIDIA-NeMo/Switchyard | LLM protocol translation & routing proxy | PASS / Apache-2.0 code | 9 | 9 | 9 | 5 | 10 | 8.4 |
| 19 | Blume | AI-ready Markdown documentation framework | PASS / MIT | 10 | 7 | 8 | 8 | 9 | 8.4 |
| 20 | Balsa UI | agent-readable Vue/React UI component source | PASS / MIT repository code | 10 | 7 | 8 | 8 | 9 | 8.4 |
| 21 | @inferock/measure | LLM billing-integrity measurement library | PASS / Apache-2.0 component code | 9 | 8 | 9 | 7 | 8 | 8.2 |
| 22 | MemoryCustodian | repo-native agent memory | PASS / MIT | 9 | 7 | 8 | 6 | 9 | 7.8 |
| 23 | Soup CLI | local LLM fine-tuning/post-training CLI | PASS / Apache-2.0 | 8 | 6 | 9 | 7 | 9 | 7.8 |
| 24 | Aureka OpenDDE | biomolecular foundation model / drug-discovery engine | PASS / Apache-2.0 code + released checkpoints; datasets/search DB scope separate | 7 | 8 | 10 | 5 | 8 | 7.6 |

### 2026-08-20 新增驗證

**Balsa UI**
- Primary repo: https://github.com/pedrobalsa/balsa-ui
- Immutable verification commit: `20115e0bb47c9ec1e7c65c0ef81a5896d520c9c7`
- Primary code license: https://github.com/pedrobalsa/balsa-ui/blob/20115e0bb47c9ec1e7c65c0ef81a5896d520c9c7/LICENSE
- License gate: `PASS / MIT` **for repository code**.
- Freshness evidence: pinned commit was committed on 2026-08-19 and carries the `Release 0.8.1` message.
- 技術價值：Balsa UI 將 Vue 3 / React 19 components 以 editable source 安裝，而不是 opaque package-only dependency。其 machine-readable specs 由同一 source compiler 衍生，並提供 intent search、MCP tool exposure、hosted `llms.txt`、catalog index/specs、read-only diff 與 local-edit-preserving update flow。這使 UI component library 同時可被 human developer 與 coding agents 理解，適合 agentic frontend generation、design-system conformance 與 component provenance 實驗。
- Business boundary：上游目前主要價值是 open-source component infrastructure；本排行的 Business 7 是 implementation leverage 評分，不代表 upstream 已有等價 SaaS revenue。
- Production boundary：component generation / update 仍需在實際 application stack 驗證 accessibility、browser behavior、security、framework upgrades、local modifications 與 design-system constraints。MIT 不可外推到 app-specific assets、third-party icons/fonts、external models、customer data 或 generated trajectories。
- `assets.code`: PASS — repository code at pinned commit.
- `assets.llm_models`: not_found — no bundled model weights are inferred.
- `assets.data`: not_found — component catalog metadata is project source, not treated as a separately licensed reusable production dataset.
- `assets.trajectories`: not_found — no reusable licensed agent-trajectory corpus verified.

### 2026-08-18 新增驗證

**Vendo**
- Primary repo: https://github.com/runvendo/vendo
- Immutable verification commit: `5cb079e62730d4b4fa133176f2a18c9fa34399c8`
- Primary code license: https://github.com/runvendo/vendo/blob/5cb079e62730d4b4fa133176f2a18c9fa34399c8/LICENSE
- License gate: `PASS / Apache-2.0` **for repository code**.
- 技術價值：B2B SaaS embedded customization layer。Agent 以 signed-in user 身分透過 host API 執行，讓終端使用者生成 views、micro-apps 與 automations，而不修改 host source。Generated UI 放在 sandboxed iframe，README 明確描述 `connect-src 'none'`；policy、approvals、grants、breakers 與 audit 集中在 guarded execution choke point。Repository 同時提供 store、harnesses、actions、guard、apps、automations、UI、MCP 與 telemetry packages，適合作為 embedded-agent、customer-generated UI、guarded tool execution 與 MCP exposure 的 production reference。
- Business evidence：open-source self-hosted layer之外，官方公開 Pro US$49/month、Teams US$499/month 等 paid packaging，提供直接 monetization evidence；這些 cloud/commercial plan terms 不是 Apache-2.0 license evidence。
- Production boundary：generated customer features 仍受 host API/schema、permission drift、customer data、third-party API terms、model-provider terms 與 deployment hardening 影響；Apache-2.0 不可外推到 cloud-gated sharing/publishing/org features、external models、customer/generated data 或 trajectories。
- `assets.code`: PASS — repository code at pinned commit.
- `assets.llm_models`: not_found — Vendo runtime accepts external models; no bundled model-weight license is inferred.
- `assets.data`: not_found — no independently reusable permissively licensed production/customer dataset verified.
- `assets.trajectories`: not_found — generated runs/audit records are not treated as a reusable licensed trajectory corpus.

### Previously verified assets — current boundaries

**HarnessRouter Community Edition** — commit `902c2c2146fb4e4ce5f2c666836a0c203ed706a1`, Apache-2.0 repository code. UHP provides versioned HTTP contract, OpenAPI 3.1, JSON Schema 2020-12 and 52 runnable conformance checks. Third-party harness CLIs, provider/model terms, production kits and generated trajectories require separate review. Protocol conformance does not prove task-level behavioral parity.

**Blume** — commit `5d0c14e638a333c9f8bcf6184726493d78858cc3`, MIT. Markdown-first agent-readable docs with raw Markdown, `llms.txt`, read-only MCP tools, AI skills, OpenAPI/AsyncAPI and docs eval. Machine-readable docs do not prove that documentation remains aligned with live API behavior; docs drift remains an upper-layer CI problem.

**@inferock/measure** — commit `e170a84e8aa55e062b646452474d45e3fcb45f9f`, Apache-2.0 **for `packages/measure` only**. Canonical provider events, token/cost checks, billing-integrity detectors and receipt-ready fields. Repository root is multi-license; the full `inferock-bench` CLI is `CONDITIONAL`, not formal PASS.

**BrowserAct Skills** — commit `8f287271faa0c1df79a44578cb059102ff004da2`, MIT repository code. Managed cloud/proxy services, website terms and collected-data rights are separate.

**DeepSeek Harness** — commit `47f943859bef60e4160492346772ded9b24f765a`, MIT repository code. Composable Cordis runtime, durable `SessionEvent` log and model-visible logging invariant; upstream developer-preview/breaking-change status keeps Production score conservative. Model weights, datasets, external plugins and trajectories remain separate.

**Aureka OpenDDE** — commit `d42760d264637a4518c0ab56d021451b9888d1f9`, Apache-2.0 code and released checkpoints according to upstream release/model repository. Training datasets, external biological databases and third-party data are excluded. Upstream labels the release preview/not yet intended for production pipelines.

**NVIDIA-NeMo/Switchyard** — commit `58f355a132d6fdd95191501aaa8522e100e06834`, Apache-2.0 code. Useful for OpenAI/Anthropic protocol translation and routing; upstream remains pre-alpha/experimental/not for production.

**Paritok gateway + Paritok-4B-v1** — Apache-2.0 code/adapter; Qwen base model card states Apache-2.0. Training trajectories remain excluded until separate data-license verification.

**Prime Agent** — MIT code. Persistent/self-improving agent patterns are valuable, but worker/kernel isolation is not a security sandbox; mutation governance and rollback are required. External models/datasets/skills/extensions remain separate.

**AgentConnect** — Apache-2.0 code. Strong reference for heterogeneous multi-agent collaboration and permission-aware control plane; credential/public-ingress/runtime hardening require separate production evidence.

**Soup CLI** — Apache-2.0. Useful for SFT/DPO/GRPO/KTO and local post-training; layer streaming remains BETA and old RTX 3050 throughput evidence is not treated as a current benchmark.

**MemoryCustodian** — MIT. Useful for repository-native Markdown memory, manifest routing and cross-agent adapters; production maturity remains below mature infrastructure projects.

### Conditional / excluded from formal rank

- `inferock-bench` full CLI: `CONDITIONAL`; root multi-license includes FSL-1.1-ALv2 for the CLI and CC-BY-4.0 for spec material. Only `packages/measure` is formally ranked as Apache-2.0.
- `Spine-AI/medley`: `CONDITIONAL`; plugin shim is MIT but the Medley engine is proprietary/closed source.

## English

Only `PASS` entries receive a formal rank. Code, model weights, datasets and trajectories require separate license verification. A permissive code license never proves that bundled data, cloud services, external models or generated trajectories are commercially reusable.

Evaluation dimensions: Hackathon MVP speed, Business monetization leverage, Research/reproducibility value, Production maturity, and compatibility with common production AI stacks.

### New verified asset — 2026-08-20

**Balsa UI** enters at rank 20 with an internal 8.4 average. Repository code was verified at commit `20115e0bb47c9ec1e7c65c0ef81a5896d520c9c7` under MIT. Balsa exposes editable Vue 3 and React 19 component source plus machine-readable specs derived from the same source compiler, intent search, MCP tools, hosted `llms.txt`, catalog metadata, read-only diffing, and updates designed to preserve local edits. This makes it a useful substrate for agentic frontend generation and design-system conformance.

The PASS decision covers repository code only. No model-weight, customer-data, third-party asset, or agent-trajectory rights are inferred. Production use still requires application-level accessibility, browser, security, framework-upgrade, and local-modification validation.

### New verified asset — 2026-08-18

**Vendo** enters at rank 11 with an internal 8.8 average. Repository code was verified at commit `5cb079e62730d4b4fa133176f2a18c9fa34399c8` under Apache-2.0. Vendo is an embedded customization layer for B2B SaaS: an agent acts through the host API as the signed-in user and generates customer-owned views, micro-apps and automations without modifying host source. Its architecture includes a sandboxed generated-UI surface plus centralized policy, approvals, grants, breakers and audit at a guarded execution choke point. The repository also exposes composable store, harness, actions, guard, apps, automation, UI and MCP packages.

Business evidence includes paid Pro and Teams packaging, but those hosted/commercial terms are separate from the Apache-2.0 code license. The PASS decision covers repository code only. External model terms, customer/generated data, third-party APIs, hosted features and generated trajectories require separate rights and production review. The main production gap is compatibility: customer-generated features can silently break when host APIs, schemas or permissions change even if the host application's own tests remain green.

### Current boundary reminders

HarnessRouter remains a protocol/interoperability reference; protocol conformance does not prove task-level parity. Blume remains a strong agent-readable docs substrate, while docs drift remains unsolved above it. `@inferock/measure` remains component-scoped Apache-2.0; the full CLI is conditional. BrowserAct, DeepSeek Harness, Switchyard, Prime Agent, AgentConnect, Soup, OpenDDE and other entries retain their previously verified code/model/data boundaries described above.
