"""Журнал ошибок ввода (сохраняет сообщения в памяти и дублирует в файл)."""

from __future__ import annotations
import datetime
from constans import LOG_FILE

_entries: list[str] = []


def log_error(message: str) -> None:
    """Добавить запись об ошибке в память и файл с меткой времени."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {message}"
    _entries.append(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except OSError:
        pass


def get_entries() -> list[str]:
    """Вернуть копию журнала ошибок из памяти."""
    return list(_entries)


def clear() -> None:
    """Очистить журнал ошибок (используется в тестах)."""
    _entries.clear()
