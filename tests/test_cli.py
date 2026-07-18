"""Tests de la interfaz de línea de comandos (con capsys)."""

import json
from pathlib import Path

import pytest

from analizador_gastos.cli import main

ENCABEZADO = "fecha,categoria,monto,descripcion\n"


def test_usa_datos_de_ejemplo_por_defecto(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main([])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "REPORTE DE GASTOS" in salida.out
    assert salida.err == ""


def test_lee_archivo_propio(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ruta = tmp_path / "gastos.csv"
    ruta.write_text(ENCABEZADO + "2026-05-03,comida,45.50,Super\n", encoding="utf-8")
    codigo = main([str(ruta)])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "Total de registros : 1" in salida.out
    assert "$45.50" in salida.out


def test_formato_json(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main(["--formato", "json"])
    salida = capsys.readouterr()
    assert codigo == 0
    datos = json.loads(salida.out)
    assert datos["total_registros"] == 15
    assert datos["total"] == pytest.approx(918.14)


def test_archivo_inexistente(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main(["no_existe.csv"])
    salida = capsys.readouterr()
    assert codigo == 1
    assert "no se encontró el archivo" in salida.err


def test_aviso_en_stderr_por_filas_invalidas(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = tmp_path / "gastos.csv"
    ruta.write_text(
        ENCABEZADO + "2026-05-03,comida,45.50,Super\n2026-05-04,comida,abc,Roto\n",
        encoding="utf-8",
    )
    codigo = main([str(ruta)])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "Aviso: se descartaron 1 fila(s)" in salida.err
    assert "línea 3" in salida.err
    assert "Total de registros : 1" in salida.out


def test_csv_sin_columnas_requeridas(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ruta = tmp_path / "gastos.csv"
    ruta.write_text("fecha,importe\n2026-05-03,10.00\n", encoding="utf-8")
    codigo = main([str(ruta)])
    salida = capsys.readouterr()
    assert codigo == 1
    assert "columnas requeridas" in salida.err


def test_formato_desconocido_termina_con_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--formato", "xml"])
    assert excinfo.value.code == 2
