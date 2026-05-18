"""
WorldQuant Brain - Complete operator and data field reference.
Rebuilt from official Brain operator docs + fields CSV (5905 fields).
This module is the single source of truth for what is VALID in Brain expressions.
"""

# ─────────────────────────────────────────────
# OPERATORS — from official Brain documentation
# ─────────────────────────────────────────────

# Base / Math operators
MATH_OPERATORS = [
    "abs",              # absolute value
    "add",              # x + y (filter=false)
    "densify",          # compress grouping buckets
    "divide",           # x / y
    "inverse",          # 1/x
    "log",              # natural log
    "max",              # element-wise max of 2+ inputs
    "min",              # element-wise min of 2+ inputs
    "multiply",         # x * y (filter=false)
    "power",            # x^y
    "reverse",          # -x
    "sign",             # +1 / -1 / 0
    "signed_power",     # sign-preserving power
    "sqrt",             # non-negative square root
    "subtract",         # x - y (filter=false)
]

# Logical operators
LOGICAL_OPERATORS = [
    "and",              # both true
    "if_else",          # conditional: if_else(cond, true_val, false_val)
    "is_nan",           # 1 if NaN
    "not",              # logical negation
    "or",               # either true
    # Comparison: <, <=, ==, >, >=, != (infix, not function calls)
]

# Time-series operators (window-based, require integer argument)
TS_OPERATORS = [
    "days_from_last_change",  # days since value changed
    "hump",             # limit change magnitude (reduce turnover)
    "kth_element",      # k-th value looking back d days
    "last_diff_value",  # most recent different value in d days
    "ts_arg_max",       # days since max in window
    "ts_arg_min",       # days since min in window
    "ts_av_diff",       # x - ts_mean(x, d), NaN-safe
    "ts_backfill",      # forward-fill NaN with lookback
    "ts_corr",          # rolling Pearson correlation
    "ts_count_nans",    # count NaN in window
    "ts_covariance",    # rolling covariance
    "ts_decay_linear",  # weighted decay, recent values heavier
    "ts_delay",         # value from d days ago
    "ts_delta",         # x[t] - x[t-d]
    "ts_mean",          # rolling mean
    "ts_product",       # rolling product
    "ts_quantile",      # rank + inverse CDF transform
    "ts_rank",          # rank current value in window
    "ts_regression",    # regression params (rettype=0..8)
    "ts_scale",         # scale to 0-1 in window
    "ts_std_dev",       # rolling standard deviation
    "ts_step",          # incrementing day counter
    "ts_sum",           # rolling sum
    "ts_zscore",        # rolling z-score
]

# Cross-sectional operators (per-day, across universe)
CS_OPERATORS = [
    "normalize",        # subtract mean, optionally /std, clamp
    "quantile",         # rank + distribution transform
    "rank",             # cross-sectional percentile rank [0,1]
    "scale",            # scale so |sum| = book size
    "winsorize",        # clip at N std devs
    "zscore",           # cross-sectional z-score
]

# Vector operators
VECTOR_OPERATORS = [
    "vec_avg",          # mean of vector elements
    "vec_sum",          # sum of vector elements
]

# Transformational operators
TRANSFORM_OPERATORS = [
    "bucket",           # create custom groups from ranked data
    "trade_when",       # conditional trading: trade_when(cond, alpha, hold_value)
]

# Group operators
GROUP_OPERATORS = [
    "group_backfill",   # fill NaN within group using winsorized mean
    "group_mean",       # harmonic mean within group
    "group_neutralize", # subtract group mean
    "group_rank",       # rank within group [0,1]
    "group_scale",      # normalize within group to [0,1]
    "group_zscore",     # z-score within group
]

ALL_OPERATORS = (
    MATH_OPERATORS + LOGICAL_OPERATORS + TS_OPERATORS +
    CS_OPERATORS + VECTOR_OPERATORS + TRANSFORM_OPERATORS + GROUP_OPERATORS
)

