# CONTEXT.md — Technical Trigger Map / 技術觸發映射

## 繁體中文

此檔把產品研究語言轉成可落地的 implementation questions 與 production stack。看到觸發詞時，必須追查可重現證據、資料流、權限邊界、成本、失敗模式、observability 與 license。

| Trigger / 技術詞 | 必問問題 | 等價實作堆疊 |
|---|---|---|
| AI agent / autonomous workflow | state、tool permissions、retry、human approval、rollback？ | LangGraph/Temporal-style durable execution、tool gateway、policy layer |
| MCP / connector / tool gateway | schema、auth、capability discovery、sandbox、audit？ | MCP-compatible server/client、OAuth/OIDC、OPA、structured tool schemas |
| RAG / citations | source lineage、retrieval recall、citation fidelity、prompt injection？ | hybrid retrieval、reranker、provenance store、eval harness |
| agent memory / project memory | durable vs session state、forgetting、routing、human review？ | repo Markdown / structured store、manifest routing、bounded context pack |
| eval / benchmark / regression | golden tasks、environment reset、judge calibration、CI gate？ | Promptfoo-style evals、deterministic fixtures、sandbox、trace store |
| trajectory / trace / rollout / JSONL | event schema、PII、replayability、retention、training rights？ | OpenTelemetry-style traces、structured JSONL、redaction、replay harness |
| model gateway / routing | fallback、quality-cost tradeoff、regional policy？ | OpenAI-compatible proxy、LiteLLM-style routing、policy/eval layer |
| open-weight / self-hosted inference | license、VRAM、quantization、throughput、SLA？ | vLLM/SGLang-class serving、GPU scheduler、cache、telemetry |
| LoRA / QLoRA / adapters | base-model rights、dataset provenance、merge/serve path？ | PEFT-style adapters、quantized training、eval-before-merge |
| synthetic data | contamination、privacy、judge bias、provenance？ | generator → verifier → dedupe → quality gate → lineage |
| agent security / governance | identity、least privilege、approval、audit evidence？ | OAuth/OIDC、OPA-style policy、secret broker、action ledger |
| sandbox / computer use | filesystem/network boundary、reset、escape test？ | container/VM/browser sandbox、seccomp/eBPF-class controls、replay |
| voice agent / WebRTC | latency、barge-in、consent、tool correctness、QA？ | WebRTC、STT/TTS、turn detector、conversation eval、recording policy |
| 3D / XR | geometry QA、poly budget、format、dimensions、viewer？ | GLB/USDZ pipeline、Blender/mesh tooling、WebGL/Three.js |
| robotics / embodied AI | telemetry、safety boundary、fleet state、sim-to-real evidence？ | ROS2-class middleware、telemetry、simulator、policy gate、fleet ops |

### Mapping contract

```yaml
product:
implementation_capabilities: []
assets:
  code: []
  llm_models: []
  data: []
  trajectories: []
license_evidence: []
production_gaps: []
not_found: []
```

`not_found` 必須說明搜尋過但沒有足夠證據，不可靜默略過。

## English

This file maps product-language triggers to implementation questions and production stacks. Every mapping must investigate reproducibility, data flow, permission boundaries, cost, failure modes, observability, and licensing—not just feature similarity.

For every product, return explicit `code`, `llm_models`, `data`, and `trajectories` candidates with primary-license evidence. If evidence is insufficient, record it under `not_found` with the reason.
