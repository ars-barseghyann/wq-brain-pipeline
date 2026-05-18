# ============================================================
#  database.py  —  confirmed Brain fields & submission history
#  All fields below are validated on WorldQuant Brain USA.
#
#  NOTE: Submitted alpha expressions have been replaced with
#  generic examples. Replace with your own submitted alphas
#  to enable proper self-correlation checking.
# ============================================================

# ── Confirmed fundamental fields (from CSV) ─────────────────
FUNDAMENTALS_CONFIRMED = [
    'operating_income', 'ebit', 'ebitda', 'cashflow_op', 'sales', 'cogs',
    'equity', 'sharesout', 'cap', 'assets', 'debt_lt', 'debt', 'debt_st',
    'inventory', 'ppent', 'income', 'revenue', 'cash', 'liabilities',
    'liabilities_curr', 'assets_curr', 'enterprise_value', 'capex',
    'bookvalue_ps', 'cashflow', 'cashflow_fin', 'cashflow_invst',
    'operating_expense', 'receivable', 'retained_earnings',
    'interest_expense', 'depre_amort', 'rd_expense', 'pretax_income',
    'income_tax', 'return_equity', 'return_assets', 'sales_growth',
    'eps', 'goodwill',
    # fnd6_ fields confirmed working
    'fnd6_newa1v1300_epspi', 'fnd6_cptnewqv1300_opepsq',
    'fnd6_newqv1300_ivltq', 'fnd6_acdo', 'fnd6_fopo',
]

# ── Analyst / Estimate fields confirmed ─────────────────────
ANALYST_CONFIRMED = [
    'est_eps', 'est_sales', 'est_ebit', 'est_fcf', 'est_ptp',
    'est_capex', 'est_cashflow_op', 'est_netprofit', 'est_bookvalue_ps',
    'anl4_ebit_value', 'anl4_ebitda_value', 'anl4_adjusted_netincome_ft',
    'analyst_revision_rank_derivative',
]

# ── News / Sentiment fields confirmed ───────────────────────
NEWS_SENTIMENT_CONFIRMED = [
    'news_max_up_ret', 'news_pct_1min', 'news_cap', 'news_atr14',
    'nws12_afterhsz_sl', 'nws12_mainz_01p',
    'scl12_buzz', 'scl12_sentiment', 'snt_buzz', 'snt_value',
    'snt_social_value', 'snt_social_volume',
    'rp_css_business', 'rp_ess_ratings',
]

# ── Option / Vol fields confirmed ───────────────────────────
OPTION_CONFIRMED = [
    'implied_volatility_call_120', 'implied_volatility_call_270',
    'implied_volatility_call_60', 'implied_volatility_mean_10',
    'parkinson_volatility_120', 'historical_volatility_120',
    'pcr_oi_270', 'pcr_oi_120',
]

# ── Relationship fields confirmed ───────────────────────────
RELATIONSHIP_CONFIRMED = [
    'rel_ret_all', 'rel_ret_comp', 'rel_ret_part', 'rel_ret_cust',
    'rel_num_part', 'rel_num_all',
    'pv13_h_min2_3000_sector', 'pv13_r2_min2_3000_sector',
]

# ── Model / Factor fields confirmed ────────────────────────
MODEL_CONFIRMED = [
    'fscore_quality', 'fscore_value', 'fscore_momentum',
    'fscore_profitability', 'fscore_total',
    'mdl177_2_deepvaluefactor_fcfp',
    'mdl177_2_earningsqualityfactor_uap',
    'mdl177_2_managementqualityfactor_saleicap',
    'unsystematic_risk_last_360_days', 'unsystematic_risk_last_90_days',
    'beta_last_60_days_spy',
]

GROUP_LEVELS = ['market', 'sector', 'industry', 'subindustry']

# ── Safe simulation settings ────────────────────────────────
SAFE_SETTINGS_FUNDAMENTAL = {
    'neutralization': 'SUBINDUSTRY', 'decay': 5, 'truncation': 0.08,
    'delay': 1, 'universe': 'TOP3000', 'region': 'USA',
}

SAFE_SETTINGS_PRICE = {
    'neutralization': 'NONE', 'decay': 2, 'truncation': 0.08,
    'delay': 1, 'universe': 'TOP3000', 'region': 'USA',
}

SAFE_SETTINGS_NEWS = {
    'neutralization': 'MARKET', 'decay': 0, 'truncation': 0.08,
    'delay': 1, 'universe': 'TOP3000', 'region': 'USA',
}

SAFE_SETTINGS_OPTION = {
    'neutralization': 'MARKET', 'decay': 0, 'truncation': 0.08,
    'delay': 1, 'universe': 'TOP3000', 'region': 'USA',
}

# ── SUBMITTED ALPHAS ────────────────────────────────────────
# Replace these with your own submitted alphas.
# Used for self-correlation checking — new alphas should be
# structurally different from these.
#
# Example format:
#   'ts_rank(fundamental_field/cap, 252)'
#   'trade_when(volume_condition, rank(price_signal), -1)'
#   'rank(-ts_corr(analyst_field_a, analyst_field_b, 63))'
#
SUBMITTED_ALPHAS = [
    # Add your submitted alpha expressions here
    # Example: 'ts_rank(operating_income/cap, 252)',
]

# ── Dataset categories used by each submitted alpha ─────────
# Track which datasets each alpha uses for correlation analysis.
# New alphas should prioritize UNUSED datasets.
SUBMITTED_DATASETS = {
    # Example:
    # 1: ['fundamental'],
    # 2: ['price_volume'],
    # 3: ['analyst'],
}
# Unused datasets to prioritize: sentiment, social_media, factor_model, risk_model
