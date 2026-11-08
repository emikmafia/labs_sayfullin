"""Расчеты: момент сопротивления W, фактическое напряжение σ, коэффициент k и класс прочности."""

from typing import Annotated
from constans import PI, K_SAFE, K_LIMIT


def section_modulus_rect(
    b: Annotated[float, "Ширина сечения, мм"],
    h: Annotated[float, "Высота сечения, мм"],
) -> float:
  """Рассчитать момент сопротивления для прямоугольного сечения: W = b * h^2 / 6."""
  return (b * (h ** 2)) / 6.0


def section_modulus_circle(
    d: Annotated[float, "Диаметр сечения, мм"],
) -> float:
  """Рассчитать момент сопротивления для круглого сечения: W = π * d^3 / 32."""
  return (PI * (d ** 3)) / 32.0


def section_modulus_beam(
    h: Annotated[float, "Высота двутавра, мм"],
) -> float:
  """Рассчитать момент сопротивления для двутавра: W = h^3 / 12."""
  return (h ** 3) / 12.0


def actual_stress(
    m: Annotated[float, "Изгибающий момент, кН * м"],
    w: Annotated[float, "Момент сопротивления, мм^3"],
) -> float:
  """Рассчитать фактическое напряжение: σ = (M * 1000000) / W (МПа)."""
  return (m * 1000000.0) / w


def usage_coefficient(
    sigma_fact: Annotated[float, "Фактическое напряжение, МПа"],
    sigma_dop: Annotated[float, "Допускаемое напряжение, МПа"],
) -> float:
  """Рассчитать коэффициент использования k = σ / [σ]."""
  return sigma_fact / sigma_dop


def strength_class(
    k: Annotated[float, "Коэффициент использования"],
) -> str:
  """Классификация состояния балки через if-elif-else."""
  if k < K_SAFE:
    return "Большой запас"
  elif K_SAFE <= k <= K_LIMIT:
    return "Допустимо"
  else:
    return "Перегрузка"