# ─────────────────────────────────────────────
# DATA FIELDS — from Brain fields CSV (5905 total)
# Only listing high-coverage, high-alpha-count fields per dataset.
# The full CSV is the canonical source; these are the most useful.
# ─────────────────────────────────────────────

PRICE_VOLUME_FIELDS = {
    # Price Volume Data for Equity (24 fields, all coverage=1.0)
    "open":         "Daily open price",
    "high":         "Daily high price",
    "low":          "Daily low price",
    "close":        "Daily close price",
    "vwap":         "Volume-weighted average price",
    "returns":      "Daily returns (close-to-close)",
    "volume":       "Share volume traded",
    "sharesout":    "Shares outstanding",
    "cap":          "Market capitalization",
    "adv20":        "20-day average dollar volume",
    "dividend":     "Dividend amount",
    "split":        "Split factor",
    "exchange":     "Exchange listing",
}

GROUP_FIELDS = {
    "sector":       "GICS sector",
    "industry":     "GICS industry group",
    "subindustry":  "GICS sub-industry",
    "market":       "Market listing",
    "country":      "Country of listing",
}

FUNDAMENTAL_FIELDS = {
    # Company Fundamental Data for Equity (886 fields, top by alphaCount)
    "assets":           "Total assets",
    "liabilities":      "Total liabilities",
    "operating_income": "Operating income",
    "enterprise_value": "Enterprise value",
    "sales":            "Total sales/revenue",
    "debt":             "Total debt",
    "capex":            "Capital expenditure",
    "equity":           "Shareholders equity",
    "ebitda":           "EBITDA",
    "ebit":             "EBIT",
    "eps":              "Earnings per share",
    "debt_lt":          "Long-term debt",
    "cashflow_op":      "Operating cash flow",
    "assets_curr":      "Current assets",
    "goodwill":         "Goodwill",
    "income":           "Net income",
    "revenue":          "Revenue",
    "cash":             "Cash and equivalents",
    "liabilities_curr": "Current liabilities",
    "cogs":             "Cost of goods sold",
    "debt_st":          "Short-term debt",
    "bookvalue_ps":     "Book value per share",
    "cashflow":         "Total cash flow",
    "ppent":            "PP&E net",
    "operating_expense":"Operating expenses",
    "inventory":        "Inventory",
    "return_equity":    "Return on equity",
    "return_assets":    "Return on assets",
    "sales_growth":     "Sales growth",
    "receivable":       "Accounts receivable",
    "retained_earnings":"Retained earnings",
    "income_tax":       "Income tax",
    "pretax_income":    "Pretax income",
    "cashflow_fin":     "Financing cash flow",
    "cashflow_invst":   "Investing cash flow",
    "depre_amort":      "Depreciation & amortization",
    "rd_expense":       "R&D expense",
    "interest_expense": "Interest expense",
    # Key fnd6_ fields used in practice
    "fnd6_newa1v1300_epspi":  "Annual EPS estimate",
    "fnd6_cptnewqv1300_opepsq":"Quarterly operating EPS",
    "fnd6_newqv1300_ivltq":   "Quarterly inventory",
    "fnd6_acdo":              "Accumulated depreciation",
    "fnd6_fopo":              "Funds from operations",
    "fnd6_newa1v1300_gp":     "Annual gross profit estimate",
    "fnd6_newa2v1300_oibdp":  "EBITDA estimate",
}

