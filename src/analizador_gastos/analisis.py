"""Funciones puras de análisis sobre colecciones de gastos."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence

from analizador_gastos.modelos import Gasto


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


def gasto_mayor(gastos: Iterable[Gasto]) -> Gasto | None:
    """El gasto de mayor monto, o ``None`` si no hay gastos."""
    return max(gastos, key=lambda gasto: gasto.monto, default=None)
