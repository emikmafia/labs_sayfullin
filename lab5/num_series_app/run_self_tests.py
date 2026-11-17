"""Запуск самопроверок проекта без pytest.

Использование:
    python run_self_tests.py
"""
import contextlib
import io
import tempfile
from pathlib import Path

from num_series import (
    random_series, sine_series, trend_series,
    mean, median, spread, summarize,
    simple_moving_average, centered_moving_average, exponential_moving_average,
    save_series_json, load_series_auto,
)

import main as cli


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(argv)
    return code, out.getvalue(), err.getvalue()


def check_generator():
    assert len(random_series(10, seed=1)) == 10
    assert all(-1.0 <= v <= 1.0 for v in random_series(50, low=-1.0, high=1.0, seed=1))
    assert sine_series(4, amplitude=1.0, noise=0.0)[0] == 0.0
    assert trend_series(3, start=1.0, step=1.0, noise=0.0) == [1.0, 2.0, 3.0]


def check_stats():
    assert mean([1, 2, 3, 4]) == 2.5
    assert median([3, 1, 2]) == 2.0
    assert median([1, 2, 3, 4]) == 2.5
    assert spread([1, 5, 3]) == 4.0
    assert summarize([1, 2, 3, 4])["count"] == 4


def check_moving_average():
    assert simple_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
    assert centered_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
    assert exponential_moving_average([1.0, 2.0, 3.0], 0.5) == [1.0, 1.5, 2.25]


def check_io():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "s.json"
        save_series_json([1.0, 2.0, 3.0], path, meta={"kind": "test"})
        assert load_series_auto(path) == [1.0, 2.0, 3.0]


def check_cli():
    code, out, _ = run_cli([])
    assert code == 0
    assert "Среднее арифметическое" in out
    assert "SMA (window=3)" in out

    code, out, _ = run_cli(["--kind", "random", "--n", "10", "--seed", "1"])
    assert code == 0
    assert "сгенерирован (random, n=10, seed=1)" in out

    code, _, err = run_cli(["--n", "0"])
    assert code == 1
    assert "Ошибка" in err


CHECKS = (check_generator, check_stats, check_moving_average, check_io, check_cli)


def main():
    failed = 0
    for check in CHECKS:
        try:
            check()
        except AssertionError as err:
            failed += 1
            print(f"[FAIL] {check.__name__}: {err}")
        else:
            print(f"[ OK ] {check.__name__}")

    print("-" * 40)
    print(f"Провалено: {failed} из {len(CHECKS)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
