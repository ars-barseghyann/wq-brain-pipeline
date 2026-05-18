# ============================================================
#  scrape_alphas.py  —  fetch unsubmitted passing alphas
#
#  Run this to pull all alphas from your Brain account that
#  already pass IS thresholds, then pipe into submit_alphas.py
#
#  Usage:
#    python scrape_alphas.py
#    → writes data/scraped_TIMESTAMP.csv
# ============================================================

from main import WQSession
import time, logging, csv, json
import pandas as pd
from concurrent.futures import as_completed, ThreadPoolExecutor
from threading import current_thread

OFFSET, LIMIT = 0, 30

def get_link(x):
    return (
        f'https://api.worldquantbrain.com/users/self/alphas'
        f'?limit={LIMIT}&offset={x}'
        f'&stage=IS%1fOS'
        f'&is.sharpe%3E=1.25'
        f'&is.turnover%3E=0.01'
        f'&is.fitness%3E=1'
        f'&status=UNSUBMITTED'
        f'&order=-dateCreated'
        f'&hidden=false'
    )

wq = WQSession()

# ── Fetch total count ───────────────────────────────────────
r = wq.get(get_link(0)).json()
total = r.get('count', 0)
print(f'Found {total} unsubmitted passing alphas.')

offsets = list(range(0, total, LIMIT))

def scrape(result):
    thread = current_thread().name
    alpha  = result['regular']['code']
    settings = result['settings']
    aid    = result['id']
    checks = result['is']['checks']

    if any(c['result'] in ('FAIL', 'ERROR') for c in checks):
        return None

    # Full check via API
    while True:
        cr = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/check')
        if cr.content:
            try:
                full_checks = cr.json()['is']['checks']
                break
            except:
                pass
        time.sleep(2.5)

    if not all(c['result'] == 'PASS' for c in full_checks):
        return None

    max_corr = next((c['value'] for c in full_checks if c['name'] == 'SELF_CORRELATION'), -1)

    row = {
        'id': aid,
        'code': alpha,
        'sharpe': result['is']['sharpe'],
        'fitness': result['is']['fitness'],
        'turnover': round(100 * result['is']['turnover'], 2),
        'self_correlation': max_corr,
        'universe': settings.get('universe'),
        'neutralization': settings.get('neutralization'),
        'decay': settings.get('decay'),
        'link': f'https://platform.worldquantbrain.com/alpha/{aid}',
        'before': -1,
        'after': -1,
    }
    logging.info(f'{thread} scraped: {aid} sharpe={row["sharpe"]:.2f} corr={max_corr}')
    return row

rows = []
for offset in offsets:
    batch = wq.get(get_link(offset)).json().get('results', [])
    with ThreadPoolExecutor(max_workers=5) as ex:
        for row in ex.map(scrape, batch):
            if row:
                rows.append(row)

if rows:
    ts = str(int(time.time()))
    out = f'data/scraped_{ts}.csv'
    df = pd.DataFrame(rows).sort_values('sharpe', ascending=False)
    df.to_csv(out, index=False)
    print(f'\n✓ {len(rows)} passing alphas saved to {out}')
    print(df[['sharpe','fitness','turnover','self_correlation','code']].to_string(index=False))
else:
    print('No fully-passing unsubmitted alphas found.')
