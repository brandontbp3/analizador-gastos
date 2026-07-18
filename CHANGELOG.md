# Registro de cambios

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] - 2026-07-18

### Añadido

- Paquete `analizador_gastos` con layout `src/` y módulos separados:
  `modelos`, `lector`, `analisis`, `reporte` y `cli`.
- Dataclass `Gasto` (fecha, categoría, monto, descripción) con fecha tipada
  como `datetime.date`.
- Lector de CSV robusto: devuelve los gastos válidos junto con una lista de
  errores por fila (número de línea y motivo), sin silenciar filas corruptas.
- Funciones puras de análisis: `total`, `promedio`, `total_por_categoria`,
  `total_por_mes` y `gasto_mayor`.
- Reporte en formato JSON además del reporte de texto con barras.
- CLI instalable como comando `analizador-gastos`, con flag `--formato
  texto|json`, aviso en stderr por filas inválidas y datos de ejemplo
  empaquetados como recurso (accedidos vía `importlib.resources`).
- Empaquetado moderno con `pyproject.toml` (PEP 621, setuptools) y
  entry point de consola.
- Suite de tests en pytest para lector, análisis, reporte y CLI.
- Integración continua con GitHub Actions (Python 3.10 a 3.13, ruff y pytest).
- Licencia MIT, changelog y `.gitignore` completo.

### Cambiado

- Los tests migraron de `unittest` a pytest, ahora importan el paquete
  instalado en lugar de manipular `sys.path`.
- El reporte de texto se genera desde las funciones puras de `analisis`.

### Eliminado

- Script suelto `analizador.py` en la raíz del proyecto (reemplazado por el
  paquete `src/analizador_gastos/`).
- Carpeta `datos/` de la raíz: los datos de ejemplo ahora viven dentro del
  paquete.
