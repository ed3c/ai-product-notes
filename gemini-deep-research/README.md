# Gemini Deep Research Workspace

## 繁體中文

此目錄只接 Gemini Deep Research 的 research artifacts，不直接覆蓋 canonical ranking。

資料流：

`inbox/ Markdown + citations` → `reports/ normalized research` → `citations/ claim ledger` → `mappings/ product-open-asset map` → primary license verification → `RANK.md`

強制規則：

- 保留 source title、URL、publication/event date、retrieved date。
- 每個 material claim 需要 claim-level citation。
- Product mapping 必須分成 `code`, `llm_models`, `data`, `trajectories`。
- license 未驗證不得標記 commercial-safe。
- citation conflict 必須保留，不得用單一摘要掩蓋。
- private customer traces 只記 schema/metadata，不提交 raw content。

## English

This directory receives Gemini Deep Research artifacts without granting them authority to overwrite the canonical ranking directly. Normalize research, preserve claim-level citations, split product mappings into code/models/data/trajectories, verify primary licenses, and only then promote candidates into `RANK.md`.
