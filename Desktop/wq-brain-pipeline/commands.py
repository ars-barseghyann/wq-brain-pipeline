# ============================================================
#  commands.py  —  curated alpha library (FIXED + EXPANDED)
#
#  CHANGES from original:
#    • Removed adv60 (not a Brain field — only adv20 exists)
#    • Removed ts_skewness (not an official operator)
#    • Removed fam_est_eps_rank (not in Brain fields CSV)
#    • Added Archetype G: Sentiment & Social Media (UNTAPPED)
#    • Added Archetype H: Factor Model Composites (UNTAPPED)
#    • Added Archetype I: Options / Implied Volatility (LIGHTLY USED)
#    • Added Archetype J: Relationship & Relative Returns (LIGHTLY USED)
#    • Updated daily_batch() with picks from new archetypes
#
#  Ground rules:
#    • Fundamental alphas  → SUBINDUSTRY, Decay 5, TOP3000
#    • Price-vol alphas    → NONE, Decay 0-2, TOP3000
#    • News/sentiment      → MARKET, Decay 0, TOP3000
#    • Options/vol data    → MARKET, Decay 0, TOP3000
#    • Always wrap outer expression in rank() for weight safety
#    • Use ts_backfill for sparse data fields
#    • No already-submitted expressions (see SUBMITTED_ALPHAS in database.py)
# ============================================================

from database import (
    SAFE_SETTINGS_FUNDAMENTAL, SAFE_SETTINGS_PRICE,
    SAFE_SETTINGS_NEWS, SAFE_SETTINGS_OPTION,
)


def _fund(**overrides):
    s = dict(SAFE_SETTINGS_FUNDAMENTAL)
    s.update(overrides)
    return s

def _price(**overrides):
    s = dict(SAFE_SETTINGS_PRICE)
    s.update(overrides)
    return s

def _news(**overrides):
    s = dict(SAFE_SETTINGS_NEWS)
    s.update(overrides)
    return s

