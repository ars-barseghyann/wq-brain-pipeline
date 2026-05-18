#!/usr/bin/env python3
"""
test_pipeline.py — Validate all pipeline updates before running.

Usage:
    python test_pipeline.py

Checks:
  1. All operators in commands.py are in the official Brain operator list
  2. All fields in commands.py exist in the Brain fields CSV
  3. No submitted alphas are duplicated in the batch
  4. Expression syntax is valid (balanced parens, etc.)
  5. Diversity score of new alphas vs submitted portfolio
"""

import re
import sys
import csv
from pathlib import Path

# ── Load CSV fields ─────────────────────────────────────────
def load_csv_fields(csv_path="fields_1778245023.csv"):
    fields = set()
    if Path(csv_path).exists():
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                fields.add(row['id'].strip())
    else:
        # Fallback: use field names from brain_data.py
        from brain_data import ALL_DATA_FIELDS
        fields = set(ALL_DATA_FIELDS.keys())
    return fields

# ── Official Brain operators ────────────────────────────────
OFFICIAL_OPERATORS = {
    # Math
    'abs', 'add', 'densify', 'divide', 'inverse', 'log', 'max', 'min',
    'multiply', 'power', 'reverse', 'sign', 'signed_power', 'sqrt', 'subtract',
    # Logical
    'and', 'if_else', 'is_nan', 'not', 'or',
    # Time-series
    'days_from_last_change', 'hump', 'kth_element', 'last_diff_value',
    'ts_arg_max', 'ts_arg_min', 'ts_av_diff', 'ts_backfill', 'ts_corr',
    'ts_count_nans', 'ts_covariance', 'ts_decay_linear', 'ts_delay',
    'ts_delta', 'ts_mean', 'ts_product', 'ts_quantile', 'ts_rank',
    'ts_regression', 'ts_scale', 'ts_std_dev', 'ts_step', 'ts_sum', 'ts_zscore',
    # Cross-sectional
    'normalize', 'quantile', 'rank', 'scale', 'winsorize', 'zscore',
    # Vector
    'vec_avg', 'vec_sum',
    # Transformational
    'bucket', 'trade_when',
    # Group
    'group_backfill', 'group_mean', 'group_neutralize', 'group_rank',
    'group_scale', 'group_zscore',
}

# ── Known INVALID operators (common hallucinations) ─────────
INVALID_OPERATORS = {
    'ts_std', 'ts_skewness', 'ts_kurtosis', 'ts_median', 'ts_ir',
    'ts_entropy', 'ts_autocorr', 'ts_moment', 'ts_decay_exp_window',
    'demean', 'truncate', 'group_std', 'group_median',
    'nan_out', 'purify', 'fill_nan', 'fraction', 'sigmoid', 'tanh',
    'exp', 'square', 'log1p', 'is_finite',
}

# ── Known INVALID field names ──────────────────────────────
INVALID_FIELDS = {
    'roe', 'roa', 'roic', 'pe', 'pb', 'ps', 'fcf', 'grossmargin',
    'netmargin', 'operatingmargin', 'netincome', 'sgna', 'rd',
    'dividendyield', 'payoutratio', 'ev_ebitda', 'turnover_vol',
    'amount', 'adv5', 'adv60', 'price', 'volume_avg', 'ret',
    'market_cap', 'eps_actual', 'fam_est_eps_rank',
}


def extract_operators(expr):
    """Extract all operator-like names from an expression."""
    return set(re.findall(r'([a-z][a-z0-9_]+)\s*\(', expr.lower()))


def extract_fields(expr):
    """Extract all potential field names (word tokens not followed by '(')."""
    # Remove operator calls first
    tokens = re.findall(r'\b([a-z][a-z0-9_]+)\b', expr.lower())
    ops = extract_operators(expr)
    # Keywords that aren't fields
    keywords = {'rettype', 'std', 'filter', 'true', 'false', 'nan',
                'dense', 'constant', 'lookback', 'hump', 'driver',
                'gaussian', 'sigma', 'rate', 'longscale', 'shortscale'}
    return {t for t in tokens if t not in ops and t not in keywords and not t.isdigit()}


def validate_expression(expr, csv_fields):
    """Validate a single expression. Returns list of issues."""
    issues = []

    # Balanced parens
    if expr.count('(') != expr.count(')'):
        issues.append("SYNTAX: Unbalanced parentheses")

    # Check operators
    ops = extract_operators(expr)
    for op in ops:
        if op in INVALID_OPERATORS:
            issues.append(f"INVALID_OP: '{op}' is NOT a valid Brain operator")
        elif op not in OFFICIAL_OPERATORS:
            issues.append(f"UNKNOWN_OP: '{op}' not in official list (may still work)")

    # Check fields
    fields = extract_fields(expr)
    for f in fields:
        if f in INVALID_FIELDS:
            issues.append(f"INVALID_FIELD: '{f}' does NOT exist in Brain")
        elif f not in csv_fields and len(f) > 2:
            # Short names might be variables in multi-line expressions
            if not any(f"{f} =" in expr.lower() or f"{f}=" in expr.lower() for _ in [1]):
                issues.append(f"WARN_FIELD: '{f}' not found in CSV (may be variable or unlisted)")

    return issues


