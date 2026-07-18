"""Funciones puras de análisis sobre colecciones de gastos."""

from __future__ import annotations

import datetime
from collections import defaultdict
from collections.abc import Iterable, Sequence

from analizador_gastos.modelos import Gasto


def filtrar_gastos(
    gastos: Iterable[Gasto],
    desde: datetime.date | None = None,
    hasta: datetime.date | None = None,
    categoria: str | None = None,
) -> list[Gasto]:
    """Filtra gastos por rango de fechas (inclusivo) y por categoría.

    Args:
        gastos: Gastos a filtrar.
        desde: Fecha mínima, inclusive; ``None`` no aplica límite inferior.
        hasta: Fecha máxima, inclusive; ``None`` no aplica límite superior.
        categoria: Categoría a conservar, insensible a mayúsculas y a espacios
            alrededor (se compara con la categoría normalizada); ``None``
            conserva todas las categorías.

    Returns:
        Lista con los gastos que cumplen todos los filtros, en su orden original.
    """
    categoria_normalizada = categoria.strip().lower() if categoria is not None else None
    return [
        gasto
        for gasto in gastos
        if (desde is None or gasto.fecha >= desde)
        and (hasta is None or gasto.fecha <= hasta)
        and (categoria_normalizada is None or gasto.categoria == categoria_normalizada)
    ]


def total(gastos: Iterable[Gasto]) -> float:
    """Suma de los montos de todos los gastos (``0.0`` si no hay gastos)."""
    return sum(gasto.monto for gasto in gastos)


def promedio(gastos: Sequence[Gasto]) -> float:
    """Monto promedio por gasto, o ``0.0`` si no hay gastos."""
    if not gastos:
        return 0.0
    return total(gastos) / len(gastos)


def total_por_categoria(gastos: Iterable[Gasto]) -> dict[str, float]:
    """Totales agrupados por categoría, ordenados de mayor a menor monto."""
    totales: defaultdict[str, float] = defaultdict(float)
    for gasto in gastos:
        totales[gasto.categoria] += gasto.monto
    return dict(sorted(totales.items(), key=lambda par: par[1], reverse=True))


def total_por_mes(gastos: Iterable[Gasto]) -> dict[str, float]:
    """Totales agrupados por mes (formato ``AAAA-MM``), en orden cronológico."""
    totales: defaultdict[str, float] = defaultdict(float)
    for gasto in gastos:
        totales[gasto.mes] += gasto.monto
    return dict(sorted(totales.items()))


def variacion_mensual(gastos: Iterable[Gasto]) -> dict[str, float | None]:
    """Variación porcentual del total de cada mes respecto al mes anterior.

    El primer mes no tiene referencia y su variación es ``None``; también es
    ``None`` cuando el total del mes anterior es cero, porque la variación
    porcentual no está definida en ese caso.

    Returns:
        Diccionario mes (``AAAA-MM``) → variación porcentual (o ``None``),
        en orden cronológico.
    """
    variaciones: dict[str, float | None] = {}
    total_anterior: float | None = None
    for mes, monto in total_por_mes(gastos).items():
        if total_anterior is None or total_anterior == 0:
            variaciones[mes] = None
        else:
            variaciones[mes] = (monto - total_anterior) / total_anterior * 100
        total_anterior = monto
    return variaciones


def gasto_mayor(gastos: Iterable[Gasto]) -> Gasto | None:
    """El gasto de mayor monto, o ``None`` si no hay gastos."""
    return max(gastos, key=lambda gasto: gasto.monto, default=None)
