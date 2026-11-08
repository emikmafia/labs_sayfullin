"""Меню выбора типа сечения и маршрутизация через match-case."""

from __future__ import annotations


def show_menu() -> None:
  """Вывести пункты меню на экран."""
  print("\nВыберите тип сечения балки: ")
  print("1 — прямоугольное (W = b * h^2 / 6)")
  print("2 — круглое (W = π * d^3 / 32)")
  print("3 — двутавр (W = h^3 / 12)")
  print("0 — выход")


def select_mode() -> int | None:
  """Циклически запрашивать пункт меню через match-case. Возвращает номер режима или None при выходе."""
  while True:
    choice = input("Введите номер пункта (0-3): ").strip()
    match choice:
      case "1" | "2" | "3":
        return int(choice)
      case "0":
        return None
      case _:
        print("Ошибка: неверный пункт меню. Повторите ввод.")


def mode_name(mode: int) -> str:
  """Вернуть название типа сечения по его номеру через match-case."""
  match mode:
    case 1:
      return "Прямоугольное"
    case 2:
      return "Круглое"
    case 3:
      return "Двутавр"
    case _:
      return "Неизвестный"