ANALYST_FIELDS = {
    # Analyst Estimate Data for Equity (653 fields)
    "est_eps":              "Consensus EPS estimate",
    "est_capex":            "Consensus capex estimate",
    "est_rd_expense":       "Consensus R&D estimate",
    "est_epsr":             "Consensus EPS revised",
    "est_sales":            "Consensus sales estimate",
    "est_netprofit":        "Consensus net profit estimate",
    "est_ptp":              "Consensus pretax profit estimate",
    "est_cashflow_op":      "Consensus operating cash flow estimate",
    "est_ebit":             "Consensus EBIT estimate",
    "est_fcf":              "Consensus free cash flow estimate",
    "est_bookvalue_ps":     "Consensus book value/share estimate",
    "est_grossincome":      "Consensus gross income estimate",
    "est_tot_assets":       "Consensus total assets estimate",
    # anl4 analyst flags/values (high alpha count)
    "anl4_adjusted_netincome_ft": "Adjusted net income (analyst)",
    "anl4_ptp_flag":        "Pretax profit flag",
    "anl4_bvps_flag":       "Book value per share flag",
    "anl4_ebit_value":      "EBIT value (analyst estimate)",
    "anl4_ebitda_value":    "EBITDA value (analyst estimate)",
    "anl4_netdebt_flag":    "Net debt flag",
    "anl4_epsr_flag":       "EPS revision flag",
    "anl4_totassets_flag":  "Total assets flag",
}

NEWS_FIELDS = {
    # US News Data (322 fields) + Ravenpack (75 fields)
    "nws12_afterhsz_sl":   "News sentiment (after hours, short/long)",
    "news_cap":             "News-adjusted market cap",
    "news_atr14":           "News ATR 14-day",
    "news_eod_close":       "News end-of-day close",
    "news_pe_ratio":        "News P/E ratio",
    "news_atr_ratio":       "News ATR ratio",
    "news_mins_20_chg":     "News 20-min price change",
    "news_tot_ticks":       "News total ticks",
    "news_max_up_ret":      "News max upside return",
    "news_pct_1min":        "News 1-min price pct change",
    "nws12_mainz_01p":      "News main z-score",
    "nws12_afterhsz_57s":   "News after-hours sentiment (5-7 sec)",
    "nws12_prez_4l":        "News pre-market z-score",
    # Ravenpack
    "rp_css_business":      "RP composite sentiment - business",
    "rp_nip_inverstor":     "RP net investor positive",
    "rp_ess_ratings":       "RP event sentiment - ratings",
    "rp_css_ratings":       "RP composite sentiment - ratings",
    "rp_css_earnings":      "RP composite sentiment - earnings",
    "rp_ess_partner":       "RP event sentiment - partner",
}

SENTIMENT_FIELDS = {
    # Sentiment Data for Equity
    "scl12_buzz":           "Social buzz score (coverage=1.0)",
    "snt_buzz":             "Sentiment buzz",
    "snt_buzz_bfl":         "Sentiment buzz backfilled",
    "snt_social_value":     "Social media sentiment value",
    "snt_social_volume":    "Social media volume",
    "scl12_buzzvec":        "Social buzz vector",
    "snt_buzz_ret":         "Sentiment buzz return",
    "scl12_sentiment":      "Social sentiment score",
    "snt_value":            "Sentiment value",
    # Sentiment indicators
    "snt1_d1_analystcoverage":    "Analyst coverage indicator",
    "snt1_d1_earningsrevision":   "Earnings revision indicator",
    "snt1_d1_earningstorpedo":    "Earnings torpedo indicator",
    "snt1_d1_longtermepsgrowthest":"Long-term EPS growth estimate",
}

OPTION_FIELDS = {
    # Volatility Data (64 fields)
    "implied_volatility_call_270": "IV call 270-day",
    "implied_volatility_put_270":  "IV put 270-day",
    "implied_volatility_call_120": "IV call 120-day",
    "implied_volatility_call_1080":"IV call 1080-day",
    "implied_volatility_mean_10":  "IV mean 10-day",
    "implied_volatility_call_60":  "IV call 60-day",
    "implied_volatility_call_30":  "IV call 30-day",
    "implied_volatility_put_60":   "IV put 60-day",
    "implied_volatility_put_120":  "IV put 120-day",
    "parkinson_volatility_120":    "Parkinson volatility 120-day",
    "historical_volatility_180":   "Historical vol 180-day",
    "historical_volatility_120":   "Historical vol 120-day",
    # Options Analytics (74 fields)
    "pcr_oi_270":           "Put-call ratio OI 270-day",
    "pcr_oi_180":           "Put-call ratio OI 180-day",
    "pcr_oi_120":           "Put-call ratio OI 120-day",
    "pcr_oi_10":            "Put-call ratio OI 10-day",
    "call_breakeven_10":    "Call breakeven 10-day",
    "call_breakeven_20":    "Call breakeven 20-day",
}

