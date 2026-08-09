# Daily Monitor Contract / 每日監控契約

## 繁體中文

每天執行一次 AI 產品與融資監控，最近 24 小時為硬性 freshness window。優先讀 Product Hunt、There's An AI For That、其他 launch platforms、公司官方來源與可靠融資媒體。發布日期無法確認、來源互相衝突、已被前一日收錄或只是舊產品被搜尋引擎重新索引者，一律不納入。

執行順序：

1. 先讀 `README.md`、`docs/CONFIG.md`、`CONTEXT.md`、`RANK.md`、`data/products/index.json` 與兩份 current datasets。
2. 搜尋候選，記錄 event date、source date、official URL 與 evidence quality。
3. 僅保留最多 5–10 個最高品質候選；不足則回報實際數量，包含 0。
4. 分析客群、痛點、business model、pricing/WTP、technical/operational barrier、margin、competition、gap、distribution、Solopreneur feasibility 與 MVP。
5. 只對真正新項目新增資料；真正變更才更新 `Last Updated At`。
6. 依 `docs/CONFIG.md` 公式重算排名；每榜最多 100。
7. 深度筆記寫到 `notes/<category>/<slug>/<YYYY-MM-DD>.md`，繁體中文與 English 同檔。
8. 每日簡報寫到 `daily/YYYY-MM-DD.md`。
9. 若 `gemini-deep-research/inbox/` 有新 Markdown，保留 citations，產生 normalized report 與 product → `code | llm_models | data | trajectories` mapping。
10. 每個 OSS/open-weight 候選必須驗證 primary license；commercial use 不清楚時不得標記可商用。
11. 更新 `RANK.md`，維度為 Hackathon MVP、Business、Research、Production Use、Stack Compatibility。
12. 所有例行變更直接寫 `main`，不建立 note branch；絕不提交 secret/API key/private customer data。
13. 不再建立或更新 Google Sheet、Google Doc 或 Excel。

## English

Run a daily trailing-24-hour AI product and funding monitor. Freshness is a hard gate. Prefer primary launch pages, company announcements, and reputable funding sources. Exclude unverifiable dates, conflicting launch histories, duplicates from the previous run, and stale pages re-indexed as fresh.

Read repository state first, qualify candidates, update only changed records, recompute rankings using `docs/CONFIG.md`, write bilingual notes, save the daily brief, process Gemini Deep Research inputs, verify primary licenses before commercial-use mapping, and update `RANK.md`. Routine writes go directly to `main`. Never write new canonical data to Google Sheets, Google Docs, or Excel.