def _option(**overrides):
    s = dict(SAFE_SETTINGS_OPTION)
    s.update(overrides)
    return s


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE A — Fundamental Yield (ts_rank / cap structure)
# ─────────────────────────────────────────────────────────────
def archetype_a_fundamental_yield():
    alphas = [
        # A1 — Gross-profit yield
        {**_fund(), 'code': 'rank(ts_rank((sales - cogs) / cap, 252))'},
        # A2 — EBITDA yield
        {**_fund(), 'code': 'rank(ts_rank(ebitda / cap, 252))'},
        # A3 — Book-to-market
        {**_fund(), 'code': 'rank(ts_rank(equity / cap, 252))'},
        # A4 — Leverage reduction
        {**_fund(), 'code': 'rank(-ts_rank(debt_lt / cap, 252))'},
        # A5 — Sales yield
        {**_fund(), 'code': 'rank(ts_rank(sales / cap, 252))'},
        # A6 — Inventory efficiency
        {**_fund(), 'code': 'rank(-ts_rank(inventory / cap, 252))'},
        # A7 — Capital-light premium
        {**_fund(), 'code': 'rank(-ts_rank(ppent / cap, 252))'},
        # A8 — Gross margin trend
        {**_fund(), 'code': 'rank(ts_rank((sales - cogs) / sales, 252))'},
        # A9 — Operating leverage
        {**_fund(), 'code': 'rank(ts_rank(ebit / ebitda, 252))'},
        # A10 — Cash return on assets
        {**_fund(), 'code': 'rank(ts_rank(cashflow_op / assets, 252))'},
        # TOP1000 variants
        {**_fund(universe='TOP1000'), 'code': 'rank(ts_rank(ebitda / cap, 252))'},
        {**_fund(universe='TOP1000'), 'code': 'rank(ts_rank(equity / cap, 252))'},
        # Shorter lookback
        {**_fund(), 'code': 'rank(ts_rank(ebitda / cap, 120))'},
        {**_fund(), 'code': 'rank(ts_rank(equity / cap, 120))'},
        {**_fund(), 'code': 'rank(-ts_rank(debt_lt / cap, 120))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE B — Composite Fundamental × Volume
#  FIXED: removed adv60 (not a Brain field)
# ─────────────────────────────────────────────────────────────
def archetype_b_fundamental_volume():
    fund_legs = [
        'ts_rank(ebitda / cap, 252)',
        'ts_rank(equity / cap, 252)',
        'ts_rank((sales - cogs) / cap, 252)',
        'ts_rank(-debt_lt / cap, 252)',
        'ts_rank(cashflow_op / assets, 252)',
        'ts_rank(sales / cap, 252)',
    ]
    vol_legs = [
        'rank(volume / adv20)',
        'rank(ts_rank(volume / adv20, 20))',
    ]
    alphas = []
    for fl in fund_legs:
        for vl in vol_legs:
            alphas.append({
                **_price(neutralization='NONE', decay=2),
                'code': f'rank({fl}) * {vl}'
            })
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE C — Conditional Reversion (trade_when gate)
# ─────────────────────────────────────────────────────────────
def archetype_c_conditional_reversion():
    alphas = [
        # C1 — Volume spike gates reversal
        {**_price(decay=0), 'code':
            'trade_when(ts_rank(volume/adv20, 20) > 0.7, rank(-ts_delta(close, 3)), -1)'},
        # C2 — 5-day momentum reversal
        {**_price(decay=0), 'code':
            'trade_when(volume > ts_mean(volume, 20), rank(-ts_delta(close, 5)), -1)'},
        # C3 — Intraday range breakout reversal
        {**_price(decay=0), 'code':
            'trade_when(ts_rank((high - low) / close, 20) > 0.6, rank(-(high + low) / 2 + close), -1)'},
        # C4 — Volatility-regime reversion
        {**_price(decay=0), 'code':
            'trade_when(ts_rank(ts_std_dev(returns, 22), 252) > 0.55, rank(-ts_delta(close, 5)), -1)'},
        # C5 — Returns-momentum reversal in elevated vol
        {**_price(decay=2), 'code':
            'trade_when(ts_rank(ts_std_dev(returns, 10), 60) > 0.5, rank(-ts_sum(returns, 5)), -1)'},
        # C6 — Open-to-close reversion gated by volume
        {**_price(decay=0), 'code':
            'trade_when(volume > ts_mean(volume, 5), rank(open - close), -1)'},
        # C7 — Gap-open reversion
        {**_price(decay=0), 'code':
            'trade_when(ts_rank(volume, 5) > 0.8, rank(-(open - ts_delay(close, 1))), -1)'},
        # C8 — Consecutive-day loss reversal
        {**_price(decay=0), 'code':
            'trade_when(ts_sum(returns < 0, 3) >= 2, rank(-ts_delta(close, 3)), -1)'},
        # C9 — High-vol + negative return = oversold bounce
        {**_price(decay=0), 'code':
            'trade_when(volume > ts_mean(volume, 20) and returns < 0, rank(-returns), -1)'},
        # C10 — Volume-weighted price pressure reversal
        {**_price(decay=2), 'code':
            'trade_when(ts_rank(volume/adv20, 10) > 0.65, rank(-ts_delta(close, 2)) * rank(volume/adv20), -1)'},
        # TOP1000 variants
        {**_price(decay=0, universe='TOP1000'), 'code':
            'trade_when(volume > ts_mean(volume, 20), rank(-ts_delta(close, 5)), -1)'},
        {**_price(decay=0, universe='TOP1000'), 'code':
            'trade_when(ts_rank(ts_std_dev(returns, 22), 252) > 0.55, rank(-ts_delta(close, 5)), -1)'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE D — Cross-Sectional Quality Composites
# ─────────────────────────────────────────────────────────────
def archetype_d_cross_sectional_quality():
    alphas = [
        # D1 — Sector-relative earnings quality × volume trend
        {**_fund(decay=0), 'code':
            'group_rank(ts_rank(ebitda/cap, 252), sector) * (1 + rank(volume/adv20))'},
        # D2 — Industry-relative gross margin × size
        {**_fund(decay=0), 'code':
            'group_rank(ts_rank((sales-cogs)/sales, 120), industry) * rank(1/cap)'},
        # D3 — Subindustry book-value rank
        {**_fund(decay=5), 'code':
            'group_rank(ts_rank(equity/cap, 252), subindustry)'},
        # D4 — Sector cash yield composite
        {**_fund(decay=5), 'code':
            'group_rank(ts_rank(cashflow_op/cap, 120), sector) * (1 + rank(ts_rank(ebitda/cap, 120)))'},
        # D5 — Operating efficiency vs sector peers
        {**_fund(decay=5), 'code':
            'group_rank(ts_rank(ebit/assets, 252), subindustry)'},
        # D6 — Sector-relative leverage
        {**_fund(decay=0), 'code':
            'group_rank(-ts_rank(debt_lt/cap, 252), sector)'},
        # D7 — Multi-factor: value + quality within subindustry
        {**_fund(decay=5), 'code':
            'group_rank(ts_rank(equity/cap, 252) + ts_rank(cashflow_op/cap, 252), subindustry)'},
        # D8 — Capital-light premium vs peers
        {**_fund(decay=0, universe='TOP1000'), 'code':
            'group_rank(-ts_rank(ppent/assets, 252), sector)'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE E — Volatility & Regime Signals
#  FIXED: removed ts_skewness (not an official Brain operator)
# ─────────────────────────────────────────────────────────────
def archetype_e_volatility_regime():
    alphas = [
        # E1 — Vol-of-vol mean reversion
        {**_price(decay=0), 'code':
            'rank(-ts_std_dev(ts_std_dev(returns, 5), 20))'},
        # E2 — Intraday volatility compression
        {**_price(decay=2), 'code':
            'rank(-ts_rank((high - low) / close, 60))'},
        # E3 — Short vs medium vol ratio (compression)
        {**_price(decay=0), 'code':
            'rank(-(ts_std_dev(returns, 5) / ts_std_dev(returns, 60)))'},
        # E4 — Realized vol percentile (low vol = quality)
        {**_price(decay=2), 'code':
            'rank(-ts_rank(ts_std_dev(returns, 22), 252))'},
        # E5 — Volume-vol interaction (silent stocks)
        {**_price(decay=0), 'code':
            'rank(-ts_std_dev(returns, 10)) * rank(ts_rank(volume/adv20, 20))'},
        # E6 — Momentum decay regression
        {**_price(decay=2), 'code':
            'rank(-ts_regression(returns, ts_delay(returns, 1), 60))'},
        # E7 — Vol-gated returns (normal vol regime only)
        {**_price(decay=0, universe='TOP1000'), 'code':
            'trade_when(ts_rank(ts_std_dev(returns,22),252) < 0.7, rank(-ts_sum(returns,5)), -1)'},
        # E8 — Unsystematic risk signal (low idio risk = quality)
        {**_price(decay=2), 'code':
            'rank(-ts_backfill(unsystematic_risk_last_360_days, 60))'},
        # E9 — Beta-adjusted momentum
        {**_price(decay=0), 'code':
            'rank(-ts_backfill(beta_last_60_days_spy, 20)) * rank(ts_rank(returns, 60))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE F — Analyst Estimates (FIXED)
#  REMOVED: fam_est_eps_rank (not a valid Brain field)
#  REPLACED with: est_eps, anl4 fields, analyst_revision_rank_derivative
# ─────────────────────────────────────────────────────────────
def archetype_f_analyst_estimates():
    alphas = [
        # F1 — EPS estimate rank × volume
        {**_price(decay=2), 'code':
            'rank(ts_rank(ts_backfill(est_eps, 60), 40)) * rank(volume / adv20)'},
        # F2 — Forward EPS vs cap
        {**_fund(decay=5), 'code':
            'rank(ts_rank(fnd6_newa1v1300_epspi / cap, 252))'},
        # F3 — Operating EPS quarterly change
        {**_fund(decay=5), 'code':
            'rank(ts_delta(fnd6_cptnewqv1300_opepsq, 63) / cap)'},
        # F4 — Analyst revision rank derivative (momentum of revisions)
        {**_fund(decay=5, universe='TOP1000'), 'code':
            'rank(ts_rank(ts_backfill(analyst_revision_rank_derivative, 60), 120))'},
        # F5 — EPS estimate × book value composite
        {**_fund(decay=5), 'code':
            'rank(ts_rank(ts_backfill(est_eps, 60), 40)) * rank(ts_rank(equity/cap, 252))'},
        # F6 — EBIT estimate vs actual divergence
        {**_fund(decay=5), 'code':
            'rank(ts_backfill(anl4_ebit_value, 60) / ebit)'},
        # F7 — Sales estimate momentum
        {**_fund(decay=5), 'code':
            'rank(ts_delta(ts_backfill(est_sales, 60), 63))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE G — Sentiment & Social Media  *** NEW ***
#  UNTAPPED DATASET — zero correlation with submitted portfolio
# ─────────────────────────────────────────────────────────────
def archetype_g_sentiment_social():
    alphas = [
        # G1 — Social buzz trend (rising attention)
        {**_news(decay=0), 'code':
            'rank(ts_delta(scl12_buzz, 5))'},
        # G2 — Sentiment value rank
        {**_news(decay=2), 'code':
            'rank(ts_rank(snt_value, 20))'},
        # G3 — Buzz × sentiment composite
        {**_news(decay=0), 'code':
            'rank(ts_rank(scl12_buzz, 10)) * rank(scl12_sentiment)'},
        # G4 — Social volume surge gated reversion
        {**_news(decay=0), 'code':
            'trade_when(ts_rank(snt_social_volume, 10) > 0.7, rank(snt_social_value), -1)'},
        # G5 — Sentiment buzz return (pre-computed return after buzz)
        {**_news(decay=2), 'code':
            'rank(ts_rank(snt_buzz_ret, 20))'},
        # G6 — Analyst coverage indicator momentum
        {**_news(decay=0), 'code':
            'rank(ts_delta(ts_backfill(snt1_d1_analystcoverage, 20), 10))'},
        # G7 — Earnings revision indicator × social buzz
        {**_news(decay=2), 'code':
            'rank(ts_backfill(snt1_d1_earningsrevision, 20)) * rank(scl12_buzz)'},
        # G8 — Sentiment mean reversion (oversold on negative sentiment)
        {**_news(decay=0), 'code':
            'trade_when(ts_rank(scl12_sentiment, 20) < 0.3, rank(-ts_delta(close, 5)), -1)'},
        # G9 — Social buzz backfilled rank (smooth signal)
        {**_news(decay=0, universe='TOP1000'), 'code':
            'rank(ts_rank(snt_buzz_bfl, 40))'},
        # G10 — Earnings torpedo indicator (surprise risk)
        {**_news(decay=0), 'code':
            'rank(-ts_backfill(snt1_d1_earningstorpedo, 20))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE H — Factor Model Composites  *** NEW ***
#  Uses pre-built factor scores — UNTAPPED dataset
# ─────────────────────────────────────────────────────────────
def archetype_h_factor_models():
    alphas = [
        # H1 — Quality factor score rank
        {**_fund(decay=0, neutralization='MARKET'), 'code':
            'rank(ts_rank(ts_backfill(fscore_quality, 60), 120))'},
        # H2 — Value factor × quality composite
        {**_fund(decay=5, neutralization='MARKET'), 'code':
            'rank(ts_backfill(fscore_value, 60)) * rank(ts_backfill(fscore_quality, 60))'},
        # H3 — Deep value FCF/Price model
        {**_fund(decay=5, neutralization='MARKET'), 'code':
            'rank(ts_rank(ts_backfill(mdl177_2_deepvaluefactor_fcfp, 60), 252))'},
        # H4 — Earnings quality factor (accruals)
        {**_fund(decay=0, neutralization='SUBINDUSTRY'), 'code':
            'group_rank(ts_backfill(mdl177_2_earningsqualityfactor_uap, 60), sector)'},
        # H5 — Management quality: sales/invested capital
        {**_fund(decay=5, neutralization='MARKET'), 'code':
            'rank(ts_rank(ts_backfill(mdl177_2_managementqualityfactor_saleicap, 60), 120))'},
        # H6 — Factor momentum: fscore_total trend
        {**_fund(decay=0, neutralization='MARKET'), 'code':
            'rank(ts_delta(ts_backfill(fscore_total, 60), 20))'},
        # H7 — Profitability × growth composite
        {**_fund(decay=5, neutralization='MARKET'), 'code':
            'rank(ts_backfill(fscore_profitability, 60)) * rank(ts_backfill(fscore_growth, 60))'},
        # H8 — Relative value model (TTM FCF/Price)
        {**_fund(decay=5, neutralization='MARKET', universe='TOP1000'), 'code':
            'rank(ts_rank(ts_backfill(mdl177_2_relativevaluemodel_ttmfcfp, 60), 252))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE I — Options / Implied Volatility  *** NEW ***
#  Extends alpha #8 into new territory
# ─────────────────────────────────────────────────────────────
def archetype_i_options_vol():
    alphas = [
        # I1 — Put-call ratio OI trend (sentiment proxy)
        {**_option(decay=0), 'code':
            'rank(-ts_delta(ts_backfill(pcr_oi_270, 60), 20))'},
        # I2 — IV term structure slope (270d vs 60d call IV)
        {**_option(decay=2), 'code':
            'rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_call_60, 60))'},
        # I3 — IV mean reversion (high IV → buy)
        {**_option(decay=0), 'code':
            'trade_when(ts_rank(ts_backfill(implied_volatility_mean_10,60), 60) > 0.8, rank(-ts_delta(close, 5)), -1)'},
        # I4 — Put IV vs Call IV skew
        {**_option(decay=2), 'code':
            'rank(ts_backfill(implied_volatility_put_270, 60) / ts_backfill(implied_volatility_call_270, 60))'},
        # I5 — Call breakeven trend
        {**_option(decay=0), 'code':
            'rank(ts_delta(ts_backfill(call_breakeven_20, 60), 10))'},
        # I6 — IV/Historical vol ratio (cheap options signal)
        {**_option(decay=2), 'code':
            'rank(-ts_backfill(implied_volatility_call_120, 60) / ts_backfill(historical_volatility_120, 60))'},
        # I7 — PCR × returns interaction (contrarian)
        {**_option(decay=0), 'code':
            'rank(ts_backfill(pcr_oi_120, 60)) * rank(-ts_sum(returns, 5))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  ARCHETYPE J — Relationship & Relative Returns  *** NEW ***
#  Extends alpha #9 into new territory
# ─────────────────────────────────────────────────────────────
def archetype_j_relationship():
    alphas = [
        # J1 — Competitor relative return momentum
        {**_price(decay=2), 'code':
            'rank(ts_rank(rel_ret_comp, 20))'},
        # J2 — Partner vs competitor return spread
        {**_price(decay=0), 'code':
            'rank(rel_ret_part - rel_ret_comp)'},
        # J3 — Sector R² signal (high R² = crowded)
        {**_price(decay=2), 'code':
            'rank(-pv13_r2_min2_3000_sector)'},
        # J4 — Customer relative return (supply chain signal)
        {**_price(decay=0), 'code':
            'rank(ts_delta(rel_ret_cust, 5))'},
        # J5 — Number of relationships × return quality
        {**_price(decay=2), 'code':
            'rank(rel_num_all) * rank(ts_rank(returns, 60))'},
        # J6 — Hedge factor trend (sector-relative)
        {**_price(decay=0), 'code':
            'rank(ts_delta(pv13_h_min2_3000_sector, 10))'},
        # J7 — Relative return all (cumulative short-term)
        {**_price(decay=0, universe='TOP1000'), 'code':
            'rank(ts_sum(rel_ret_all, 5))'},
    ]
    return alphas


# ─────────────────────────────────────────────────────────────
#  MASTER LIST — all archetypes
# ─────────────────────────────────────────────────────────────
def all_alphas():
    """All curated alphas. Run overnight."""
    return (
        archetype_a_fundamental_yield()    +   # ~15
        archetype_b_fundamental_volume()   +   # ~12
        archetype_c_conditional_reversion()+   # ~12
        archetype_d_cross_sectional_quality()+ # ~8
        archetype_e_volatility_regime()    +   # ~9
        archetype_f_analyst_estimates()    +   # ~7
        archetype_g_sentiment_social()     +   # ~10 NEW
        archetype_h_factor_models()        +   # ~8  NEW
        archetype_i_options_vol()          +   # ~7  NEW
        archetype_j_relationship()             # ~7  NEW
    )   # ≈ 95 total candidates


# ─────────────────────────────────────────────────────────────
#  FOCUSED DAILY BATCH — diversified across ALL archetypes
#  Prioritizes UNTAPPED datasets for merged performance
# ─────────────────────────────────────────────────────────────
def daily_batch():
    """
    Highest-confidence candidates, biased toward untapped datasets.
    Aim: maximize diversity for merged performance improvement.
    """
    return [
        # ── Fundamental (A) — 2 picks ────────────────────────
        {**_fund(), 'code': 'rank(ts_rank(ebitda / cap, 252))'},
        {**_fund(), 'code': 'rank(ts_rank((sales - cogs) / cap, 252))'},

        # ── Conditional reversion (C) — 2 picks ─────────────
        {**_price(decay=0), 'code':
            'trade_when(volume > ts_mean(volume, 20), rank(-ts_delta(close, 5)), -1)'},
        {**_price(decay=0), 'code':
            'trade_when(ts_rank(ts_std_dev(returns, 22), 252) > 0.55, rank(-ts_delta(close, 5)), -1)'},

        # ── Sentiment/Social (G) — 3 picks *** UNTAPPED *** ─
        {**_news(decay=0), 'code':
            'rank(ts_delta(scl12_buzz, 5))'},
        {**_news(decay=0), 'code':
            'rank(ts_rank(scl12_buzz, 10)) * rank(scl12_sentiment)'},
        {**_news(decay=0), 'code':
            'trade_when(ts_rank(scl12_sentiment, 20) < 0.3, rank(-ts_delta(close, 5)), -1)'},

        # ── Factor Models (H) — 2 picks *** UNTAPPED *** ────
        {**_fund(decay=0, neutralization='MARKET'), 'code':
            'rank(ts_rank(ts_backfill(fscore_quality, 60), 120))'},
        {**_fund(decay=5, neutralization='MARKET'), 'code':
            'rank(ts_backfill(fscore_value, 60)) * rank(ts_backfill(fscore_quality, 60))'},

        # ── Options (I) — 2 picks *** LIGHTLY USED *** ──────
        {**_option(decay=0), 'code':
            'rank(-ts_delta(ts_backfill(pcr_oi_270, 60), 20))'},
        {**_option(decay=2), 'code':
            'rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_call_60, 60))'},

        # ── Relationship (J) — 2 picks *** LIGHTLY USED *** ─
        {**_price(decay=2), 'code':
            'rank(ts_rank(rel_ret_comp, 20))'},
        {**_price(decay=0), 'code':
            'rank(rel_ret_part - rel_ret_comp)'},

        # ── Vol/Risk (E) — 1 pick (new risk metric field) ───
        {**_price(decay=2), 'code':
            'rank(-ts_backfill(unsystematic_risk_last_360_days, 60))'},
    ]
