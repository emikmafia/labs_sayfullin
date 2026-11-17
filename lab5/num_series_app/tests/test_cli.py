import pytest

import main as app


def test_main_returns_zero_and_prints_stats(capsys):
    assert app.main([]) == 0
    out = capsys.readouterr().out
    assert "Среднее арифметическое" in out
    assert "SMA (window=3)" in out


def test_main_prints_selected_kind(capsys):
    assert app.main(["--kind", "random", "--n", "10", "--seed", "1"]) == 0
    assert "сгенерирован (random, n=10, seed=1)" in capsys.readouterr().out


def test_main_returns_one_on_error(capsys):
    assert app.main(["--n", "0"]) == 1
    assert "Ошибка" in capsys.readouterr().err


def test_unknown_kind_is_rejected_by_argparse(capsys):
    with pytest.raises(SystemExit):
        app.main(["--kind", "unknown"])
