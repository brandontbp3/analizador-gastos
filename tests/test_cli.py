"""Tests de la interfaz de línea de comandos (con capsys)."""

import json
from pathlib import Path

import pytest

from analizador_gastos.cli import main

ENCABEZADO = "fecha,categoria,monto,descripcion\n"
CSV_FILTROS = (
    ENCABEZADO
    + "2026-05-03,comida,50.00,Super\n"
    + "2026-05-10,Transporte,20.00,Bus\n"
    + "2026-06-01,comida,30.00,Almuerzo\n"
)


def _escribir_csv_filtros(tmp_path: Path) -> Path:
    ruta = tmp_path / "gastos.csv"
    ruta.write_text(CSV_FILTROS, encoding="utf-8")
    return ruta


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


def test_filtra_por_rango_de_fechas(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    codigo = main([str(ruta), "--desde", "2026-05-10", "--hasta", "2026-06-01"])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "Total de registros : 2" in salida.out
    assert "$50.00" in salida.out


def test_filtro_de_fechas_es_inclusivo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    codigo = main([str(ruta), "--desde", "2026-05-03", "--hasta", "2026-06-01"])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "Total de registros : 3" in salida.out


def test_filtra_por_categoria_insensible_a_mayusculas(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    codigo = main([str(ruta), "--categoria", "TRANSPORTE"])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "Total de registros : 1" in salida.out
    assert "$20.00" in salida.out


def test_filtros_combinados_con_formato_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    codigo = main(
        [str(ruta), "--desde", "2026-06-01", "--categoria", "comida", "--formato", "json"]
    )
    salida = capsys.readouterr()
    assert codigo == 0
    datos = json.loads(salida.out)
    assert datos["total_registros"] == 1
    assert datos["total"] == 30.0


def test_filtro_sin_coincidencias_muestra_mensaje(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    codigo = main([str(ruta), "--categoria", "viajes"])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "No hay gastos que coincidan con los filtros aplicados." in salida.out
    assert "REPORTE DE GASTOS" not in salida.out


def test_fecha_de_filtro_invalida_termina_con_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        main([str(ruta), "--desde", "03/05/2026"])
    salida = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "fecha inválida" in salida.err


def test_desde_posterior_a_hasta_termina_con_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ruta = _escribir_csv_filtros(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        main([str(ruta), "--desde", "2026-06-01", "--hasta", "2026-05-01"])
    salida = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "no puede ser posterior" in salida.err


def test_formato_markdown(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main(["--formato", "markdown"])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "# Reporte de gastos" in salida.out
    assert "| Total de registros | 15 |" in salida.out
    assert "## Por mes" in salida.out
    assert "+29.0%" in salida.out


def test_variacion_mensual_en_reporte_de_texto(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main([])
    salida = capsys.readouterr()
    assert codigo == 0
    assert "(—)" in salida.out
    assert "(+29.0%)" in salida.out
