# Analizador de Gastos

[![CI](https://github.com/brandontbp3/analizador-gastos/actions/workflows/ci.yml/badge.svg)](https://github.com/brandontbp3/analizador-gastos/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Linter: ruff](https://img.shields.io/badge/linter-ruff-261230.svg)](https://docs.astral.sh/ruff/)

Herramienta de línea de comandos en Python para analizar gastos personales desde un
archivo CSV. Genera un reporte con totales por categoría (con gráfico de barras en
texto), totales por mes con variación porcentual, gasto promedio y gasto mayor, en
formato texto, JSON o Markdown, con filtros por rango de fechas y por categoría.

Sin dependencias externas: solo la librería estándar.

## Características

- **Parseo robusto del CSV**: las filas corruptas no se silencian; se reportan en
  stderr con número de línea y motivo, y el análisis continúa con las filas válidas.
- **Tres formatos de salida**: reporte de texto con barras proporcionales, JSON
  listo para consumir desde otros programas o tablas Markdown listas para pegar
  en un issue o README.
- **Filtros por fecha y categoría**: `--desde` y `--hasta` (rango inclusivo) y
  `--categoria` (insensible a mayúsculas), combinables entre sí y con `--formato`.
- **Comparativa mensual**: cada mes muestra la variación porcentual respecto al
  mes anterior en todos los formatos.
- **Funciones puras de análisis** reutilizables desde Python (`total`, `promedio`,
  `total_por_categoria`, `total_por_mes`, `gasto_mayor`, `filtrar_gastos`,
  `variacion_mensual`).
- **Datos de ejemplo incluidos** dentro del paquete para probar la herramienta al
  instante.
- **Compatible con la consola de Windows**: la salida se reconfigura a UTF-8 para
  mostrar correctamente las barras del gráfico.

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -e .
```

## Uso

```bash
# Con los datos de ejemplo incluidos en el paquete
analizador-gastos

# Con tu propio archivo CSV
analizador-gastos ruta/a/mis_gastos.csv

# Reporte en JSON
analizador-gastos ruta/a/mis_gastos.csv --formato json

# Reporte en Markdown (tablas listas para pegar en un issue o README)
analizador-gastos ruta/a/mis_gastos.csv --formato markdown

# Solo los gastos de un rango de fechas (inclusivo)
analizador-gastos ruta/a/mis_gastos.csv --desde 2026-06-01 --hasta 2026-06-30

# Solo los gastos de una categoría (insensible a mayúsculas)
analizador-gastos ruta/a/mis_gastos.csv --categoria Comida

# Filtros combinados entre sí y con el formato
analizador-gastos ruta/a/mis_gastos.csv --desde 2026-06-01 --categoria comida --formato markdown

# Versión y ayuda
analizador-gastos --version
analizador-gastos --help
```

Los filtros se aplican antes del análisis. Una fecha mal formada o un `--desde`
posterior a `--hasta` terminan con un error claro y código de salida 2; si los
filtros no dejan ningún gasto, la CLI muestra un mensaje claro en lugar de un
reporte vacío.

### Formato del CSV

```csv
fecha,categoria,monto,descripcion
2026-05-03,comida,45.50,Supermercado semanal
2026-05-05,transporte,12.00,Pasajes de bus
```

- `fecha`: formato `AAAA-MM-DD`
- `categoria`: texto libre (se normaliza a minúsculas)
- `monto`: número decimal mayor o igual a cero
- `descripcion`: texto libre (opcional)

Si una fila es inválida (fecha mal formada, monto no numérico o negativo, campos
faltantes), se descarta y se muestra un aviso en stderr con la línea y el motivo.

### Ejemplo de salida

```text
==================================================
REPORTE DE GASTOS
==================================================
Total de registros : 15
Gasto total        : $918.14
Gasto promedio     : $61.21
Gasto mayor        : $199.99 (Curso de Python en línea)

--- Por categoría ---
servicios       $    240.00   26.1% █████████████
comida          $    235.65   25.7% ████████████
educacion       $    199.99   21.8% ██████████
...

--- Por mes ---
2026-05         $    253.70  (—)
2026-06         $    327.25  (+29.0%)
2026-07         $    337.19  (+3.0%)
```

Cada mes muestra entre paréntesis la variación porcentual respecto al mes
anterior; el primer mes muestra `(—)` porque no tiene referencia.

Con `--formato json` la salida es un objeto con `total_registros`, `total`,
`promedio`, `gasto_mayor`, `por_categoria`, `por_mes` y `variacion_pct`
(variación porcentual de cada mes respecto al anterior; `null` cuando no está
definida, como en el primer mes).

Con `--formato markdown` la salida son tablas Markdown (resumen general, por
categoría con porcentaje y por mes con variación); por ejemplo, la tabla por mes:

```markdown
| Mes | Monto | Variación |
| --- | ---: | ---: |
| 2026-05 | $253.70 | — |
| 2026-06 | $327.25 | +29.0% |
| 2026-07 | $337.19 | +3.0% |
```

## Desarrollo

Instala el paquete en modo editable con las dependencias de desarrollo:

```bash
pip install -e ".[dev]"
```

Ejecuta la suite de tests:

```bash
pytest
```

Revisa el estilo y el formato del código:

```bash
ruff check .
ruff format --check .
```

## Estructura del proyecto

```text
analizador-gastos/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── analizador_gastos/
│       ├── __init__.py
│       ├── modelos.py        # Dataclass Gasto
│       ├── lector.py         # Parseo y validación del CSV
│       ├── analisis.py       # Funciones puras de agregación
│       ├── reporte.py        # Reportes en texto, JSON y Markdown
│       ├── cli.py            # Interfaz de línea de comandos
│       └── datos/
│           └── gastos_ejemplo.csv
├── tests/
│   ├── conftest.py
│   ├── test_lector.py
│   ├── test_analisis.py
│   ├── test_reporte.py
│   └── test_cli.py
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).
