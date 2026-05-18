# DAILY TRIGGER PROMPT
# Paste this ONCE into your Claude Project each morning.
# Claude will generate all 60 candidates and output them as JSON.
# Copy the JSON output into candidates/YYYY-MM-DD.json and feed to your pipeline.
#
# ── INSTRUCTIONS ──────────────────────────────────────────────────────────
# 1. Replace [FORBIDDEN PATTERNS] with the last 10-15 lines from your
#    candidates/fingerprints.json (or leave blank on day 1)
# 2. Replace [COVERAGE GAPS] if you know which archetypes are underrepresented
# 3. Paste and send — Claude handles everything else
# ──────────────────────────────────────────────────────────────────────────

---

ALPHA BATCH GENERATION — DAILY RUN

Date: [TODAY'S DATE]
Target: 60 expressions across 12 strategy archetypes (5 per archetype)

FORBIDDEN PATTERNS (do not replicate these structural approaches):
[PASTE YOUR EXISTING FINGERPRINT SUMMARY HERE — or leave blank]

COVERAGE GAPS (prioritize these archetypes):
[PASTE UNDERREPRESENTED ARCHETYPES HERE — or leave blank for auto-rotation]

---

Execute the following 12 batch generation tasks in sequence.
For each archetype:
1. Search for ONE recent academic paper or anomaly relevant to that archetype
2. Generate 5 structurally distinct Brain FastExpr expressions inspired by that research

ARCHETYPE 1: Price Momentum
- Search for a 2020-2025 paper on cross-sectional or time-series momentum
- Generate 5 expressions: vary time horizons (5d, 20d, 60d, 120d, hybrid)
- At least 1 must use vwap, 1 must use sector neutralization

ARCHETYPE 2: Mean Reversion
- Search for a paper on short-term reversal, microstructure, or bid-ask bounce
- Generate 5 expressions: vary from 1-day reversal to 10-day zscore reversion
- At least 1 must use volume as a confirmation signal

ARCHETYPE 3: Volume-Price Divergence
- Search for a paper on volume-price relationship or informed trading indicators
- Generate 5 expressions: combine volume with returns/close/vwap in different ways
- At least 1 must use ts_correlation

ARCHETYPE 4: Fundamental Value
- Search for a 2020-2025 paper on value factor revival or composite value signals
- Generate 5 expressions: use different valuation multiples (pe, pb, ps, ev_ebitda, composite)
- At least 2 must use group_rank or group_neutralize by sector

ARCHETYPE 5: Quality
- Search for a paper on quality factor construction (Novy-Marx, AQR, or recent)
- Generate 5 expressions: vary across profitability, stability, safety, growth dimensions
- At least 1 must combine 2 quality metrics (e.g., roe AND grossmargin)

ARCHETYPE 6: Earnings Momentum
- Search for a paper on post-earnings announcement drift or analyst revision effects
- Generate 5 expressions: use eps_revision, surprise, surprise_pct, earningsgrowth differently
- At least 1 must combine price momentum with earnings momentum

ARCHETYPE 7: Volatility
- Search for a paper on low-volatility anomaly or volatility forecasting
- Generate 5 expressions: mix realized vol, skewness, vol-of-vol, vol relative to sector
- At least 1 must use ts_skewness or ts_kurtosis

ARCHETYPE 8: Liquidity
- Search for a paper on liquidity premium or Amihud illiquidity measure
- Generate 5 expressions: use volume, amount, adv20, turnover_vol in different combinations
- At least 1 must create an illiquidity measure (price impact = |returns|/volume)

ARCHETYPE 9: Intraday Patterns
- Search for a paper on open-to-close returns, overnight vs intraday, or high-low spreads
- Generate 5 expressions: use open, high, low, vwap, close relationships
- At least 1 must use (close-open)/open and at least 1 must use (high-low)/vwap

ARCHETYPE 10: Leverage & Balance Sheet
- Search for a paper on leverage effect, financial distress, or asset growth anomaly
- Generate 5 expressions: use debt, equity, debttoeq, interestcoverage, assets
- At least 1 must use interestcoverage and at least 1 must measure leverage trend

ARCHETYPE 11: Earnings Quality
- Search for a paper on accruals anomaly, cash earnings quality, or earnings persistence
- Generate 5 expressions: measure gap between accounting earnings and cash earnings
- At least 1 must use fcf vs netincome divergence (classic Sloan accruals)

ARCHETYPE 12: Cross-Sectional Relative Strength
- Search for a paper on industry momentum, relative strength, or within-group signals
- Generate 5 expressions: all must use group_rank or group_neutralize
- Use different group levels (sector, industry, subindustry) and time horizons

---

OUTPUT FORMAT:
Respond with a single JSON object:
{
  "date": "[TODAY'S DATE]",
  "candidates": [
    {
      "id": "alpha_[DATE]_001",
      "archetype": "[archetype name]",
      "expression": "[valid Brain expression]",
      "rationale": "[one sentence]",
      "research_source": "[paper name or anomaly]"
    },
    ... (60 total)
  ]
}

IMPORTANT:
- Every expression must use ONLY the valid operators and fields in your system prompt
- No expression can share the same primary operator AND same primary fields as another in the same archetype
- All 60 expressions must be syntactically valid (balanced parentheses, no Python code)
- Number IDs sequentially: alpha_[DATE]_001 through alpha_[DATE]_060
