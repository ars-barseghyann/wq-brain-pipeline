"""
Async Batch Alpha Generator

Architecture:
  12 archetypes × 5 expressions per batch = 60 candidates
  Per archetype: 1 research call + 1 batch-synthesis call = 2 API calls
  All 12 run concurrently (semaphore-limited to avoid rate limits)
  Total API calls: ~24  |  Wall time: ~2-4 minutes for 60 candidates

Each batch call asks Claude to produce N structurally distinct expressions
at once, with explicit variety constraints (different operators, fields,
time horizons within the same archetype).
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import anthropic

from brain_data import (
    STRATEGY_ARCHETYPES, TS_OPERATORS, CS_OPERATORS, GROUP_OPERATORS,
    TRANSFORM_OPERATORS, MATH_OPERATORS, LOGICAL_OPERATORS,
    format_operators_for_prompt, format_fields_for_prompt,
    ALL_DATA_FIELDS, ALL_OPERATORS,
)
from config import cfg
from diversity import DiversityTracker

logger = logging.getLogger("generator")


@dataclass
class Candidate:
    expression: str
    archetype: str
    rationale: str
    diversity_score: float = 0.0
    generation_stage: str = ""   # research_backed / fallback
    batch_index: int = 0

    # filled by run_daily.py when writing output
    candidate_id: str = ""
    date: str = ""


# ─────────────────────────────────────────────────────────────────────────
# BATCH GENERATOR
# ─────────────────────────────────────────────────────────────────────────

class BatchAlphaGenerator:

    def __init__(self, tracker: DiversityTracker):
        self.client = anthropic.AsyncAnthropic(api_key=cfg.anthropic_api_key)
        self.tracker = tracker
        self._semaphore = asyncio.Semaphore(cfg.max_concurrent_batches)

    async def generate_all(self, target: int = 60) -> list[Candidate]:
        """
        Generate `target` candidates across all archetypes.
        Returns list sorted by diversity score descending.
        """
        # Determine how many batches and which archetypes to use
        batches_needed = -(-target // cfg.batch_size)  # ceiling division
        archetypes_to_use = self._select_archetypes(batches_needed)

        logger.info(f"Starting {len(archetypes_to_use)} async batches "
                    f"(batch_size={cfg.batch_size}, target={target})")

        t0 = time.time()
        tasks = [
            self._generate_batch(arch, i)
            for i, arch in enumerate(archetypes_to_use)
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        candidates = []
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Batch failed: {result}")
                continue
            candidates.extend(result)

        # Deduplicate and score diversity
        candidates = self._deduplicate(candidates)
        for c in candidates:
            c.diversity_score = self.tracker.diversity_score(c.expression)

        # Sort: highest diversity first (most original candidates at the top)
        candidates.sort(key=lambda c: c.diversity_score, reverse=True)

        elapsed = time.time() - t0
        logger.info(f"Generated {len(candidates)} candidates in {elapsed:.1f}s")
        return candidates[:target]

    async def _generate_batch(self, archetype: dict, batch_index: int) -> list[Candidate]:
        """Generate one batch of `batch_size` expressions for one archetype."""
        async with self._semaphore:
            logger.info(f"[Batch {batch_index}] Starting: {archetype['name']}")

            # Stage 1: Research (optional, can be skipped to save calls)
            research = ""
            if cfg.use_web_research and (batch_index % cfg.research_every_n_archetypes == 0):
                research = await self._research_concept(archetype)

            # Stage 2: Batch expression synthesis
            candidates = await self._synthesize_batch(archetype, research, batch_index)

            logger.info(f"[Batch {batch_index}] Done: {len(candidates)} expressions")
            return candidates

    async def _research_concept(self, archetype: dict) -> str:
        """One Claude call to surface a research concept for the archetype."""
        tools = [{"type": "web_search_20250305", "name": "web_search"}] \
            if cfg.use_web_research else []

        prompt = f"""You are a quant researcher. Find ONE specific, recent (2019-2025) academic finding or market anomaly for this strategy type:

Archetype: {archetype['name']}
Theory: {archetype['theory']}

Search for it. Return a 3-sentence summary:
1. The specific paper/anomaly name
2. The economic mechanism  
3. Which data fields it requires (use exact Brain field names from: {', '.join(archetype['primary_fields'])})

