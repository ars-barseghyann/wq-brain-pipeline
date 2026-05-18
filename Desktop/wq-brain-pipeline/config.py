"""Generator-only config. No Brain API settings needed."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # ── Claude ─────────────────────────────────────────────────────────
    anthropic_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

    # Use Sonnet for speed/cost at 60/day. Switch to opus for higher quality.
    claude_model: str = "claude-sonnet-4-5-20251101"

    # ── Generation targets ─────────────────────────────────────────────
    candidates_per_day: int = 60        # total output target
    batch_size: int = 5                 # expressions per archetype per batch
    # 12 archetypes × 5 = 60. Increase batch_size or repeat archetypes if you want more.

    # ── Diversity ──────────────────────────────────────────────────────
    min_diversity_score: float = 0.25   # lower threshold = allow more variety within archetype
    max_recent_fingerprints: int = 100  # how many past alphas to compare against

    # ── Async concurrency ─────────────────────────────────────────────
    max_concurrent_batches: int = 6     # parallel archetype batches at once
    request_timeout: int = 120          # seconds per Claude call

    # ── Research injection ────────────────────────────────────────────
    use_web_research: bool = True       # Claude searches for academic concepts
    research_every_n_archetypes: int = 1  # 1 = research for every archetype

    # ── Paths ──────────────────────────────────────────────────────────
    candidates_dir: str = "candidates"
    logs_dir: str = "logs"
    fingerprint_store: str = "data/fingerprints.json"

    def validate(self):
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Export it or add to .env")


cfg = Config()
