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


def test_filtrar_gastos_sin_filtros_devuelve_todo(gastos: list[Gasto]) -> None:
    assert analisis.filtrar_gastos(gastos) == gastos


def test_filtrar_gastos_desde(gastos: list[Gasto]) -> None:
    filtrados = analisis.filtrar_gastos(gastos, desde=datetime.date(2026, 5, 10))
    assert [gasto.descripcion for gasto in filtrados] == ["Almuerzo", "Bus"]


def test_filtrar_gastos_hasta(gastos: list[Gasto]) -> None:
    filtrados = analisis.filtrar_gastos(gastos, hasta=datetime.date(2026, 5, 10))
    assert [gasto.descripcion for gasto in filtrados] == ["Super", "Almuerzo"]


def test_filtrar_gastos_rango_inclusivo_en_ambos_extremos(gastos: list[Gasto]) -> None:
    filtrados = analisis.filtrar_gastos(
        gastos, desde=datetime.date(2026, 5, 3), hasta=datetime.date(2026, 6, 1)
    )
    assert filtrados == gastos


def test_filtrar_gastos_categoria_insensible_a_mayusculas(gastos: list[Gasto]) -> None:
    filtrados = analisis.filtrar_gastos(gastos, categoria="  COMIDA  ")
    assert [gasto.categoria for gasto in filtrados] == ["comida", "comida"]


def test_filtrar_gastos_combina_fechas_y_categoria(gastos: list[Gasto]) -> None:
    filtrados = analisis.filtrar_gastos(
        gastos,
        desde=datetime.date(2026, 5, 5),
        hasta=datetime.date(2026, 6, 30),
        categoria="comida",
    )
    assert [gasto.descripcion for gasto in filtrados] == ["Almuerzo"]


def test_filtrar_gastos_sin_coincidencias(gastos: list[Gasto]) -> None:
    assert analisis.filtrar_gastos(gastos, categoria="viajes") == []


def test_filtrar_gastos_lista_vacia() -> None:
    assert analisis.filtrar_gastos([], desde=datetime.date(2026, 1, 1)) == []


def test_variacion_mensual(gastos: list[Gasto]) -> None:
    variaciones = analisis.variacion_mensual(gastos)
    assert variaciones["2026-05"] is None
    assert variaciones["2026-06"] == pytest.approx(-75.0)
    assert list(variaciones) == ["2026-05", "2026-06"]


def test_variacion_mensual_aumento() -> None:
    pareja = [
        Gasto(datetime.date(2026, 5, 1), "comida", 100.0, "Base"),
        Gasto(datetime.date(2026, 6, 1), "comida", 129.0, "Sube"),
    ]
    assert analisis.variacion_mensual(pareja)["2026-06"] == pytest.approx(29.0)


def test_variacion_mensual_un_solo_mes() -> None:
    unico = [Gasto(datetime.date(2026, 5, 1), "comida", 10.0, "Algo")]
    assert analisis.variacion_mensual(unico) == {"2026-05": None}


def test_variacion_mensual_mes_anterior_en_cero() -> None:
    con_mes_en_cero = [
        Gasto(datetime.date(2026, 5, 1), "comida", 0.0, "Gratis"),
        Gasto(datetime.date(2026, 6, 1), "comida", 10.0, "Algo"),
    ]
    assert analisis.variacion_mensual(con_mes_en_cero) == {"2026-05": None, "2026-06": None}


def test_variacion_mensual_sin_gastos() -> None:
    assert analisis.variacion_mensual([]) == {}
