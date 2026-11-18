"""Вариант 8: числовой ряд с выбросами, усечённое среднее, скользящая медиана.

Состав варианта:
- ряд: шум плюс два выброса, значения которых в 10 раз больше типичных;
- дополнительный показатель: усечённое среднее (10% с каждого конца);
- сглаживание: скользящая медиана окна k (чётное и нечётное окно).

Модуль не заменяет существующие модули пакета и не меняет их поведение.
"""
from __future__ import annotations

import random
from typing import List, Optional, Sequence

__all__ = ["outlier_series", "trimmed_mean", "rolling_median"]


def _ensure_not_empty(data: Sequence[float]) -> None:
    if not data:
        raise ValueError("Ряд пуст: расчёт невозможен")


def _median_sorted(sorted_data: Sequence[float]) -> float:
    """Медиана уже отсортированного ряда: чётное и нечётное количество."""
    n = len(sorted_data)
    k = n // 2
    if n % 2:
        return float(sorted_data[k])
    return (sorted_data[k - 1] + sorted_data[k]) / 2.0


def outlier_series(
    n: int = 1500,
    seed: Optional[int] = None,
    positions: Optional[Sequence[int]] = None,
) -> List[float]:
    """Ряд из n чисел: нормальный шум и два выброса, в 10 раз больше типичных.

    Типичный масштаб ряда оценивается по максимальному отклонению шума,
    значение выброса равно 10 * scale.

    Args:
        n: длина ряда (по варианту 1500).
        seed: зерно ГПСЧ для воспроизводимости.
        positions: индексы выбросов; по умолчанию n // 3 и 2 * n // 3.

    Raises:
        ValueError: если n не положительное целое или позиция выброса вне ряда.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(f"n должно быть целым >= 1 (получено: {n!r})")

    rng = random.Random(seed)
    data = [rng.gauss(0.0, 1.0) for _ in range(n)]

    if positions is None:
        positions = (n // 3, (2 * n) // 3)

    scale = max(abs(v) for v in data)
    for position in positions:
        if not isinstance(position, int) or isinstance(position, bool):
            raise ValueError(
                f"позиция выброса должна быть целой (получено: {position!r})"
            )
        if not 0 <= position < n:
            raise ValueError(f"позиция выброса вне ряда: {position} (n={n})")
        data[position] = 10.0 * scale

    return data


def trimmed_mean(data: Sequence[float], proportion: float = 0.10) -> float:
    """Усечённое среднее: по proportion доли отбрасывается с каждого конца.

    Args:
        data: числовой ряд.
        proportion: доля усечения с каждой стороны (по варианту 0.10).

    Raises:
        ValueError: если ряд пуст, proportion вне [0, 0.5) или после
            усечения не осталось значений.
    """
    _ensure_not_empty(data)
    if not (0 <= proportion < 0.5):
        raise ValueError(
            f"proportion должна быть в [0, 0.5) (получено: {proportion})"
        )

    ordered = sorted(data)
    cut = int(len(ordered) * proportion)
    kept = ordered[cut:len(ordered) - cut] if cut else ordered
    if not kept:
        raise ValueError("После усечения ряд пуст")
    return sum(kept) / len(kept)


def rolling_median(data: Sequence[float], window: int) -> List[float]:
    """Скользящая медиана: медиана каждого полного окна длины window.

    Окно может быть чётным и нечётным: для чётного берётся среднее двух
    центральных элементов. Длина результата len(data) - window + 1.

    Raises:
        ValueError: если ряд пуст, window не целое, window < 1 или window
            больше длины ряда.
    """
    _ensure_not_empty(data)
    if not isinstance(window, int) or isinstance(window, bool) or window < 1:
        raise ValueError(f"window должно быть целым >= 1 (получено: {window!r})")
    if window > len(data):
        raise ValueError(
            f"window не может быть больше длины ряда (получено: {window} > {len(data)})"
        )

    result: List[float] = []
    last_start = len(data) - window + 1
    for start in range(last_start):
        result.append(_median_sorted(sorted(data[start:start + window])))
    return result
