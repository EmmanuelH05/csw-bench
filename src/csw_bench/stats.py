"""Percentile bootstrap, pure Python.

At benchmark scale (hundreds of items, ten thousand resamples) this runs in seconds, so
it takes no numeric dependency. The seed is a required argument: a CI that cannot be
reproduced is a bare point estimate with extra steps.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from statistics import fmean


def bootstrap_ci(
    values: Sequence[float],
    *,
    resamples: int,
    seed: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty sample")
    if resamples < 1:
        raise ValueError("resamples must be positive")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be strictly between 0 and 1")

    rng = random.Random(seed)
    n = len(values)
    means = sorted(fmean(rng.choices(values, k=n)) for _ in range(resamples))

    tail = (1.0 - confidence) / 2.0
    lower = means[round(tail * (resamples - 1))]
    upper = means[round((1.0 - tail) * (resamples - 1))]
    return lower, upper
