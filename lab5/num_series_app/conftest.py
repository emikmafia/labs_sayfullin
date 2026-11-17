"""Настройка путей для pytest.

Добавляет корень проекта в sys.path, чтобы тесты могли импортировать
пакет num_series и модуль main без установки проекта.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
