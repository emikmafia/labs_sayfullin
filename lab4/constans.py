"""Модуль констант для расчёта прочности балки на изгиб (Вариант 8)."""

import math

# Допустимые диапазоны для размеров сечения (мм)
MIN_ZNACH: float = 10.0
MAX_ZNACH: float = 1000.0

# Диапазон для изгибающего момента (кН * м)
MIN_M: float = 0.1
MAX_M: float = 500.0

# Диапазон для допускаемого напряжения (МПа)
MIN_SIGMA_DOP: float = 50.0
MAX_SIGMA_DOP: float =  400.0

# Пороговые значения коэффициента использования (k = sigma_fact/sigma_dop)
K_SAFE: float = 0.5     # Большой запас
K_LIMIT: float = 1.0    # Допустимо

# Число Пи
PI: float = math.pi

# Файл журнала ошибок ввода
LOG_FILE: str = "input_errors.log"
