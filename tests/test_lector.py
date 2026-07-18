"""Tests del módulo lector: parseo robusto del CSV."""

import datetime
from pathlib import Path

import pytest

from analizador_gastos.lector import leer_gastos
from analizador_gastos.modelos import Gasto

ENCABEZADO = "fecha,categoria,monto,descripcion\n"


def _escribir_csv(tmp_path: Path, contenido: str) -> Path:
    ruta = tmp_path / "gastos.csv"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def test_csv_valido(tmp_path: Path) -> None:
    ruta = _escribir_csv(
        tmp_path,
        ENCABEZADO + "2026-05-03,Comida,45.50,Supermercado\n2026-06-01,transporte,12.00,Bus\n",
    )
    gastos, errores = leer_gastos(ruta)
    assert errores == []
    assert gastos == [
        Gasto(datetime.date(2026, 5, 3), "comida", 45.5, "Supermercado"),
        Gasto(datetime.date(2026, 6, 1), "transporte", 12.0, "Bus"),
    ]


def test_csv_con_bom_utf8(tmp_path: Path) -> None:
    """Excel y PowerShell en Windows guardan CSV UTF-8 con BOM; debe aceptarse."""
    ruta = tmp_path / "gastos.csv"
    ruta.write_text(
        ENCABEZADO + "2026-05-03,comida,45.50,Supermercado\n",
        encoding="utf-8-sig",
    )
    gastos, errores = leer_gastos(ruta)
    assert errores == []
    assert gastos == [Gasto(datetime.date(2026, 5, 3), "comida", 45.5, "Supermercado")]


def test_categoria_se_normaliza_a_minusculas(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO + "2026-05-03,  COMIDA  ,10.00,Algo\n")
    gastos, _ = leer_gastos(ruta)
    assert gastos[0].categoria == "comida"


def test_descripcion_es_opcional(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, "fecha,categoria,monto\n2026-05-03,comida,10.00\n")
    gastos, errores = leer_gastos(ruta)
    assert errores == []
    assert gastos[0].descripcion == ""


def test_monto_invalido_se_reporta_con_linea(tmp_path: Path) -> None:
    ruta = _escribir_csv(
        tmp_path,
        ENCABEZADO + "2026-05-03,comida,45.50,Super\n2026-05-04,comida,abc,Roto\n",
    )
    gastos, errores = leer_gastos(ruta)
    assert len(gastos) == 1
    assert len(errores) == 1
    assert errores[0].linea == 3
    assert "monto inválido" in errores[0].motivo


def test_fecha_invalida_se_reporta(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO + "no-es-fecha,comida,10.00,Algo\n")
    gastos, errores = leer_gastos(ruta)
    assert gastos == []
    assert errores[0].linea == 2
    assert "fecha inválida" in errores[0].motivo


def test_campos_faltantes_se_reportan(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO + "2026-05-03,comida\n")
    gastos, errores = leer_gastos(ruta)
    assert gastos == []
    assert errores[0].linea == 2
    assert "faltan campos obligatorios" in errores[0].motivo


def test_monto_negativo_se_reporta(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO + "2026-05-03,comida,-5.00,Devolución\n")
    gastos, errores = leer_gastos(ruta)
    assert gastos == []
    assert "monto negativo" in errores[0].motivo


def test_monto_no_finito_se_reporta(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO + "2026-05-03,comida,nan,Raro\n")
    gastos, errores = leer_gastos(ruta)
    assert gastos == []
    assert "monto no finito" in errores[0].motivo


def test_filas_validas_se_conservan_junto_a_errores(tmp_path: Path) -> None:
    ruta = _escribir_csv(
        tmp_path,
        ENCABEZADO
        + "2026-05-03,comida,45.50,Super\n"
        + "fecha-mala,comida,10.00,Roto\n"
        + "2026-05-05,transporte,12.00,Bus\n",
    )
    gastos, errores = leer_gastos(ruta)
    assert [gasto.categoria for gasto in gastos] == ["comida", "transporte"]
    assert [error.linea for error in errores] == [3]


def test_archivo_vacio(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, "")
    assert leer_gastos(ruta) == ([], [])


def test_archivo_solo_con_encabezado(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, ENCABEZADO)
    assert leer_gastos(ruta) == ([], [])


def test_columnas_requeridas_faltantes(tmp_path: Path) -> None:
    ruta = _escribir_csv(tmp_path, "fecha,importe\n2026-05-03,10.00\n")
    with pytest.raises(ValueError, match="columnas requeridas"):
        leer_gastos(ruta)


def test_archivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        leer_gastos(tmp_path / "no_existe.csv")