RELATIONSHIP_FIELDS = {
    # Relationship Data for Equity (165 fields)
    "pv13_h_min2_3000_sector":     "Sector-relative hedge min 2",
    "pv13_r2_min2_3000_sector":    "Sector R² min 2",
    "pv13_r2_min20_3000_sector":   "Sector R² min 20",
    "pv13_h_min2_focused_pureplay_3000_sector": "Focused pureplay hedge",
    "rel_num_part":                "Number of partner relationships",
    "rel_num_all":                 "Number of all relationships",
    "pv13_revere_key_sector_total":"Revere key sector total",
    "rel_ret_all":                 "Relative return (all relationships)",
    "rel_ret_comp":                "Relative return (competitor)",
    "rel_ret_part":                "Relative return (partner)",
    "rel_ret_cust":                "Relative return (customer)",
}

MODEL_FIELDS = {
    # Analysts' Factor Model (3241 fields) — top by alpha count
    "mdl177_garpanalystmodel_qgp_vfpriceratio":     "GARP value-to-price ratio",
    "mdl177_fangma_gpam_usa_fangma_gpam11":          "FANGMA growth model",
    "mdl177_2_sensitivityfactor400_ttmocfev":        "TTM operating CF/EV sensitivity",
    "mdl177_2_sensitivityfactor400_chg12msip":       "12M change in SIP sensitivity",
    "mdl177_2_liquidityriskfactor_si_ratio":          "Liquidity risk SI ratio",
    "mdl177_2_managementqualityfactor_saleicap":     "Mgmt quality: sales/invested cap",
    "mdl177_2_deepvaluefactor_fcfp":                 "Deep value: FCF/Price",
    "mdl177_2_managementqualityfactor_noato":        "Mgmt quality: net operating ATO",
    "mdl177_2_earningsqualityfactor_uap":            "Earnings quality: unexpected accruals",
    "mdl177_2_relativevaluemodel_ttmfcfp":           "Relative value: TTM FCF/Price",
    "mdl177_valueanalystmodel_qva_chgacc":           "Value analyst: change in accruals",
    "mdl177_5shortsentimentfactor_act_util":          "Short sentiment: actual utilization",
    # Fundamental Scores (24 fields)
    "fscore_quality":       "Fundamental quality score",
    "fscore_momentum":      "Fundamental momentum score",
    "fscore_value":         "Fundamental value score",
    "fscore_profitability": "Fundamental profitability score",
    "fscore_total":         "Fundamental total score",
    "fscore_growth":        "Fundamental growth score",
    "fscore_surface":       "Fundamental surface score",
    "analyst_revision_rank_derivative": "Analyst revision rank derivative",
    # Systematic Risk (16 fields)
    "unsystematic_risk_last_360_days": "Unsystematic risk 360d",
    "unsystematic_risk_last_90_days":  "Unsystematic risk 90d",
    "systematic_risk_last_90_days":    "Systematic risk 90d",
    "beta_last_60_days_spy":           "Beta vs SPY 60d",
    "beta_last_90_days_spy":           "Beta vs SPY 90d",
    "correlation_last_60_days_spy":    "Correlation vs SPY 60d",
}

ALL_DATA_FIELDS = {
    **PRICE_VOLUME_FIELDS,
    **GROUP_FIELDS,
    **FUNDAMENTAL_FIELDS,
    **ANALYST_FIELDS,
    **NEWS_FIELDS,
    **SENTIMENT_FIELDS,
    **OPTION_FIELDS,
    **RELATIONSHIP_FIELDS,
    **MODEL_FIELDS,
}

