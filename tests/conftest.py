"""Fixtures compartidas para la suite de tests."""

import datetime

import pytest

from analizador_gastos.modelos import Gasto


@pytest.fixture
def gastos() -> list[Gasto]:
    """Lista pequeña de gastos conocidos para verificar cálculos exactos."""
    return [
        Gasto(datetime.date(2026, 5, 3), "comida", 50.0, "Super"),
        Gasto(datetime.date(2026, 5, 10), "comida", 30.0, "Almuerzo"),
        Gasto(datetime.date(2026, 6, 1), "transporte", 20.0, "Bus"),
    ]
