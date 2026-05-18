# ============================================================
#  parameters.py  —  choose what to simulate today
#
#  USAGE OPTIONS:
#
#  1. DAILY BATCH  (recommended — ~13 sims, targets 3/day)
#     DATA = daily_batch()
#
#  2. FULL OVERNIGHT  (~67 sims, run before bed)
#     DATA = all_alphas()
#
#  3. SINGLE ARCHETYPE  (focused testing)
#     DATA = archetype_a_fundamental_yield()
#     DATA = archetype_c_conditional_reversion()
#     DATA = archetype_e_volatility_regime()
#
#  4. CUSTOM MANUAL  (paste in your own code)
#     DATA = [{
#         'neutralization': 'NONE',
#         'decay': 0,
#         'truncation': 0.08,
#         'delay': 1,
#         'universe': 'TOP3000',
#         'region': 'USA',
#         'code': 'your_expression_here'
#     }]
# ============================================================

from commands import (
    daily_batch,
    all_alphas,
    archetype_a_fundamental_yield,
    archetype_b_fundamental_volume,
    archetype_c_conditional_reversion,
    archetype_d_cross_sectional_quality,
    archetype_e_volatility_regime,
    archetype_f_analyst_estimates,
)

# ── Change this line to switch modes ──────────────────────
DATA = daily_batch()
# DATA = all_alphas()
# DATA = archetype_c_conditional_reversion()
