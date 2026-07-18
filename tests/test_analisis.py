"""Tests del módulo analisis: funciones puras de agregación."""

import datetime

import pytest

from analizador_gastos import analisis
from analizador_gastos.modelos import Gasto


def test_total(gastos: list[Gasto]) -> None:
    assert analisis.total(gastos) == pytest.approx(100.0)


def test_total_sin_gastos() -> None:
    assert analisis.total([]) == 0.0


def test_promedio(gastos: list[Gasto]) -> None:
    assert analisis.promedio(gastos) == pytest.approx(100.0 / 3)


def test_promedio_sin_gastos() -> None:
    assert analisis.promedio([]) == 0.0


def test_total_por_categoria_suma_y_ordena(gastos: list[Gasto]) -> None:
    totales = analisis.total_por_categoria(gastos)
    assert totales == {"comida": 80.0, "transporte": 20.0}
    assert list(totales) == ["comida", "transporte"]


def test_total_por_categoria_sin_gastos() -> None:
    assert analisis.total_por_categoria([]) == {}


def test_total_por_mes_orden_cronologico(gastos: list[Gasto]) -> None:
    totales = analisis.total_por_mes(gastos)
    assert totales == {"2026-05": 80.0, "2026-06": 20.0}
    assert list(totales) == ["2026-05", "2026-06"]


def test_total_por_mes_sin_gastos() -> None:
    assert analisis.total_por_mes([]) == {}


def test_gasto_mayor(gastos: list[Gasto]) -> None:
    mayor = analisis.gasto_mayor(gastos)
    assert mayor is not None
    assert mayor.monto == 50.0
    assert mayor.descripcion == "Super"


def test_gasto_mayor_sin_gastos() -> None:
    assert analisis.gasto_mayor([]) is None


def test_gasto_mayor_con_empate_devuelve_el_primero() -> None:
    empatados = [
        Gasto(datetime.date(2026, 5, 1), "comida", 10.0, "Primero"),
        Gasto(datetime.date(2026, 5, 2), "comida", 10.0, "Segundo"),
    ]
    mayor = analisis.gasto_mayor(empatados)
    assert mayor is not None
    assert mayor.descripcion == "Primero"