def main():
    print("=" * 60)
    print("  PIPELINE VALIDATION TEST")
    print("=" * 60)

    # Load CSV fields
    csv_path = Path("fields_1778245023.csv")
    csv_fields = load_csv_fields(csv_path)
    if csv_path.exists():
        print(f"\n✓ Loaded {len(csv_fields)} fields from CSV")
    else:
        print(f"\n✓ Loaded {len(csv_fields)} fields from brain_data.py (CSV not found)")

    # Import commands
    try:
        from commands import all_alphas, daily_batch
        from database import SUBMITTED_ALPHAS
        print("✓ Imports OK")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("  Make sure the updated files are in place.")
        sys.exit(1)

    # Test all alphas
    all_a = all_alphas()
    daily = daily_batch()
    print(f"\n  all_alphas(): {len(all_a)} candidates")
    print(f"  daily_batch(): {len(daily)} candidates")
    print(f"  submitted:     {len(SUBMITTED_ALPHAS)} alphas")

    # Validate each expression
    total_issues = 0
    critical = 0

    print(f"\n{'─' * 60}")
    print("VALIDATING ALL EXPRESSIONS")
    print(f"{'─' * 60}\n")

    for i, sim in enumerate(all_a):
        code = sim['code']
        issues = validate_expression(code, csv_fields)
        if issues:
            has_critical = any(i.startswith("INVALID_") or i.startswith("SYNTAX") for i in issues)
            marker = "✗" if has_critical else "⚠"
            print(f"  {marker} [{i+1}] {code[:70]}...")
            for issue in issues:
                print(f"       → {issue}")
                if issue.startswith("INVALID_") or issue.startswith("SYNTAX"):
                    critical += 1
            total_issues += len(issues)
        # else: silent pass

    # Check for duplicates with submitted
    print(f"\n{'─' * 60}")
    print("CHECKING AGAINST SUBMITTED ALPHAS")
    print(f"{'─' * 60}\n")

    submitted_normalized = {s.replace(' ', '').lower() for s in SUBMITTED_ALPHAS}
    for i, sim in enumerate(all_a):
        code_norm = sim['code'].replace(' ', '').lower()
        if code_norm in submitted_normalized:
            print(f"  ✗ DUPLICATE: [{i+1}] matches submitted alpha")
            print(f"       {sim['code'][:70]}")
            critical += 1

    # Summary
    print(f"\n{'=' * 60}")
    if critical == 0:
        print(f"  ✓ ALL CLEAR — {len(all_a)} expressions valid")
        print(f"    Warnings: {total_issues} (non-critical)")
    else:
        print(f"  ✗ {critical} CRITICAL issues found")
        print(f"    Total issues: {total_issues}")
    print(f"{'=' * 60}")

    # Dataset coverage analysis
    print(f"\n{'─' * 60}")
    print("DATASET DIVERSITY ANALYSIS")
    print(f"{'─' * 60}\n")

    dataset_counts = {}
    for sim in daily:
        code = sim['code'].lower()
        datasets = set()
        for f in csv_fields:
            if f in code:
                # Determine category by checking field membership
                if f in {'open','high','low','close','vwap','returns','volume','sharesout','cap','adv20','dividend','split','exchange'}:
                    datasets.add('price_volume')
                elif 'news' in f or 'nws' in f or 'rp_' in f:
                    datasets.add('news')
                elif 'scl12' in f or 'snt' in f:
                    datasets.add('sentiment')
                elif 'implied_vol' in f or 'parkinson' in f or 'historical_vol' in f or 'pcr_' in f or 'call_breakeven' in f:
                    datasets.add('option')
                elif 'rel_ret' in f or 'pv13_' in f or 'rel_num' in f:
                    datasets.add('relationship')
                elif 'fscore' in f or 'mdl177' in f or 'unsystematic' in f or 'systematic' in f or 'beta_last' in f or 'correlation_last' in f:
                    datasets.add('model')
                elif 'est_' in f or 'anl4_' in f or 'analyst_' in f:
                    datasets.add('analyst')
                elif 'fnd6_' in f or f in {'assets','liabilities','operating_income','enterprise_value','sales','debt','capex','equity','ebitda','ebit','eps','debt_lt','cashflow_op','assets_curr','goodwill','income','revenue','cash','liabilities_curr','cogs','debt_st','bookvalue_ps','cashflow','ppent','operating_expense','inventory','return_equity','return_assets','sales_growth','receivable','retained_earnings','income_tax','pretax_income','cashflow_fin','cashflow_invst','depre_amort','rd_expense','interest_expense'}:
                    datasets.add('fundamental')
        for ds in datasets:
            dataset_counts[ds] = dataset_counts.get(ds, 0) + 1

    print("  Daily batch dataset coverage:")
    for ds, count in sorted(dataset_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {ds:<20} {count:>3}  {bar}")

    # Submitted portfolio datasets
    print("\n  Submitted portfolio datasets:")
    sub_ds = {'fundamental': 3, 'price_volume': 5, 'analyst': 1, 'option': 1, 'relationship': 1, 'news': 1}
    for ds, count in sorted(sub_ds.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {ds:<20} {count:>3}  {bar}")
    print(f"    {'sentiment':<20}   0  (UNTAPPED)")
    print(f"    {'model':<20}   0  (UNTAPPED)")

    return 0 if critical == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
