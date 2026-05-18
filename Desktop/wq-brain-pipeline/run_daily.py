"""
run_daily.py — entry point for the alpha candidate generator.

Usage:
    python run_daily.py                     # generate 60 candidates
    python run_daily.py --count 30          # generate 30 candidates
    python run_daily.py --count 60 --no-research   # skip web search (faster)
    python run_daily.py --validate-only     # just check existing JSON for syntax

Output:
    candidates/YYYY-MM-DD.json     ← feed this to your simulation pipeline
    candidates/YYYY-MM-DD.txt      ← plain expressions, one per line (optional)
    logs/YYYY-MM-DD_HH-MM.log
"""

import asyncio
import argparse
import json
import logging
import sys
import time
from datetime import date, datetime
from pathlib import Path

from config import cfg
from diversity import DiversityTracker
from generator import BatchAlphaGenerator, _quick_validate


# ─────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────

def setup_logging():
    Path(cfg.logs_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(cfg.logs_dir) / f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file),
        ]
    )


# ─────────────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────────────

def save_candidates(candidates, count_requested: int) -> Path:
    """
    Save candidates to dated JSON file.
    Format:
    {
      "date": "2026-05-02",
      "count": 60,
      "candidates": [
        {
          "id": "alpha_2026-05-02_001",
          "expression": "rank(ts_ir(returns, 20) ...)",
          "archetype": "Quality",
          "rationale": "...",
          "diversity_score": 0.87,
          "generation_stage": "research_backed"
        },
        ...
      ]
    }
    """
    Path(cfg.candidates_dir).mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = Path(cfg.candidates_dir) / f"{today}.json"

    output = {
        "date": today,
        "requested": count_requested,
        "generated": len(candidates),
        "candidates": []
    }

    for i, c in enumerate(candidates, 1):
        c.candidate_id = f"alpha_{today}_{i:03d}"
        c.date = today
        output["candidates"].append({
            "id": c.candidate_id,
            "expression": c.expression,
            "archetype": c.archetype,
            "rationale": c.rationale,
            "diversity_score": round(c.diversity_score, 4),
            "generation_stage": c.generation_stage,
        })

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    # Also write a plain .txt (one expression per line) for easy piping
    txt_path = Path(cfg.candidates_dir) / f"{today}.txt"
    with open(txt_path, "w") as f:
        for c in candidates:
            f.write(c.expression + "\n")

    return out_path


# ─────────────────────────────────────────────────────────────────────────
# VALIDATE-ONLY MODE
# ─────────────────────────────────────────────────────────────────────────

def validate_json(path: Path) -> None:
    """Read an existing candidates JSON and re-validate all expressions."""
    with open(path) as f:
        data = json.load(f)

    candidates = data.get("candidates", [])
    print(f"\nValidating {len(candidates)} expressions from {path}\n")
    passed = 0
    for c in candidates:
        expr = c.get("expression", "")
        ok = _quick_validate(expr)
        status = "✅" if ok else "❌"
        print(f"  {status}  [{c.get('archetype', '?')}]  {expr[:75]}")
        if ok:
            passed += 1

    print(f"\n{passed}/{len(candidates)} passed validation")


# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

async def main(count: int, no_research: bool):
    setup_logging()
    logger = logging.getLogger("run_daily")

    # Config override
    if no_research:
        cfg.use_web_research = False

    try:
        cfg.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("=" * 60)
    logger.info(f"  ALPHA CANDIDATE GENERATOR  |  target: {count}")
    logger.info(f"  date: {date.today()}  |  model: {cfg.claude_model}")
    logger.info(f"  web_research: {cfg.use_web_research}  |  "
                f"concurrency: {cfg.max_concurrent_batches}")
    logger.info("=" * 60)

    tracker = DiversityTracker()
    coverage = tracker.coverage_summary()
    logger.info(f"Existing fingerprints: {coverage['total']} alphas tracked")

    generator = BatchAlphaGenerator(tracker)

    t0 = time.time()
    candidates = await generator.generate_all(target=count)
    elapsed = time.time() - t0

    if not candidates:
        logger.error("Zero candidates generated. Check API key and logs.")
        sys.exit(1)

    # Register all accepted candidates in the diversity tracker
    for c in candidates:
        tracker.add(c.expression, c.archetype)

    # Save output
    out_path = save_candidates(candidates, count)

    # Print summary
    archetypes_used = {}
    for c in candidates:
        archetypes_used[c.archetype] = archetypes_used.get(c.archetype, 0) + 1

    print("\n" + "=" * 60)
    print(f"  Generated {len(candidates)}/{count} candidates in {elapsed:.0f}s")
    print(f"  Output: {out_path}")
    print()
    print(f"  {'Archetype':<35} {'Count':>5}  {'Avg Diversity':>14}")
    print(f"  {'-'*35} {'-'*5}  {'-'*14}")

    by_arch: dict = {}
    for c in candidates:
        if c.archetype not in by_arch:
            by_arch[c.archetype] = []
        by_arch[c.archetype].append(c.diversity_score)

    for arch, scores in sorted(by_arch.items(), key=lambda x: -len(x[1])):
        avg = sum(scores) / len(scores)
        print(f"  {arch:<35} {len(scores):>5}  {avg:>13.2f}")

    print()
    avg_div = sum(c.diversity_score for c in candidates) / len(candidates)
    high_div = [c for c in candidates if c.diversity_score >= 0.70]
    print(f"  Average diversity score : {avg_div:.3f}")
    print(f"  High-diversity (≥0.70)  : {len(high_div)}/{len(candidates)}")
    print(f"  Research-backed         : {sum(1 for c in candidates if c.generation_stage == 'research_backed')}/{len(candidates)}")
    print("=" * 60 + "\n")

    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alpha Candidate Generator")
    parser.add_argument("--count",   type=int,  default=cfg.candidates_per_day,
                        help=f"Number of candidates to generate (default: {cfg.candidates_per_day})")
    parser.add_argument("--no-research", action="store_true",
                        help="Skip web research calls (faster, cheaper, less grounded)")
    parser.add_argument("--validate-only", type=str, metavar="PATH",
                        help="Validate expressions in an existing candidates JSON file")
    args = parser.parse_args()

    if args.validate_only:
        validate_json(Path(args.validate_only))
        sys.exit(0)

    asyncio.run(main(count=args.count, no_research=args.no_research))
