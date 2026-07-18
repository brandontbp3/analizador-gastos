"""Generación de reportes de gastos en texto, JSON y Markdown."""

from __future__ import annotations

import json
from collections.abc import Sequence

from analizador_gastos import analisis
from analizador_gastos.modelos import Gasto

ANCHO_LINEA = 50
SIN_GASTOS = "No hay gastos para analizar."


def generar_reporte_texto(gastos: Sequence[Gasto]) -> str:
    """Genera el reporte en texto plano con barras proporcionales por categoría.

    Args:
        gastos: Gastos a resumir.

    Returns:
        El reporte completo como una sola cadena multilínea.
    """
    mayor = analisis.gasto_mayor(gastos)
    if mayor is None:
        return SIN_GASTOS

    total = analisis.total(gastos)
    promedio = analisis.promedio(gastos)

    lineas = [
        "=" * ANCHO_LINEA,
        "REPORTE DE GASTOS",
        "=" * ANCHO_LINEA,
        f"Total de registros : {len(gastos)}",
        f"Gasto total        : ${total:,.2f}",
        f"Gasto promedio     : ${promedio:,.2f}",
        f"Gasto mayor        : ${mayor.monto:,.2f} ({mayor.descripcion})",
        "",
        "--- Por categoría ---",
    ]
    for categoria, monto in analisis.total_por_categoria(gastos).items():
        porcentaje = monto / total * 100 if total else 0.0
        barra = "█" * int(porcentaje / 2)
        lineas.append(f"{categoria:<15} ${monto:>10,.2f}  {porcentaje:5.1f}% {barra}")

    lineas.append("")
    lineas.append("--- Por mes ---")
    variaciones = analisis.variacion_mensual(gastos)
    for mes, monto in analisis.total_por_mes(gastos).items():
        lineas.append(f"{mes:<15} ${monto:>10,.2f}  ({_formatear_variacion(variaciones[mes])})")

    return "\n".join(lineas)


def generar_reporte_json(gastos: Sequence[Gasto]) -> str:
    """Genera el reporte como cadena JSON con los mismos indicadores del reporte de texto.

    Args:
        gastos: Gastos a resumir.

    Returns:
        Una cadena JSON con ``total_registros``, ``total``, ``promedio``,
        ``gasto_mayor`` (``null`` si no hay gastos), ``por_categoria``,
        ``por_mes`` y ``variacion_pct`` (variación porcentual de cada mes
        respecto al anterior; ``null`` cuando no está definida).
    """
    mayor = analisis.gasto_mayor(gastos)
    por_categoria = analisis.total_por_categoria(gastos)
    por_mes = analisis.total_por_mes(gastos)
    variaciones = analisis.variacion_mensual(gastos)

    datos = {
        "total_registros": len(gastos),
        "total": round(analisis.total(gastos), 2),
        "promedio": round(analisis.promedio(gastos), 2),
        "gasto_mayor": _gasto_a_dict(mayor) if mayor is not None else None,
        "por_categoria": {cat: round(monto, 2) for cat, monto in por_categoria.items()},
        "por_mes": {mes: round(monto, 2) for mes, monto in por_mes.items()},
        "variacion_pct": {
            mes: round(valor, 2) if valor is not None else None
            for mes, valor in variaciones.items()
        },
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)


def generar_reporte_markdown(gastos: Sequence[Gasto]) -> str:
    """Genera el reporte como tablas Markdown listas para pegar en un issue o README.

    Args:
        gastos: Gastos a resumir.

    Returns:
        El reporte completo como una sola cadena Markdown con tablas de
        resumen general, por categoría (con porcentaje) y por mes (con
        variación respecto al mes anterior).
    """
    mayor = analisis.gasto_mayor(gastos)
    if mayor is None:
        return SIN_GASTOS

    total = analisis.total(gastos)
    promedio = analisis.promedio(gastos)
    variaciones = analisis.variacion_mensual(gastos)

    lineas = [
        "# Reporte de gastos",
        "",
        "## Resumen general",
        "",
        "| Indicador | Valor |",
        "| --- | --- |",
        f"| Total de registros | {len(gastos)} |",
        f"| Gasto total | ${total:,.2f} |",
        f"| Gasto promedio | ${promedio:,.2f} |",
        f"| Gasto mayor | ${mayor.monto:,.2f} ({mayor.descripcion}) |",
        "",
        "## Por categoría",
        "",
        "| Categoría | Monto | Porcentaje |",
        "| --- | ---: | ---: |",
    ]
    for categoria, monto in analisis.total_por_categoria(gastos).items():
        porcentaje = monto / total * 100 if total else 0.0
        lineas.append(f"| {categoria} | ${monto:,.2f} | {porcentaje:.1f}% |")

    lineas += [
        "",
        "## Por mes",
        "",
        "| Mes | Monto | Variación |",
        "| --- | ---: | ---: |",
    ]
    for mes, monto in analisis.total_por_mes(gastos).items():
        lineas.append(f"| {mes} | ${monto:,.2f} | {_formatear_variacion(variaciones[mes])} |")

    return "\n".join(lineas)


def _formatear_variacion(variacion: float | None) -> str:
    """Formatea una variación porcentual como texto (``—`` cuando no está definida)."""
    if variacion is None:
        return "—"
    return f"{variacion:+.1f}%"


def _gasto_a_dict(gasto: Gasto) -> dict[str, str | float]:
    """Convierte un gasto en un diccionario serializable a JSON."""
    return {
        "fecha": gasto.fecha.isoformat(),
        "categoria": gasto.categoria,
        "monto": round(gasto.monto, 2),
        "descripcion": gasto.descripcion,
    }