# ─────────────────────────────────────────────
# FIELD CATEGORIES (for diversity tracking)
# ─────────────────────────────────────────────
FIELD_TO_CATEGORY = {}
for f in PRICE_VOLUME_FIELDS: FIELD_TO_CATEGORY[f] = "price_volume"
for f in GROUP_FIELDS:        FIELD_TO_CATEGORY[f] = "group"
for f in FUNDAMENTAL_FIELDS:  FIELD_TO_CATEGORY[f] = "fundamental"
for f in ANALYST_FIELDS:      FIELD_TO_CATEGORY[f] = "analyst"
for f in NEWS_FIELDS:         FIELD_TO_CATEGORY[f] = "news"
for f in SENTIMENT_FIELDS:    FIELD_TO_CATEGORY[f] = "sentiment"
for f in OPTION_FIELDS:       FIELD_TO_CATEGORY[f] = "option"
for f in RELATIONSHIP_FIELDS: FIELD_TO_CATEGORY[f] = "relationship"
for f in MODEL_FIELDS:        FIELD_TO_CATEGORY[f] = "model"

# ─────────────────────────────────────────────
# COMMON WINDOWS
# ─────────────────────────────────────────────
COMMON_WINDOWS = [5, 10, 20, 40, 60, 120, 252]

# ─────────────────────────────────────────────
# SIMULATION SETTINGS
# ─────────────────────────────────────────────
SIMULATION_SETTINGS = {
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "MARKET",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "OFF",
    "language": "FASTEXPR",
    "instrumentType": "EQUITY",
}

# ─────────────────────────────────────────────
# QUALITY THRESHOLDS for keeping alphas
# ─────────────────────────────────────────────
QUALITY_THRESHOLDS = {
    "sharpe":       1.25,   # minimum annualized Sharpe ratio
    "fitness":      1.00,   # Brain fitness score minimum
    "turnover_min": 0.01,   # too low = not trading
    "turnover_max": 0.70,   # too high = noise
}

