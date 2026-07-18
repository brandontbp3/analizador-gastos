"""Modelos de datos del analizador de gastos."""

from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Gasto:
    """Un gasto individual registrado en el archivo CSV.

    Attributes:
        fecha: Fecha en la que se realizó el gasto.
        categoria: Categoría del gasto, normalizada a minúsculas.
        monto: Importe del gasto (siempre mayor o igual a cero).
        descripcion: Texto libre opcional que describe el gasto.
    """

    fecha: datetime.date
    categoria: str
    monto: float
    descripcion: str = ""

    @property
    def mes(self) -> str:
        """Mes del gasto en formato ``AAAA-MM``."""
        return self.fecha.strftime("%Y-%m")
