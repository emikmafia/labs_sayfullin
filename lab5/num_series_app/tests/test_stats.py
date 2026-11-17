import pytest

from num_series.stats import mean, median, spread, summarize


def test_mean():
    assert mean([1, 2, 3, 4]) == pytest.approx(2.5)


def test_median_odd_and_even():
    assert median([3, 1, 2]) == pytest.approx(2.0)
    assert median([1, 2, 3, 4]) == pytest.approx(2.5)


def test_spread():
    assert spread([1, 5, 3]) == pytest.approx(4.0)


def test_summarize():
    result = summarize([1, 2, 3, 4])
    assert result["count"] == 4
    assert result["min"] == pytest.approx(1.0)
    assert result["max"] == pytest.approx(4.0)


def test_empty_series_raises():
    for func in (mean, median, spread, summarize):
        with pytest.raises(ValueError):
            func([])
