"""Tests del módulo reporte: salida en texto y JSON."""

import json

from analizador_gastos.modelos import Gasto
from analizador_gastos.reporte import generar_reporte_json, generar_reporte_texto


def test_reporte_texto_contiene_indicadores(gastos: list[Gasto]) -> None:
    reporte = generar_reporte_texto(gastos)
    assert "REPORTE DE GASTOS" in reporte
    assert "Total de registros : 3" in reporte
    assert "$100.00" in reporte
    assert "$33.33" in reporte
    assert "$50.00 (Super)" in reporte
    assert "comida" in reporte
    assert "2026-05" in reporte
    assert "█" in reporte


def test_reporte_texto_ordena_categorias_por_monto(gastos: list[Gasto]) -> None:
    reporte = generar_reporte_texto(gastos)
    assert reporte.index("comida") < reporte.index("transporte")


def test_reporte_texto_sin_gastos() -> None:
    assert generar_reporte_texto([]) == "No hay gastos para analizar."


def test_reporte_json_estructura(gastos: list[Gasto]) -> None:
    datos = json.loads(generar_reporte_json(gastos))
    assert datos["total_registros"] == 3
    assert datos["total"] == 100.0
    assert datos["promedio"] == 33.33
    assert datos["gasto_mayor"] == {
        "fecha": "2026-05-03",
        "categoria": "comida",
        "monto": 50.0,
        "descripcion": "Super",
    }
    assert datos["por_categoria"] == {"comida": 80.0, "transporte": 20.0}
    assert datos["por_mes"] == {"2026-05": 80.0, "2026-06": 20.0}


def test_reporte_json_sin_gastos() -> None:
    datos = json.loads(generar_reporte_json([]))
    assert datos["total_registros"] == 0
    assert datos["total"] == 0.0
    assert datos["promedio"] == 0.0
    assert datos["gasto_mayor"] is None
    assert datos["por_categoria"] == {}
    assert datos["por_mes"] == {}
