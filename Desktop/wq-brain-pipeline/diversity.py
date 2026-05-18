"""
Diversity Tracker

Stores structural fingerprints of all previously generated alphas
and scores new candidates for originality. No simulation state — 
this module only cares about structural uniqueness.

Fingerprint = hash of (operators used, data domains, time horizons).
Two alphas are "too similar" if Jaccard similarity of their fingerprints
exceeds the diversity threshold.
"""

import json
import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from brain_data import (
    TS_OPERATORS, CS_OPERATORS, MATH_OPERATORS,
    GROUP_OPERATORS, TRANSFORM_OPERATORS, VECTOR_OPERATORS, LOGICAL_OPERATORS,
    PRICE_VOLUME_FIELDS, FUNDAMENTAL_FIELDS, ANALYST_FIELDS,
    NEWS_FIELDS, SENTIMENT_FIELDS, OPTION_FIELDS,
    RELATIONSHIP_FIELDS, MODEL_FIELDS,
)
from config import cfg


@dataclass
class Fingerprint:
    expression_hash: str        # md5 of the raw expression (exact-dup check)
    structural_hash: str        # hash of operator+domain combo
    ts_ops: list
    cs_ops: list
    domains: list               # price / fundamental / analyst / news / ...
    horizons: list              # short / medium / long
    fields: list
    archetype: str
    date: str


def fingerprint(expression: str, archetype: str = "") -> Fingerprint:
    """Extract structural fingerprint from a Brain expression."""
    expr = expression.lower()

    ts_ops  = sorted({op for op in TS_OPERATORS  if op.lower() in expr})
    cs_ops  = sorted({op for op in CS_OPERATORS  if op.lower() in expr})

    # Check each dataset category
    price_f = [f for f in PRICE_VOLUME_FIELDS if f in expr]
    fund_f  = [f for f in FUNDAMENTAL_FIELDS  if f in expr]
    anal_f  = [f for f in ANALYST_FIELDS      if f in expr]
    news_f  = [f for f in NEWS_FIELDS         if f in expr]
    sent_f  = [f for f in SENTIMENT_FIELDS    if f in expr]
    opt_f   = [f for f in OPTION_FIELDS       if f in expr]
    rel_f   = [f for f in RELATIONSHIP_FIELDS if f in expr]
    mdl_f   = [f for f in MODEL_FIELDS        if f in expr]

    domains = []
    if price_f: domains.append("price_volume")
    if fund_f:  domains.append("fundamental")
    if anal_f:  domains.append("analyst")
    if news_f:  domains.append("news")
    if sent_f:  domains.append("sentiment")
    if opt_f:   domains.append("option")
    if rel_f:   domains.append("relationship")
    if mdl_f:   domains.append("model")

    windows = [int(w) for w in re.findall(r'\b(\d+)\b', expr)
               if int(w) in [5, 10, 20, 40, 60, 120, 252, 756]]
    horizons = sorted({
        "short"  if w <= 10 else
        "medium" if w <= 60 else
        "long"
        for w in windows
    })

    all_fields = sorted(set(price_f + fund_f + anal_f + news_f + sent_f + opt_f + rel_f + mdl_f))

    struct_str = "|".join(ts_ops + cs_ops + domains + horizons)
    structural_hash = hashlib.md5(struct_str.encode()).hexdigest()[:12]
    expression_hash = hashlib.md5(expression.strip().encode()).hexdigest()[:12]

    from datetime import date
    return Fingerprint(
        expression_hash=expression_hash,
        structural_hash=structural_hash,
        ts_ops=ts_ops,
        cs_ops=cs_ops,
        domains=domains,
        horizons=horizons,
        fields=all_fields,
        archetype=archetype,
        date=date.today().isoformat(),
    )


def _jaccard(a: list, b: list) -> float:
    s1, s2 = set(a), set(b)
    if not s1 and not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def structural_similarity(fp1: Fingerprint, fp2: Fingerprint) -> float:
    """[0,1] — 1.0 means structurally identical."""
    return (
        _jaccard(fp1.ts_ops,   fp2.ts_ops)   * 0.25 +
        _jaccard(fp1.cs_ops,   fp2.cs_ops)   * 0.15 +
        _jaccard(fp1.domains,  fp2.domains)  * 0.30 +  # domains weighted highest
        _jaccard(fp1.horizons, fp2.horizons) * 0.15 +
        _jaccard(fp1.fields,   fp2.fields)   * 0.15
    )


class DiversityTracker:
    """
    Persists fingerprints across runs and scores new candidates.
    Thread-safe for async use (all mutations go through add()).
    """

    def __init__(self):
        self.path = Path(cfg.fingerprint_store)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._store: list[Fingerprint] = []
        self._expression_hashes: set[str] = set()
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    raw = json.load(f)
                self._store = [Fingerprint(**item) for item in raw.get("fingerprints", [])]
                self._expression_hashes = {fp.expression_hash for fp in self._store}
            except Exception:
                self._store = []

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(
                {"fingerprints": [asdict(fp) for fp in self._store]},
                f, indent=2
            )

    def is_exact_duplicate(self, expression: str) -> bool:
        h = hashlib.md5(expression.strip().encode()).hexdigest()[:12]
        return h in self._expression_hashes

    def diversity_score(self, expression: str) -> float:
        """
        Return [0,1] originality score vs. the recent portfolio.
        1.0 = completely novel. 0.0 = structural duplicate.
        """
        if not self._store:
            return 1.0
        fp = fingerprint(expression)
        recent = self._store[-cfg.max_recent_fingerprints:]
        max_sim = max(structural_similarity(fp, stored) for stored in recent)
        return 1.0 - max_sim

    def add(self, expression: str, archetype: str = ""):
        """Register a new alpha. Call after accepting a candidate."""
        if self.is_exact_duplicate(expression):
            return
        fp = fingerprint(expression, archetype)
        self._store.append(fp)
        self._expression_hashes.add(fp.expression_hash)
        self._save()

    def coverage_summary(self) -> dict:
        """What archetypes/domains have we already covered?"""
        arch: dict = {}
        domains: dict = {}
        for fp in self._store:
            arch[fp.archetype] = arch.get(fp.archetype, 0) + 1
            for d in fp.domains:
                domains[d] = domains.get(d, 0) + 1
        return {
            "total": len(self._store),
            "archetypes": arch,
            "domains": domains,
        }

    def forbidden_patterns_text(self, n: int = 15) -> str:
        """
        Human-readable list of existing structural patterns.
        Shown to Claude as anti-mimicry context.
        """
        lines = []
        for fp in self._store[-n:]:
            ops = fp.ts_ops[:3] + fp.cs_ops[:2]
            lines.append(
                f"  [{fp.archetype}] ops:{','.join(ops) or 'none'}  "
                f"domains:{','.join(fp.domains)}  "
                f"horizons:{','.join(fp.horizons)}"
            )
        return "\n".join(lines) if lines else "  (none yet)"
