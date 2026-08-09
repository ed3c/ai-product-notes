# Data Model / 資料模型

## 繁體中文

兩個 canonical dataset：

1. `Top 100 Best AI Products`
2. `Top 100 Solopreneur Products`

核心欄位沿用舊主資料庫的 1–10 分尺度，並將舊 `Google Doc Note URL` 改為 `Repository Note URL`，另新增 `Repository Note Path`。

追蹤欄位：`Official URL`、`Canonical Unique Key`、`First Added At`、`Last Updated At`、`Note Status`、`Repository Note URL`、`Repository Note Path`。

去重主鍵：`normalized_name|canonical_official_url`。若 URL 或命名變更，再以公司名稱、發布日期與產品描述做人類可審核的 secondary match。

每日流程必須先讀現有資料，再新增/更新；不得整份以新推測資料覆蓋。Top 100 超額時，只在完成全榜重算與排序後裁切。Historical timestamps 不得因 schema/storage migration 被刷新。

目前 dataset 以 20 筆一個 shard 儲存，`data/products/index.json` 是 shard manifest。這樣可在 GitHub 原生增量更新時避免整個大型 JSON 被不必要覆寫。

## English

Canonical datasets are `Top 100 Best AI Products` and `Top 100 Solopreneur Products`. The legacy 1–10 score scale is preserved. `Google Doc Note URL` is replaced by `Repository Note URL`, with `Repository Note Path` added.

Primary dedupe key: `normalized_name|canonical_official_url`. Use company/date/description only as a secondary human-reviewable match. Read-before-write is mandatory; prune to 100 only after recomputation. Storage/schema migration must not refresh historical timestamps.

Datasets are stored in 20-record shards referenced by `data/products/index.json`, allowing safe repository-native incremental updates without replacing one oversized JSON file.
