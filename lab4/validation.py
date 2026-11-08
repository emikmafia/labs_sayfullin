"""Валидация пользовательского ввода (проверка границ через if-elif-else, try/except)."""

from __future__ import annotations
from constans import MIN_ZNACH, MAX_ZNACH, MIN_M, MAX_M, MIN_SIGMA_DOP, MAX_SIGMA_DOP
from logger import log_error


def validate_range(value: float, low: float, high: float) -> tuple[bool, str]:
    """Проверка попадания value в [low, high] через if-elif-else."""
    if value < low:
        return False, f"Ошибка: значение меньше нижней границы ({low})."
    elif value > high:
        return False, f"Ошибка: значение больше верхней границы ({high})."
    else:
        return True, ""


def input_number(prompt: str, low: float, high: float) -> float:
    """Циклически запрашивать число, пока не будет корректного.
    Проверяет тип (float) через try/except ValueError и границы."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError as e:
            msg = str(e.args[0]) if e.args else str(e)
            msg = f"Ошибка: введено не число ('{raw}'). {msg}"
            print(msg)
            log_error(msg)
            continue

        ok, msg = validate_range(value, low, high)
        if ok:
            return value
        print(msg + "Повторите ввод.")
        log_error(msg)


def input_size() -> float:
    """Циклический ввод размеров сечения (мм), допустимо 10..1000."""
    return input_number(
        f"Введите размер сечения, мм ({MIN_ZNACH}..{MAX_ZNACH}): ",
        MIN_ZNACH, MAX_ZNACH
    )


def input_moment() -> float:
    """Циклический ввод изгибающего момента М (кН * м), допустимо 0.1..500."""
    return input_number(
        f"Введите изгибающий момент М, кН * м  ({MIN_M}..{MAX_M}): ",
        MIN_M, MAX_M
    )


def input_sigma_dop() -> float:
    """Циклический ввод допускаемого напряжения [σ] (МПа), допустимо 50..400."""
    return input_number(
        f"Введите допускаемое напряжение [σ], МПа ({MIN_SIGMA_DOP}..{MAX_SIGMA_DOP}): ",
        MIN_SIGMA_DOP, MAX_SIGMA_DOP,
    )
