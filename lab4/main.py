"""Главный модуль: связывает модули и выполняет главный цикл программы."""

from validation import input_size, input_moment, input_sigma_dop
from menu import show_menu, select_mode, mode_name
from operations import section_modulus_rect, section_modulus_circle, section_modulus_beam, actual_stress, usage_coefficient, strength_class


def main() -> None:
  """Главный сценарий."""
  print("Лабораторная работа 4. Прочность балки на изгиб (Вариант 8).")

  while True:
    show_menu()
    mode = select_mode()

    if mode is None:
      print("Работа завершена.")
      break

    # Ввод данных в зависимости от выбранного режима
    match mode:
      case 1:
        b = input_size()
        h = input_size()
        w = section_modulus_rect(b, h)
      case 2:
        d = input_size()
        w = section_modulus_circle(d)
      case 3:
        h = input_size()
        w = section_modulus_beam(h)
      case _:
        continue

    m = input_moment()
    sigma_dop = input_sigma_dop()

    # Расчёты
    sigma_fact = actual_stress(m, w)
    k = usage_coefficient(sigma_fact, sigma_dop)
    proverka = sigma_fact <= sigma_dop
    cls_name = strength_class(k)

    # Вывод результатов
    print("\n--- Результаты расчёта ---")
    print(f"Тип сечения: {mode_name(mode)}")
    print(f"Момент сопротивления W: {w:.2f} мм^3")
    print(f"Фактическое напряжение σ: {sigma_fact:.2f} МПа")
    print(f"Допускаемое напряжение [σ]: {sigma_dop:.2f} МПа")
    print(f"Коэффициент использования k: {k:.2f}")
    print("Проверка прочности (σ <= [σ]): "f"{'Выполнена' if proverka else 'Не выполнена'}")
    print(f"Класс прочности: {cls_name}")


if __name__ == "__main__":
  main()
