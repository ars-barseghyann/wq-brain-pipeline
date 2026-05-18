# ============================================================
#  submit_alphas.py  —  submit best alpha from scraped CSV
#
#  Usage:
#    python submit_alphas.py data/scraped_TIMESTAMP.csv
#
#  Sorts by Sharpe descending, tries each until one passes
#  the self-correlation check on submission.
# ============================================================

from main import WQSession
import time, logging, sys
import pandas as pd

def submit(wq, row):
    aid = row['link'].split('/')[-1]
    wq.post(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
    logging.info(f'Submitting: https://platform.worldquantbrain.com/alpha/{aid}')

    for _ in range(60):   # up to 5 min
        r = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
        if r.status_code == 404:
            logging.info('Already submitted (404).')
            return False
        if r.content:
            checks = r.json().get('is', {}).get('checks', [])
            corr_check = next((c for c in checks if c['name'] == 'SELF_CORRELATION'), None)
            if corr_check:
                result = corr_check['result']
                logging.info(f'Correlation check: {result} — {corr_check}')
                return result == 'PASS'
        time.sleep(5)

    logging.warning('Timed out waiting for submission result.')
    return False

if len(sys.argv) < 2:
    print('Usage: python submit_alphas.py data/scraped_TIMESTAMP.csv')
    sys.exit(1)

wq = WQSession()
ts = int(time.time())
for h in logging.root.handlers:
    logging.root.removeHandler(h)
logging.basicConfig(
    encoding='utf-8', level=logging.INFO,
    format='%(asctime)s: %(message)s',
    filename=f'data/submit_{ts}.log'
)

df = pd.read_csv(sys.argv[1]).sort_values('sharpe', ascending=False)
print(f'Trying {len(df)} candidates sorted by Sharpe...')

for _, row in df.iterrows():
    print(f'  → Sharpe={row["sharpe"]:.2f} | {row["code"][:60]}')
    ok = submit(wq, row)
    if ok:
        print(f'\n✓ SUBMITTED SUCCESSFULLY: {row["link"]}')
        break
    else:
        print(f'  ✗ Failed correlation check, trying next...')
else:
    print('\n✗ No alpha passed submission. Check self-correlation with your portfolio.')
