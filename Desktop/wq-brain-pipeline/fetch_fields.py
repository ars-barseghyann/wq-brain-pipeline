#!/usr/bin/env python3
"""
fetch_fields.py — Download all available data fields from WorldQuant Brain.

Usage:
    python fetch_fields.py

Output:
    data/fields.csv  — all fields with id, description, category, coverage, etc.

Run this once after cloning the repo to populate your local field database.
The CSV is .gitignored to avoid committing proprietary Brain data.
"""

import csv
import json
import os
import time
from main import WQSession

FIELDS_URL = 'https://api.worldquantbrain.com/data-fields'
LIMIT = 50  # per page
OUTPUT = 'data/fields.csv'


def fetch_all_fields(wq):
    """Paginate through all Brain data fields."""
    all_fields = []
    offset = 0

    # First request to get total count
    r = wq.get(f'{FIELDS_URL}?limit={LIMIT}&offset=0&instrumentType=EQUITY')
    rj = r.json()
    total = rj.get('count', 0)
    results = rj.get('results', [])
    all_fields.extend(results)
    print(f'Found {total} total fields. Fetching...')

    while len(all_fields) < total:
        offset += LIMIT
        r = wq.get(f'{FIELDS_URL}?limit={LIMIT}&offset={offset}&instrumentType=EQUITY')
        rj = r.json()
        batch = rj.get('results', [])
        if not batch:
            break
        all_fields.extend(batch)
        pct = min(100, int(100 * len(all_fields) / total))
        print(f'  {pct}% ({len(all_fields)}/{total})')
        time.sleep(0.5)  # be polite to the API

    return all_fields


def save_csv(fields, output_path):
    """Save fields to CSV."""
    if not fields:
        print('No fields to save.')
        return

    # Determine columns from first record
    columns = ['id', 'description', 'category', 'subcategory', 'dataset',
               'dataset_id', 'type', 'coverage', 'dateCoverage',
               'userCount', 'alphaCount', 'themes']

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for field in fields:
            row = {}
            for col in columns:
                val = field.get(col, '')
                # Flatten nested objects if needed
                if isinstance(val, dict):
                    val = json.dumps(val)
                elif isinstance(val, list):
                    val = json.dumps(val)
                row[col] = val
            writer.writerow(row)

    print(f'\n✓ Saved {len(fields)} fields to {output_path}')


def print_summary(fields):
    """Print dataset coverage summary."""
    datasets = {}
    for f in fields:
        ds = f.get('dataset', 'unknown')
        datasets[ds] = datasets.get(ds, 0) + 1

    print(f'\n{"─" * 50}')
    print('DATASET SUMMARY')
    print(f'{"─" * 50}')
    for ds, count in sorted(datasets.items(), key=lambda x: -x[1]):
        bar = '█' * min(50, count // 10)
        print(f'  {ds:<40} {count:>5}  {bar}')
    print(f'\n  Total: {len(fields)} fields')


if __name__ == '__main__':
    print('Logging in to WorldQuant Brain...')
    wq = WQSession()

    print('Fetching data fields...')
    fields = fetch_all_fields(wq)

    save_csv(fields, OUTPUT)
    print_summary(fields)

    print(f'\nTo use with test_pipeline.py, rename:')
    print(f'  mv {OUTPUT} fields.csv')
    print(f'  (or update the csv_path in test_pipeline.py)')