Be concrete and cite sources. No generic answers."""

        try:
            resp = await asyncio.wait_for(
                self.client.messages.create(
                    model=cfg.claude_model,
                    max_tokens=400,
                    tools=tools if tools else anthropic.NOT_GIVEN,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=cfg.request_timeout
            )
            return _extract_text(resp).strip()
        except Exception as e:
            logger.warning(f"Research call failed for {archetype['name']}: {e}")
            return ""

    async def _synthesize_batch(
        self,
        archetype: dict,
        research: str,
        batch_index: int,
    ) -> list[Candidate]:
        """
        One Claude call → N structurally distinct expressions for one archetype.
        The key innovation: we explicitly demand variety WITHIN the batch.
        """
        n = cfg.batch_size
        operators_ref = format_operators_for_prompt()
        fields_ref = format_fields_for_prompt("all")
        forbidden = self.tracker.forbidden_patterns_text(n=12)
        coverage = self.tracker.coverage_summary()

        research_block = f"\nResearch concept to draw from:\n{research}\n" if research else ""

        variety_instructions = _variety_constraints(n, archetype)

        prompt = f"""You are a WorldQuant Brain alpha expression writer.
Generate exactly {n} STRUCTURALLY DIFFERENT alpha expressions for this archetype.

ARCHETYPE: {archetype['name']}
Theory: {archetype['theory']}
{research_block}
ALREADY EXISTS (DO NOT REPLICATE THESE STRUCTURES):
{forbidden}

VARIETY REQUIREMENTS — each of the {n} expressions must differ:
{variety_instructions}

VALID OPERATORS ONLY:
{operators_ref}

VALID DATA FIELDS ONLY:
{fields_ref}

SYNTAX RULES:
- Single line, no comments, no assignments, no Python code
- All operator calls need parentheses: ts_rank(x, 20) not ts_rank x 20  
- Balanced parentheses
- Positive = long signal, negative = short signal
- scale() as outer wrapper only when needed for dollar-neutral
- Do NOT use: price, volume_avg, ret, market_cap, eps_actual (these are invalid)

OUTPUT: Respond with a JSON array of exactly {n} objects:
[
  {{"expression": "...", "rationale": "one sentence why it predicts returns"}},
  ...
]

No preamble. No explanation. Only the JSON array."""

        for attempt in range(3):
            try:
                resp = await asyncio.wait_for(
                    self.client.messages.create(
                        model=cfg.claude_model,
                        max_tokens=1200,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=cfg.request_timeout
                )
                text = _extract_text(resp)
                items = _parse_json_array(text)
                if not items:
                    logger.warning(f"[Batch {batch_index}] Attempt {attempt+1}: no JSON parsed")
                    continue

                candidates = []
                for item in items:
                    expr = item.get("expression", "").strip()
                    rationale = item.get("rationale", "")
                    if expr and _quick_validate(expr):
                        candidates.append(Candidate(
                            expression=expr,
                            archetype=archetype["name"],
                            rationale=rationale,
                            generation_stage="research_backed" if research else "archetype_only",
                            batch_index=batch_index,
                        ))
                    else:
                        logger.debug(f"[Batch {batch_index}] Invalid expression skipped: {expr[:60]}")

                if candidates:
                    return candidates

            except asyncio.TimeoutError:
                logger.warning(f"[Batch {batch_index}] Timeout on attempt {attempt+1}")
            except Exception as e:
                logger.error(f"[Batch {batch_index}] Error attempt {attempt+1}: {e}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"[Batch {batch_index}] All attempts failed for {archetype['name']}")
        return []

    def _select_archetypes(self, count: int) -> list[dict]:
        """
        Choose which archetypes to run, prioritizing least-covered ones.
        If count > 12, some archetypes are repeated (with different research).
        """
        coverage = self.tracker.coverage_summary()
        arch_counts = coverage.get("archetypes", {})

        # Sort by least covered
        sorted_archetypes = sorted(
            STRATEGY_ARCHETYPES,
            key=lambda a: arch_counts.get(a["name"], 0)
        )

        # If we need more than 12, cycle through again
        result = []
        while len(result) < count:
            result.extend(sorted_archetypes)
        return result[:count]

    def _deduplicate(self, candidates: list[Candidate]) -> list[Candidate]:
        """Remove exact-duplicate expressions within the batch."""
        seen = set()
        unique = []
        for c in candidates:
            key = c.expression.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique


# ─────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────

def _variety_constraints(n: int, archetype: dict) -> str:
    """Generate explicit variety requirements for within-batch diversity."""
    ops = archetype.get("typical_operators", [])
    fields = archetype.get("primary_fields", [])
    windows = archetype.get("typical_windows", [5, 20, 60])

    lines = []
    if n >= 1:
        lines.append(f"  Expression 1: Use a TIME-SERIES primary operator. Short window (≤10 days).")
    if n >= 2:
        lines.append(f"  Expression 2: Use a CROSS-SECTIONAL primary operator with group neutralization.")
    if n >= 3:
        lines.append(f"  Expression 3: Medium window (20-60 days). Combine two different data fields.")
    if n >= 4:
        lines.append(f"  Expression 4: Long window (≥60 days) OR fundamental/analyst data (not price).")
    if n >= 5:
        lines.append(f"  Expression 5: Most complex (3+ nested operators). Combine price + another domain.")
    for i in range(5, n):
        lines.append(f"  Expression {i+1}: Novel combination — different operator and field from above.")
    return "\n".join(lines)


def _extract_text(response) -> str:
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return " ".join(parts)


def _parse_json_array(text: str) -> Optional[list]:
    """Robustly extract a JSON array from Claude's response."""
    # Try to find array directly
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Strip markdown fences
    clean = re.sub(r'```json|```', '', text).strip()
    try:
        result = json.loads(clean)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    return None