# ─────────────────────────────────────────────
# STRATEGY ARCHETYPES  (drives daily rotation)
# Rebuilt around actual available datasets
# ─────────────────────────────────────────────
STRATEGY_ARCHETYPES = [
    {
        "name": "Fundamental Yield",
        "description": "Accounting-yield signals: cash flow, earnings, or revenue scaled by cap",
        "primary_fields": ["cashflow_op", "operating_income", "ebitda", "ebit", "sales", "equity", "cap", "assets"],
        "typical_operators": ["ts_rank", "rank", "group_rank", "ts_backfill"],
        "typical_windows": [120, 252],
        "theory": "Stocks with high fundamental yield (cash flow / price) outperform (Lakonishok 1994)",
    },
    {
        "name": "Mean Reversion",
        "description": "Short-term price reversal after overshoot",
        "primary_fields": ["returns", "close", "open", "vwap", "volume", "adv20"],
        "typical_operators": ["ts_zscore", "ts_rank", "ts_delta", "rank", "trade_when"],
        "typical_windows": [3, 5, 10, 20],
        "theory": "Short-term price moves tend to reverse; market microstructure creates predictable patterns",
    },
    {
        "name": "News & Sentiment",
        "description": "Signals from news flow, social buzz, and sentiment data",
        "primary_fields": ["scl12_buzz", "snt_buzz", "scl12_sentiment", "snt_value",
                          "nws12_afterhsz_sl", "news_max_up_ret", "news_pct_1min",
                          "rp_css_business", "rp_ess_ratings"],
        "typical_operators": ["ts_rank", "ts_backfill", "rank", "ts_delta", "ts_regression", "winsorize"],
        "typical_windows": [5, 10, 20, 60],
        "theory": "News and social sentiment predict short-term returns; information diffuses slowly across markets",
    },
    {
        "name": "Implied Volatility",
        "description": "Options-implied volatility signals and term structure",
        "primary_fields": ["implied_volatility_call_270", "implied_volatility_call_120",
                          "implied_volatility_call_60", "implied_volatility_mean_10",
                          "parkinson_volatility_120", "historical_volatility_120",
                          "pcr_oi_270", "pcr_oi_120"],
        "typical_operators": ["ts_backfill", "ts_rank", "rank", "ts_regression", "ts_delta"],
        "typical_windows": [20, 60, 120, 252],
        "theory": "Implied vol contains forward-looking information; vol term structure and put-call ratios predict returns",
    },
    {
        "name": "Analyst Estimates",
        "description": "Signals from analyst consensus, revisions, and estimate momentum",
        "primary_fields": ["est_eps", "est_sales", "est_ebit", "est_fcf", "est_ptp",
                          "anl4_ebit_value", "anl4_ebitda_value", "anl4_adjusted_netincome_ft",
                          "analyst_revision_rank_derivative"],
        "typical_operators": ["ts_rank", "ts_delta", "rank", "ts_backfill", "ts_regression"],
        "typical_windows": [20, 40, 60, 120],
        "theory": "Analyst revisions predict returns; markets underreact to estimate changes (Chan 1996)",
    },
    {
        "name": "Relationship & Relative Returns",
        "description": "Peer-relative performance and supply chain relationship signals",
        "primary_fields": ["rel_ret_all", "rel_ret_comp", "rel_ret_part", "rel_ret_cust",
                          "rel_num_part", "rel_num_all",
                          "pv13_h_min2_3000_sector", "pv13_r2_min2_3000_sector"],
        "typical_operators": ["ts_rank", "ts_sum", "ts_product", "ts_delta", "rank", "ts_delay"],
        "typical_windows": [5, 10, 20, 60],
        "theory": "Supply chain and peer relationships transmit information with delay; relative returns capture momentum diffusion",
    },
    {
        "name": "Factor Model Composites",
        "description": "Pre-built factor scores and multi-factor model signals",
        "primary_fields": ["fscore_quality", "fscore_value", "fscore_momentum",
                          "fscore_profitability", "fscore_growth", "fscore_total",
                          "mdl177_2_deepvaluefactor_fcfp",
                          "mdl177_2_earningsqualityfactor_uap",
                          "mdl177_2_managementqualityfactor_saleicap"],
        "typical_operators": ["ts_rank", "rank", "group_rank", "ts_delta", "ts_backfill"],
        "typical_windows": [20, 60, 120, 252],
        "theory": "Combining orthogonal factors (value+quality+momentum) provides more robust signals than single factors",
    },
    {
        "name": "Volatility Regime",
        "description": "Realized vol, vol-of-vol, and risk metric signals",
        "primary_fields": ["returns", "close", "high", "low",
                          "unsystematic_risk_last_360_days", "unsystematic_risk_last_90_days",
                          "beta_last_60_days_spy", "systematic_risk_last_90_days"],
        "typical_operators": ["ts_std_dev", "ts_rank", "rank", "ts_scale", "ts_zscore"],
        "typical_windows": [5, 10, 22, 60, 252],
        "theory": "Low-volatility anomaly (Baker 2011): low-vol stocks outperform on risk-adjusted basis",
    },
    {
        "name": "Balance Sheet Quality",
        "description": "Leverage, accruals, and financial health signals",
        "primary_fields": ["debt", "debt_lt", "debt_st", "assets", "equity", "liabilities",
                          "cashflow_op", "income", "capex", "retained_earnings",
                          "interest_expense", "cash"],
        "typical_operators": ["ts_rank", "rank", "group_rank", "group_neutralize", "ts_delta"],
        "typical_windows": [60, 120, 252],
        "theory": "Firms with low leverage, high cash quality outperform (Sloan 1996 accruals, Altman Z-score)",
    },
    {
        "name": "Intraday & Volume Patterns",
        "description": "Open-close spreads, high-low range, and volume dynamics",
        "primary_fields": ["open", "close", "high", "low", "vwap", "volume", "adv20"],
        "typical_operators": ["ts_rank", "rank", "ts_mean", "ts_delta", "trade_when"],
        "typical_windows": [5, 10, 20],
        "theory": "Intraday price patterns reflect informed vs. uninformed trading; volume confirms direction",
    },
    {
        "name": "Social Media Alpha",
        "description": "Social media volume, sentiment value, and buzz-return interaction",
        "primary_fields": ["snt_social_value", "snt_social_volume", "scl12_buzz",
                          "scl12_sentiment", "snt_buzz_ret", "snt_buzz_bfl"],
        "typical_operators": ["ts_rank", "ts_delta", "ts_backfill", "rank", "ts_regression"],
        "typical_windows": [5, 10, 20, 40],
        "theory": "Social media attention predicts short-term trading activity and returns (Chen et al. 2014)",
    },
    {
        "name": "Cross-Sectional Relative Strength",
        "description": "Within-group relative performance and sector rotation",
        "primary_fields": ["returns", "close", "volume", "cap"],
        "typical_operators": ["group_rank", "group_neutralize", "group_zscore", "ts_rank", "ts_sum"],
        "typical_windows": [20, 60, 120],
        "theory": "Within-sector momentum is cleaner signal than absolute momentum (Moskowitz & Grinblatt 1999)",
    },
]


