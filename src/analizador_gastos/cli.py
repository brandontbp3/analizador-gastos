"""Interfaz de línea de comandos del analizador de gastos."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from importlib import resources
from pathlib import Path

from analizador_gastos import __version__
from analizador_gastos.lector import ErrorFila, leer_gastos
from analizador_gastos.modelos import Gasto
from analizador_gastos.reporte import generar_reporte_json, generar_reporte_texto


def _configurar_consola_utf8() -> None:
    """Reconfigura stdout y stderr a UTF-8 cuando la consola no lo usa.

    La consola de Windows usa cp1252 por defecto y no soporta caracteres
    como las barras (█) del reporte de texto.
    """
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure") and flujo.encoding and flujo.encoding.lower() != "utf-8":
            flujo.reconfigure(encoding="utf-8", errors="replace")


def crear_parser() -> argparse.ArgumentParser:
    """Construye el analizador de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        prog="analizador-gastos",
        description="Analiza un CSV de gastos y genera un reporte por categoría y por mes.",
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        default=None,
        help="ruta al archivo CSV de gastos (por defecto usa los datos de ejemplo incluidos)",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="formato del reporte (por defecto: texto)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _leer_datos_de_ejemplo() -> tuple[list[Gasto], list[ErrorFila]]:
    """Lee el CSV de ejemplo empaquetado con la distribución."""
    recurso = resources.files("analizador_gastos") / "datos" / "gastos_ejemplo.csv"
    with resources.as_file(recurso) as ruta:
        return leer_gastos(ruta)


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada de la CLI.

    Args:
        argv: Argumentos de línea de comandos; ``None`` usa ``sys.argv``.

    Returns:
        Código de salida del proceso: ``0`` si todo salió bien, ``1`` si hubo
        un error al leer el archivo.
    """
    _configurar_consola_utf8()
    args = crear_parser().parse_args(argv)

    try:
        if args.archivo is None:
            gastos, errores = _leer_datos_de_ejemplo()
        else:
            ruta = Path(args.archivo)
            if not ruta.is_file():
                print(f"Error: no se encontró el archivo {ruta}", file=sys.stderr)
                return 1
            gastos, errores = leer_gastos(ruta)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if errores:
        print(f"Aviso: se descartaron {len(errores)} fila(s) inválida(s):", file=sys.stderr)
        for error_fila in errores:
            print(f"  línea {error_fila.linea}: {error_fila.motivo}", file=sys.stderr)

    if args.formato == "json":
        print(generar_reporte_json(gastos))
    else:
        print(generar_reporte_texto(gastos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