def _quick_validate(expression: str) -> bool:
    """Fast structural validation before accepting an expression."""
    if not expression or len(expression) < 8:
        return False

    # Balanced parens
    if expression.count("(") != expression.count(")"):
        return False

    expr_lower = expression.lower()

    # Must have at least one known operator (check function-call style)
    known_ops = [op.lower() for op in ALL_OPERATORS]
    has_operator = any(op + "(" in expr_lower or op + " " in expr_lower
                       for op in known_ops)
    # Also allow bare arithmetic expressions with field names
    if not has_operator and not any(c in expression for c in ['+', '-', '*', '/']):
        return False

    # Must have at least one known data field
    if not any(f in expr_lower for f in ALL_DATA_FIELDS):
        return False

    # Common INVALID field names that LLMs hallucinate
    bad_fields = [
        r'\bprice\b(?!_)',       # "price" alone (not price_xxx)
        r'\bvolume_avg\b',
        r'\bret\b(?!urns|ained)',  # "ret" but not "returns" or "retained"
        r'\bmarket_cap\b',
        r'\beps_actual\b',
        r'\bstd_dev\b',          # should be ts_std_dev
        r'\bann_ret\b',
        r'\bavg_vol\b',
        r'\broe\b(?!_)',         # "roe" alone — use return_equity
        r'\broa\b(?!_)',         # "roa" alone — use return_assets
        r'\bpe\b(?!_|r)',        # "pe" alone — no such field
        r'\bpb\b(?!_)',          # "pb" alone — no such field
        r'\bps\b(?!_)',          # "ps" alone — no such field
        r'\bfcf\b(?!_)',         # "fcf" alone — use est_fcf or cashflow
        r'\bgrossmargin\b',
        r'\bnetmargin\b',
        r'\boperatingmargin\b',
        r'\bnetincome\b',        # correct field is "income"
        r'\bsgna\b',             # not a Brain field
        r'\brd\b(?!_)',          # use rd_expense
        r'\bdividendyield\b',
        r'\bev_ebitda\b',        # not a Brain field
        r'\bturnover_vol\b',     # not in CSV
        r'\badv60\b',            # not in CSV — only adv20 exists
        r'\badv5\b',             # not in CSV
        r'\bts_std\b(?!_dev)',   # must be ts_std_dev
        r'\bts_skewness\b',     # not in official operator list
        r'\bts_kurtosis\b',     # not in official operator list
        r'\bts_median\b',       # not in official operator list
        r'\bts_ir\b',           # not in official operator list
        r'\bts_entropy\b',      # not in official operator list
        r'\bts_autocorr\b',     # not in official operator list
        r'\bdemean\b',          # not in official operator list
        r'\btruncate\b(?!d)',   # not in official list (use winsorize)
        r'\bfill_nan\b',        # not in official list
        r'\bnan_out\b',         # not in official list
        r'\bpurify\b',          # not in official list
        r'\bfraction\b',        # not in official list
        r'\bsigmoid\b',         # not in official list
        r'\btanh\b',            # not in official list
        r'\bexp\b(?!r)',         # not in official list
        r'\bsquare\b',          # not in official list (use power(x,2))
        r'\blog1p\b',           # not in official list
    ]
    for pat in bad_fields:
        if re.search(pat, expr_lower):
            return False

    # No code constructs
    if any(kw in expr_lower for kw in ['def ', 'import ', 'for ', 'while ', 'class ']):
        return False

    # Allow multi-line with semicolons (Brain supports variable assignments with =)
    # But block Python-style "x = " at start of expression
    if re.match(r'^[a-z_]+ = ', expr_lower) and ';' not in expression:
        return False

    return True
