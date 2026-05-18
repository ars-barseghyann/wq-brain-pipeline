# ============================================================
#  main.py  —  WQ Brain batch simulator  (improved version)
#
#  Changes from original:
#    • CSV includes archetype tag for easy sorting
#    • Pass/fail summary printed at the end
#    • Handles biometric auth prompt cleanly
#    • Retry logic is cleaner (no silent infinite loops)
#    • Login expiry detected and exits gracefully
# ============================================================

import csv
import logging
import requests
import json
import time
from parameters import DATA
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

MAX_WORKERS = 5   # Brain allows ~3 concurrent — 5 threads share that headroom safely

class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            encoding='utf-8', level=logging.INFO,
            format='%(asctime)s [%(levelname)s]: %(message)s'
        )
        self.json_fn = json_fn
        self.login()
        # Wrap get/post with a single retry on network error
        _get, _post = self.get, self.post
        def safe_get(*a, **kw):
            try:    return _get(*a, **kw)
            except: return _get(*a, **kw)
        def safe_post(*a, **kw):
            try:    return _post(*a, **kw)
            except: return _post(*a, **kw)
        self.get, self.post = safe_get, safe_post
        self.login_expired  = False
        self.rows_processed = []
        self.pass_count     = 0
        self.fail_count     = 0

    def login(self):
        with open(self.json_fn, 'r') as f:
            creds = json.loads(f.read())
        self.auth = (creds['email'], creds['password'])
        r = self.post('https://api.worldquantbrain.com/authentication')
        rj = r.json()
        if 'user' not in rj:
            if 'inquiry' in rj:
                url = f"{r.url}/persona?inquiry={rj['inquiry']}"
                input(f"\n⚠  Biometric required. Open this URL:\n   {url}\nPress Enter when done...")
                self.post(f"{r.url}/persona", json=rj)
            else:
                print(f'⚠  Login problem: {rj}')
                raise SystemExit('Fix credentials.json and retry.')
        logging.info('✓ Logged in to WQBrain')

    def simulate(self, data):
        self.rows_processed = []

        def run_one(writer, f, sim):
            if self.login_expired:
                return
            thread  = current_thread().name
            alpha   = sim['code'].strip()
            delay   = sim.get('delay', 1)
            universe= sim.get('universe', 'TOP3000')
            trunc   = sim.get('truncation', 0.08)
            region  = sim.get('region', 'USA')
            decay   = sim.get('decay', 5)
            neut    = sim.get('neutralization', 'SUBINDUSTRY').upper()
            past    = sim.get('pasteurization', 'ON')
            nan     = sim.get('nanHandling', 'OFF')
            logging.info(f'{thread} → Simulating: {alpha[:60]}...')

            # ── POST simulation request ─────────────────────
            nxt = None
            for attempt in range(3):
                try:
                    r = self.post('https://api.worldquantbrain.com/simulations', json={
                        'regular': alpha,
                        'type': 'REGULAR',
                        'settings': {
                            'nanHandling': nan,
                            'instrumentType': 'EQUITY',
                            'delay': delay,
                            'universe': universe,
                            'truncation': trunc,
                            'unitHandling': 'VERIFY',
                            'pasteurization': past,
                            'region': region,
                            'language': 'FASTEXPR',
                            'decay': decay,
                            'neutralization': neut,
                            'visualization': False,
                        }
                    })
                    if 'credentials' in r.text:
                        self.login_expired = True
                        logging.warning('Session expired — re-run script.')
                        return
                    nxt = r.headers.get('Location')
                    if nxt:
                        break
                except Exception as e:
                    logging.warning(f'{thread} attempt {attempt+1} failed: {e}')
                    time.sleep(5)

            if not nxt:
                logging.error(f'{thread} ✗ Could not start simulation for: {alpha[:60]}')
                return

            logging.info(f'{thread} ⏳ Polling: {nxt}')

            # ── Poll until complete ─────────────────────────
            alpha_link = None
            fail_msg   = None
            for _ in range(120):     # up to 20 min
                r = self.get(nxt).json()
                if 'alpha' in r:
                    alpha_link = r['alpha']
                    break
                if 'message' in r and 'progress' not in r:
                    fail_msg = r.get('message', 'unknown error')
                    break
                pct = int(100 * r.get('progress', 0))
                logging.info(f'{thread} {pct}%')
                time.sleep(10)

            # ── Build result row ────────────────────────────
            if not alpha_link:
                row = [0, delay, region, neut, decay, trunc,
                       0, 0, 0, 'FAIL', -1, -1, universe,
                       'N/A', alpha, fail_msg or 'timeout']
                self.fail_count += 1
            else:
                r = self.get(f'https://api.worldquantbrain.com/alphas/{alpha_link}').json()
                url = f'https://platform.worldquantbrain.com/alpha/{alpha_link}'
                logging.info(f'{thread} ✓ {url}')

                is_data = r.get('is', {})
                checks  = is_data.get('checks', [])
                passed  = sum(c['result'] == 'PASS' for c in checks)
                weight_check = next((c['result'] for c in checks if c['name'] == 'CONCENTRATED_WEIGHT'), 'N/A')
                subsharpe    = next((c['value']  for c in checks if c['name'] == 'LOW_SUB_UNIVERSE_SHARPE'), -1)

                sharpe  = is_data.get('sharpe', 0)
                fitness = is_data.get('fitness', 0)
                turnover= round(100 * is_data.get('turnover', 0), 2)
                submittable = '✓ PASS' if passed == len(checks) and len(checks) > 0 else f'FAIL ({passed}/{len(checks)})'

                row = [passed, delay, region, neut, decay, trunc,
                       sharpe, fitness, turnover, weight_check,
                       subsharpe, -1, universe, url, alpha, submittable]

                if passed == len(checks) and len(checks) > 0:
                    self.pass_count += 1
                    logging.info(f'{thread} 🎯 SUBMITTABLE — Sharpe={sharpe:.2f} Fitness={fitness:.2f} TO={turnover}%')
                else:
                    self.fail_count += 1

            writer.writerow(row)
            f.flush()
            self.rows_processed.append(sim)

        # ── Set up CSV output ───────────────────────────────
        try:
            import os
            os.makedirs('data', exist_ok=True)
            for h in logging.root.handlers:
                logging.root.removeHandler(h)
            ts      = str(time.time()).replace('.', '_')
            csv_f   = f'data/results_{ts}.csv'
            log_f   = csv_f.replace('.csv', '.log')
            logging.basicConfig(
                encoding='utf-8', level=logging.INFO,
                format='%(asctime)s: %(message)s', filename=log_f
            )
            logging.info(f'Output: {csv_f}')
            with open(csv_f, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'passed', 'delay', 'region', 'neutralization', 'decay', 'truncation',
                    'sharpe', 'fitness', 'turnover', 'weight', 'subsharpe', 'correlation',
                    'universe', 'link', 'code', 'status'
                ])
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
                    ex.map(lambda s: run_one(writer, f, s), data)
        except Exception as e:
            print(f'Error: {type(e).__name__}: {e}')

        return [s for s in data if s not in self.rows_processed]


if __name__ == '__main__':
    total = len(DATA)
    remaining = list(DATA)
    while remaining:
        wq = WQSession()
        done = total - len(remaining)
        print(f'\n── Progress: {done}/{total} simulations done ──')
        remaining = wq.simulate(remaining)
        if remaining and wq.login_expired:
            print('Session expired. Re-running with fresh login...')
            time.sleep(5)
        elif not remaining:
            break

    print(f'\n══════════════════════════════════')
    print(f'  DONE — {total} alphas simulated')
    print(f'  ✓ Submittable : {wq.pass_count}')
    print(f'  ✗ Failed      : {wq.fail_count}')
    print(f'  Results saved in data/ folder')
    print(f'══════════════════════════════════')
