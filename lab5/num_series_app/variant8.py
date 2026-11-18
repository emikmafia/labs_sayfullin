"""Вариант 8: ряд с выбросами, усечённое среднее и скользящая медиана.

Запуск:
    python variant8.py --n 1500 --window 10 --seed 42

Параметры ряда и окна задаются через CLI, как требует задание вариантов.
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from num_series.moving_average import (
    simple_moving_average,
    simple_moving_average_deque,
)
from num_series.stats import mean, median, spread
from num_series.variant8 import outlier_series, rolling_median, trimmed_mean


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Вариант 8: ряд с выбросами, усечённое среднее, скользящая медиана",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--n", type=int, default=1500,
        help="количество точек в ряде",
    )
    parser.add_argument(
        "--window", type=int, default=10,
        help="размер окна k для скользящих средних",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="зерно ГПСЧ для воспроизводимости",
    )
    return parser


def print_series(title: str, values: List[float], limit: int = 5) -> None:
    print(f"{title} (n={len(values)}):")
    print(" " + " ".join(f"{v:>10.3f}" for v in values[:limit]))


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        data = outlier_series(args.n, seed=args.seed)
        sma_list = simple_moving_average(data, args.window)
        sma_deque = simple_moving_average_deque(data, args.window)
        medians = rolling_median(data, args.window)
        trimmed = trimmed_mean(data, 0.10)
    except ValueError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1

    print("=" * 60)
    print(f"Вариант 8: n = {args.n}, k = {args.window}, seed = {args.seed}")
    print("-" * 60)
    print(f"Среднее арифметическое  : {mean(data):>12.4f}")
    print(f"Медиана                 : {median(data):>12.4f}")
    print(f"Размах (max - min)      : {spread(data):>12.4f}")
    print(f"Усечённое среднее (10%) : {trimmed:>12.4f}")
    print("-" * 60)
    print_series(f"SMA (list, window={args.window})", sma_list)
    print_series(f"SMA (deque, window={args.window})", sma_deque)
    print_series(f"Скользящая медиана (window={args.window})", medians)

    difference = max(abs(a - b) for a, b in zip(sma_list, sma_deque))
    print(f"Макс. расхождение SMA list/deque: {difference:.3e}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
