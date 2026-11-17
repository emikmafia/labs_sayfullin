import pytest

from num_series.moving_average import (
    simple_moving_average,
    centered_moving_average,
    exponential_moving_average,
)


def test_simple_moving_average():
    assert simple_moving_average([1, 2, 3, 4, 5], 3) == pytest.approx([2.0, 3.0, 4.0])


def test_simple_moving_average_window_too_big():
    with pytest.raises(ValueError):
        simple_moving_average([1, 2], 3)


def test_centered_moving_average():
    assert centered_moving_average([1, 2, 3, 4, 5], 3) == pytest.approx([2.0, 3.0, 4.0])


def test_centered_moving_average_even_window_raises():
    with pytest.raises(ValueError):
        centered_moving_average([1, 2, 3, 4], 2)


def test_exponential_moving_average():
    assert exponential_moving_average([1.0, 2.0, 3.0], 0.5) == pytest.approx(
        [1.0, 1.5, 2.25]
    )


def test_exponential_moving_average_invalid_alpha():
    with pytest.raises(ValueError):
        exponential_moving_average([1.0, 2.0], 0.0)
