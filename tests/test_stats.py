from __future__ import annotations

from statistics import fmean

import pytest

from csw_bench.stats import bootstrap_ci

_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0, 0.5, 0.25, 0.75]


def test_same_seed_reproduces_the_interval() -> None:
    """A CI that cannot be reproduced is a bare point estimate with extra steps."""
    kwargs = {"resamples": 1000, "seed": 42}

    assert bootstrap_ci(_VALUES, **kwargs) == bootstrap_ci(_VALUES, **kwargs)


def test_interval_brackets_the_sample_mean() -> None:
    low, high = bootstrap_ci(_VALUES, resamples=2000, seed=0)

    assert low <= fmean(_VALUES) <= high
    assert low < high


def test_constant_data_collapses_to_a_point() -> None:
    assert bootstrap_ci([0.5, 0.5, 0.5], resamples=100, seed=0) == (0.5, 0.5)


def test_empty_sample_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty sample"):
        bootstrap_ci([], resamples=100, seed=0)


def test_nonpositive_resamples_are_rejected() -> None:
    with pytest.raises(ValueError, match="resamples"):
        bootstrap_ci(_VALUES, resamples=0, seed=0)


@pytest.mark.parametrize("confidence", [0.0, 1.0, 1.5])
def test_degenerate_confidence_is_rejected(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        bootstrap_ci(_VALUES, resamples=100, seed=0, confidence=confidence)


def test_wider_confidence_never_narrows_the_interval() -> None:
    narrow = bootstrap_ci(_VALUES, resamples=2000, seed=7, confidence=0.5)
    wide = bootstrap_ci(_VALUES, resamples=2000, seed=7, confidence=0.99)

    assert wide[0] <= narrow[0]
    assert narrow[1] <= wide[1]