def get_todays_archetype(day_offset: int = 0) -> dict:
    """Select archetype by rotating through all types."""
    import datetime
    day_num = (datetime.date.today().toordinal() + day_offset) % len(STRATEGY_ARCHETYPES)
    return STRATEGY_ARCHETYPES[day_num]


def format_operators_for_prompt() -> str:
    """Return a compact, LLM-readable list of valid operators."""
    lines = []
    lines.append("=== BASE / MATH OPERATORS ===")
    lines.append(", ".join(MATH_OPERATORS))
    lines.append("\n=== LOGICAL OPERATORS ===")
    lines.append(", ".join(LOGICAL_OPERATORS))
    lines.append("  Plus infix comparisons: <, <=, ==, >, >=, !=")
    lines.append("\n=== TIME-SERIES OPERATORS (require window integer) ===")
    lines.append(", ".join(TS_OPERATORS))
    lines.append("\n=== CROSS-SECTIONAL OPERATORS ===")
    lines.append(", ".join(CS_OPERATORS))
    lines.append("\n=== VECTOR OPERATORS ===")
    lines.append(", ".join(VECTOR_OPERATORS))
    lines.append("\n=== TRANSFORMATIONAL OPERATORS ===")
    lines.append(", ".join(TRANSFORM_OPERATORS))
    lines.append("\n=== GROUP OPERATORS ===")
    lines.append(", ".join(GROUP_OPERATORS))
    return "\n".join(lines)


def format_fields_for_prompt(category: str = "all") -> str:
    """Return formatted data fields for LLM prompt."""
    sections = {
        "price_volume":  ("PRICE / VOLUME FIELDS", PRICE_VOLUME_FIELDS),
        "group":         ("GROUPING FIELDS", GROUP_FIELDS),
        "fundamental":   ("FUNDAMENTAL FIELDS", FUNDAMENTAL_FIELDS),
        "analyst":       ("ANALYST / ESTIMATE FIELDS", ANALYST_FIELDS),
        "news":          ("NEWS FIELDS", NEWS_FIELDS),
        "sentiment":     ("SENTIMENT FIELDS", SENTIMENT_FIELDS),
        "option":        ("OPTION / VOLATILITY FIELDS", OPTION_FIELDS),
        "relationship":  ("RELATIONSHIP FIELDS", RELATIONSHIP_FIELDS),
        "model":         ("FACTOR MODEL FIELDS", MODEL_FIELDS),
    }
    if category != "all" and category in sections:
        title, fields = sections[category]
        lines = [f"=== {title} ==="]
        for name, desc in fields.items():
            lines.append(f"  {name}: {desc}")
        return "\n".join(lines)

    all_lines = []
    for title, fields in sections.values():
        all_lines.append(f"\n=== {title} ===")
        for name, desc in fields.items():
            all_lines.append(f"  {name}: {desc}")
    return "\n".join(all_lines)
