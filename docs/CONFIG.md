# Configuration / 固定參數

## 繁體中文

- Canonical repository: `ed3c/ai-product-notes`
- Canonical branch: `main`
- Timezone: `Asia/Taipei`
- Monitor window: 最近 24 小時
- Daily qualified items: 最多 5–10；品質不足不得補舊聞，允許 0 筆
- Top lists: 每類最多 100 筆
- Storage: GitHub Markdown + JSON only
- Google Sheet / Google Doc / Excel writes: **disabled**
- Update strategy: incremental only
- Product identity: normalized product/concept name + canonical official URL
- Preserve `First Added At`; only true evidence/content changes modify `Last Updated At`
- Deep note condition: daily Top 3、證據太長、或需要獨立決策文件
- Note language: Traditional Chinese + English
- Git policy: routine automation writes directly to `main`; no note branches
- Secret policy: never commit API keys, credentials, private tokens, private customer data, or raw sensitive trajectories

### Composite Score

`Top 100 Best AI Products`

`0.35 * WTP + 0.25 * Funding Scale + 0.20 * User Traction + 0.20 * Market Gap Moat`

`Top 100 Solopreneur Products`

`0.35 * Tech Simplicity + 0.25 * Profit Margin + 0.25 * Gap Size + 0.15 * Distribution Ease`

### Ranking tie-break

1. Composite Score descending
2. Stronger market validation
3. Newer `Last Updated At` only when the item actually changed
4. Stable prior order if evidence does not justify reordering

## English

- Canonical repository: `ed3c/ai-product-notes`
- Canonical branch: `main`
- Timezone: `Asia/Taipei`
- Monitoring window: trailing 24 hours
- Daily qualified items: up to 5–10; never backfill stale/low-quality items; zero is valid
- Maximum active records per category: 100
- Storage: repository-native Markdown + JSON
- Google Sheet / Google Doc / Excel writes: **disabled**
- Update strategy: incremental
- Identity: normalized product/concept name + canonical official URL
- Preserve `First Added At`; update `Last Updated At` only for real changes
- Deep notes: Top-3 items, evidence-heavy cases, or decision-grade research
- Notes: Traditional Chinese + English
- Routine Git writes: directly to `main`, no note branches
- Never commit secrets, credentials, private tokens, customer-private data, or sensitive raw trajectories.

Score formulas and tie-break rules are identical to the Traditional Chinese section above.
