"""Сохранение и чтение числовых рядов в формате JSON.

Формат файла:
{
  "meta": {
    "kind": "sine",
    "n": 20,
    "seed": 42,
    "created": "2025-01-15T10:30:00"
  },
  "data": [0.0, 8.09, 9.51, ...]
}

Метаданные опциональны — при чтении они не обязательны.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PathLike = Union[str, Path]

# ---------------------------------------------------------------------------
# Сохранение
# ---------------------------------------------------------------------------


def save_series_json(
    data: List[float],
    path: PathLike,
    meta: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> None:
    """Сохраняет числовой ряд в JSON-файл.

    Args:
        data: числовой ряд (непустой список float/int).
        path: путь к файлу (создастся или перезапишется).
        meta: произвольные метаданные (kind, seed, ...). Добавится
            автоматически поле "created" с текущим временем.
        indent: отступ для читаемости (None — компактный JSON).

    Raises:
        ValueError: если data пуст или содержит нечисловые элементы.
    """
    if not data:
        raise ValueError("Ряд пуст: нечего сохранять")

    # Проверка типов — иначе json.dump упадёт с непонятной ошибкой
    for i, v in enumerate(data):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(f"Элемент data[{i}] = {v!r} не является числом")

    payload: Dict[str, Any] = {
        "meta": {
            "n": len(data),
            "created": datetime.now().isoformat(timespec="seconds"),
            **(meta or {}),
        },
        "data": list(data),
    }

    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=indent)
    except OSError as err:
        raise ValueError(f"Не удалось записать файл {file_path}: {err}") from err


# ---------------------------------------------------------------------------
# Чтение
# ---------------------------------------------------------------------------


def load_series_json(path: PathLike, with_meta: bool = False):
    """Читает числовой ряд из JSON-файла.

    Поддерживает два формата:
        1. {"data": [...], "meta": {...}} — «полный» формат (наш)
        2. [...]  — «голый» список чисел

    Args:
        path: путь к файлу.
        with_meta: если True, возвращает кортеж (data, meta);
            если False — только список чисел.

    Returns:
        list[float] или (list[float], dict).

    Raises:
        ValueError: если файл не найден, не JSON, нет поля data,
            data не список или содержит нечисловые элементы.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Файл не найден: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"Файл {file_path} не является корректным JSON: "
            f"{err.msg} (строка {err.lineno})"
        ) from err
    except OSError as err:
        raise ValueError(f"Не удалось прочитать файл {file_path}: {err}") from err

    # Поддержка «голого» списка
    if isinstance(payload, list):
        data, meta = payload, {}
    elif isinstance(payload, dict):
        if "data" not in payload:
            raise ValueError(f"В файле {file_path} нет поля 'data'")
        data = payload["data"]
        meta = payload.get("meta", {}) or {}
    else:
        raise ValueError(
            f"Некорректная структура JSON в {file_path}: "
            f"ожидался список или объект с 'data'"
        )

    if not isinstance(data, list):
        raise ValueError(
            f"Поле 'data' в {file_path} должно быть списком, "
            f"а не {type(data).__name__}"
        )
    if not data:
        raise ValueError(f"Ряд в файле {file_path} пуст")

    for i, v in enumerate(data):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(
                f"Элемент data[{i}] = {v!r} в {file_path} не является числом"
            )

    result = [float(v) for v in data]
    return (result, meta) if with_meta else result
