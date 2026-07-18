"""Lectura y validación de archivos CSV de gastos.

El lector nunca silencia filas inválidas: devuelve los gastos válidos junto
con la lista de errores encontrados, cada uno con su número de línea y motivo.
"""

from __future__ import annotations

import csv
import datetime
import logging
import math
from dataclasses import dataclass
from pathlib import Path

from analizador_gastos.modelos import Gasto

logger = logging.getLogger(__name__)

COLUMNAS_REQUERIDAS: tuple[str, ...] = ("fecha", "categoria", "monto")


@dataclass(frozen=True, slots=True)
class ErrorFila:
    """Error de validación asociado a una fila del CSV.

    Attributes:
        linea: Número de línea de la fila en el archivo (el encabezado es la 1).
        motivo: Descripción legible del problema encontrado.
    """

    linea: int
    motivo: str


def leer_gastos(ruta_csv: str | Path) -> tuple[list[Gasto], list[ErrorFila]]:
    """Lee un CSV de gastos y separa las filas válidas de las que tienen errores.

    El archivo debe tener un encabezado con las columnas ``fecha``, ``categoria``
    y ``monto``; la columna ``descripcion`` es opcional. Un archivo vacío produce
    dos listas vacías.

    Args:
        ruta_csv: Ruta al archivo CSV a leer.

    Returns:
        Una tupla ``(gastos, errores)`` con los gastos válidos y los errores
        por fila, en el orden en que aparecen en el archivo.

    Raises:
        ValueError: Si el encabezado no contiene las columnas requeridas.
        OSError: Si el archivo no existe o no se puede leer.
    """
    gastos: list[Gasto] = []
    errores: list[ErrorFila] = []

    with open(ruta_csv, encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None:
            logger.debug("Archivo vacío: %s", ruta_csv)
            return gastos, errores

        faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in lector.fieldnames]
        if faltantes:
            raise ValueError(f"el CSV no tiene las columnas requeridas: {', '.join(faltantes)}")

        for fila in lector:
            resultado = _convertir_fila(fila, lector.line_num)
            if isinstance(resultado, Gasto):
                gastos.append(resultado)
            else:
                logger.debug("Fila %d descartada: %s", resultado.linea, resultado.motivo)
                errores.append(resultado)

    return gastos, errores


def _convertir_fila(fila: dict[str, str | None], linea: int) -> Gasto | ErrorFila:
    """Convierte una fila cruda del CSV en un :class:`Gasto` o en un :class:`ErrorFila`."""
    fecha_cruda = (fila.get("fecha") or "").strip()
    categoria = (fila.get("categoria") or "").strip().lower()
    monto_crudo = (fila.get("monto") or "").strip()
    descripcion = (fila.get("descripcion") or "").strip()

    if not fecha_cruda or not categoria or not monto_crudo:
        return ErrorFila(linea, "faltan campos obligatorios (fecha, categoria o monto)")

    try:
        fecha = datetime.date.fromisoformat(fecha_cruda)
    except ValueError:
        return ErrorFila(linea, f"fecha inválida: {fecha_cruda!r} (se espera AAAA-MM-DD)")

    try:
        monto = float(monto_crudo)
    except ValueError:
        return ErrorFila(linea, f"monto inválido: {monto_crudo!r}")

    if not math.isfinite(monto):
        return ErrorFila(linea, f"monto no finito: {monto_crudo!r}")
    if monto < 0:
        return ErrorFila(linea, f"monto negativo: {monto_crudo!r}")

    return Gasto(fecha=fecha, categoria=categoria, monto=monto, descripcion=descripcion)
