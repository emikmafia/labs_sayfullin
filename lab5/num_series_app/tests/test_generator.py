import math

import pytest

from num_series.generator import (
    random_series,
    sine_series,
    trend_series,
    _validate_n,
)


def test_validate_n_rejects_non_positive():
    for bad in (0, -1):
        with pytest.raises(ValueError):
            _validate_n(bad)


def test_random_series_length_and_bounds():
    data = random_series(10, low=-1.0, high=1.0, seed=1)
    assert len(data) == 10
    assert all(-1.0 <= v <= 1.0 for v in data)


def test_random_series_reproducible():
    assert random_series(5, seed=7) == random_series(5, seed=7)


def test_sine_series_values():
    data = sine_series(4, amplitude=1.0, frequency=1.0, noise=0.0)
    assert data[0] == pytest.approx(0.0)
    assert data[1] == pytest.approx(math.sin(math.pi / 2))


def test_trend_series_values():
    assert trend_series(3, start=1.0, step=1.0, noise=0.0) == [1.0, 2.0, 3.0]
