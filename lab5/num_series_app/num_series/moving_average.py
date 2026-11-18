import time
from collections import deque
from typing import Sequence, List


# ==========================================
# 3.3. Модуль скользящей средней (moving_average.py)
# ==========================================

def check_window(window: int, n: int) -> None:
    """Валидация размера окна."""
    if not isinstance(window, int) or window < 1:
        raise ValueError(f"window должно быть целым >= 1 (получено: {window})")
    if window > n:
        raise ValueError(
            f"window не может быть больше длины ряда (получено: {window} > {n})"
        )


def simple_moving_average(data: Sequence[float], window: int) -> List[float]:
    """
    Простая скользящая средняя (SMA).
    Использует бегущую сумму для эффективности O(n).
    """
    check_window(window, len(data))
    
    # Начальная сумма первого окна
    running = sum(data[:window])
    result = [running / window]
    
    # Двигаемся по ряду, обновляя сумму (убираем старый элемент, добавляем новый)
    for i in range(window, len(data)):
        running += data[i] - data[i - window]
        result.append(running / window)
        
    return result


# ==========================================
# Самостоятельное задание
# ==========================================

def centered_moving_average(data: Sequence[float], window: int) -> List[float]:
    """
    Центрированная скользящая средняя.
    Окно должно быть нечётным. Выходной ряд выровнен по центру.
    """
    if window % 2 == 0:
        raise ValueError(f"Для центрированной SMA window должно быть нечётным (получено: {window})")
    check_window(window, len(data))
    
    half_window = window // 2
    result = []
    
    # Идём по точкам, где окно полностью помещается в ряд
    for i in range(half_window, len(data) - half_window):
        # Берём окно, центрированное на текущем элементе i
        current_window = data[i - half_window : i + half_window + 1]
        result.append(sum(current_window) / window)
        
    return result


def exponential_moving_average(data: Sequence[float], alpha: float) -> List[float]:
    """
    Экспоненциальная скользящая средняя (EMA).
    EMA[0] = data[0]
    EMA[i] = alpha * data[i] + (1 - alpha) * EMA[i-1]
    """
    if not data:
        raise ValueError("Ряд пуст: расчёт статистики невозможен")
    if not (0 < alpha <= 1):
        raise ValueError(f"alpha должна быть в диапазоне (0, 1] (получено: {alpha})")

    result = [float(data[0])]
    
    for i in range(1, len(data)):
        ema_val = alpha * data[i] + (1 - alpha) * result[-1]
        result.append(ema_val)
        
    return result


def simple_moving_average_deque(data: Sequence[float], window: int) -> List[float]:
    """SMA с использованием deque (двусторонней очереди)."""
    check_window(window, len(data))
    result = []
    d = deque()
    running_sum = 0.0
    for x in data:
        d.append(x)
        running_sum += x
        if len(d) > window:
            running_sum -= d.popleft()
        if len(d) == window:
            result.append(running_sum / window)
    return result


def benchmark_moving_average(data: Sequence[float], window: int, repeats: int = 1000) -> dict:
    """
    Замеряет среднее время выполнения SMA для реализаций на list и deque.
    Возвращает словарь с ключами 'list' и 'deque' (время в секундах).
    """
    # Проверка корректности окна (выбросит ValueError при необходимости)
    check_window(window, len(data))

    # Замер для list-реализации (существующая simple_moving_average)
    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average(data, window)
    t_list = (time.perf_counter() - t0) / repeats

    # Замер для deque-реализации
    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average_deque(data, window)
    t_deque = (time.perf_counter() - t0) / repeats

    return {"list": t_list, "deque": t_deque}