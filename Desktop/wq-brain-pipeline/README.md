# WQ Brain Alpha Pipeline

An automated alpha generation, simulation, and submission pipeline for [WorldQuant Brain](https://www.worldquant.com/brain/).

Built as a university research project exploring systematic approaches to quantitative alpha discovery using diverse datasets, strategy archetypes, and structural diversity tracking.

## Overview

This pipeline automates the full alpha research lifecycle:

1. **Generate** — AI-assisted candidate generation across 12 strategy archetypes using Claude API
2. **Validate** — Syntax and field validation against official Brain operators and data fields
3. **Simulate** — Batch simulation via Brain API with concurrent execution
4. **Scrape** — Fetch passing alphas from your Brain account
5. **Submit** — Auto-submit best candidates sorted by Sharpe ratio

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Alpha Candidate Generator (generator.py)         │
│  12 archetypes × 5 expressions = 60 candidates   │
│  Web research → Batch synthesis → Diversity check │
└──────────────────┬───────────────────────────────┘
                   │ candidates/YYYY-MM-DD.json
                   ▼
┌──────────────────────────────────────────────────┐
│  Batch Simulator (main.py)                        │
│  Concurrent simulation via Brain API              │
│  Results → data/results_*.csv                     │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│  Scraper + Submitter                              │
│  scrape_alphas.py → submit_alphas.py              │
│  Auto-submit highest Sharpe passing alphas        │
└──────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/wq-brain-pipeline.git
cd wq-brain-pipeline
pip install -r requirements.txt

# 2. Configure credentials
cp credentials.json.example credentials.json
# Edit credentials.json with your Brain email and password

# 3. Set Claude API key (for alpha generation)
cp .env.example .env
# Edit .env with your Anthropic API key

# 4. Fetch Brain data fields (one-time setup)
python fetch_fields.py

# 5. Generate candidates
python run_daily.py

# 6. Simulate batch
python main.py

# 7. Check results
ls data/results_*.csv
```

## Project Structure

| File | Purpose |
|------|---------|
| `run_daily.py` | Entry point for daily alpha generation |
| `generator.py` | Async batch engine (Claude API) |
| `diversity.py` | Fingerprint-based originality tracking |
| `brain_data.py` | Complete operator + data field reference |
| `fetch_fields.py` | Download all Brain fields to local CSV |
| `commands.py` | Curated alpha library (10 archetypes) |
| `database.py` | Confirmed fields & submission tracking |
| `main.py` | Brain batch simulator |
| `scrape_alphas.py` | Fetch passing alphas from Brain |
| `submit_alphas.py` | Auto-submit best candidates |
| `test_pipeline.py` | Validation suite |
| `config.py` | All configuration settings |

## Strategy Archetypes

The generator produces candidates across 12 research-backed archetypes:

| Archetype | Data Domain | Theory |
|-----------|-------------|--------|
| Fundamental Yield | Accounting ratios | Lakonishok (1994) value premium |
| Mean Reversion | Price/volume | Short-term overreaction reversal |
| News & Sentiment | News/social | Information diffusion (Tetlock 2007) |
| Implied Volatility | Options | Variance risk premium |
| Analyst Estimates | Analyst consensus | Revision underreaction (Chan 1996) |
| Relationship Returns | Supply chain | Economic links (Cohen & Frazzini 2008) |
| Factor Model Composites | Pre-built scores | Multi-factor orthogonality |
| Volatility Regime | Realized vol/risk | Low-vol anomaly (Baker 2011) |
| Balance Sheet Quality | Leverage/accruals | Accruals anomaly (Sloan 1996) |
| Intraday & Volume | OHLCV patterns | Informed trading detection |
| Social Media Alpha | Social sentiment | Attention-driven trading (Da et al. 2015) |
| Cross-Sectional Strength | Within-group ranks | Industry momentum (Moskowitz 1999) |

## Diversity System

Every generated expression is fingerprinted by:
- Operators used (time-series vs cross-sectional vs group)
- Data domains (price / fundamental / analyst / news / sentiment / options)
- Time horizons (short ≤10d / medium 20-60d / long ≥120d)
- Specific fields used

New candidates are rejected if structural similarity to any recent alpha exceeds 75%. Fingerprints persist across runs in `data/fingerprints.json`.

## Simulation Settings Guide

| Signal Type | Neutralization | Decay | Truncation |
|-------------|---------------|-------|------------|
| Fundamental | SUBINDUSTRY | 5 | 0.08 |
| Price/Volume | NONE | 0-2 | 0.08 |
| News/Sentiment | MARKET | 0 | 0.08 |
| Options/Vol | MARKET | 0-2 | 0.08 |

## Submission Thresholds

Alphas must pass all Brain checks:
- Sharpe ≥ 1.25
- Fitness ≥ 1.0
- Turnover: 1%–70%
- Weight Concentration: PASS
- Sub-universe Sharpe: PASS

## Configuration

Edit `config.py` to tune:

```python
candidates_per_day = 60        # total candidates per run
batch_size = 5                 # expressions per archetype
claude_model = "claude-sonnet-4-5-20251101"
use_web_research = True        # Claude searches for papers
min_diversity_score = 0.25     # originality threshold
max_concurrent_batches = 6     # parallel API calls
```

## Disclaimer

- This project is for **educational and research purposes only**
- No actual alpha expressions or proprietary trading signals are included
- Users must comply with [WorldQuant Brain Terms of Use](https://www.worldquant.com/brain/)
- The pipeline generates *candidates* — actual performance depends on market conditions
- No investment advice is provided or implied
- Brain data fields and operator names are referenced from publicly available documentation

## License

MIT — see [LICENSE](LICENSE)
