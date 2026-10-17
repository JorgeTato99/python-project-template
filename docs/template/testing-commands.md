# Referencia de comandos de testing

Los ejemplos usan el entorno de uv y el lock de la plantilla. Esta referencia enseña opciones; los comandos que se conservan en cada aplicación están en [desarrollo](../development/comandos.md).

## Instalar la selección correcta

```console
uv sync --locked
uv sync --locked --no-default-groups --group test
uv run --locked --no-default-groups --group test pytest --version
```

El primer comando incluye dev. El segundo instala proyecto y herramientas de pruebas sin los grupos predeterminados. Los grupos opcionales se incluyen también en el comando de ejecución que los necesita.

## Descubrir y seleccionar

```console
uv run --locked pytest --collect-only -q
uv run --locked pytest tests/test_package.py
uv run --locked pytest tests/test_package.py::test_reports_installed_distribution_version
uv run --locked pytest -k "version or distribution"
uv run --locked pytest -m integration
uv run --locked pytest -m "not integration"
```

Las rutas de los primeros ejemplos existen en la base. `integration` es un marker registrado; que esté registrado no implica que todos los proyectos tengan casos con ese marker.

Una expresión `-k` selecciona nombres; una expresión `-m` selecciona markers. Revisa el número recolectado y deseleccionado.

## Ver fixtures, markers y opciones

```console
uv run --locked pytest --fixtures
uv run --locked pytest --fixtures-per-test tests/test_package.py
uv run --locked pytest --markers
uv run --locked pytest --help
```

Una opción desconocida suele indicar un plugin ausente o una versión diferente. La ayuda del entorno concreto permite comprobarlo.

## Detenerse y repetir fallos

```console
uv run --locked pytest -x
uv run --locked pytest --maxfail=3
uv run --locked pytest --lf
uv run --locked pytest --ff
```

`--lf` usa información de fallos guardada en el caché. `--ff` prioriza fallos anteriores y continúa con el resto. No sustituyen una ejecución completa antes de cerrar un cambio relevante.

## Output, captura y traceback

| Opción | Efecto |
| --- | --- |
| `-v`, `-vv` | Más detalle de ejecución |
| `-q` | Menos detalle |
| `-s` | Desactivar captura de salida |
| `--tb=short` | Traceback abreviado |
| `--tb=long` | Traceback detallado |
| `--showlocals` | Mostrar variables locales en el fallo |
| `-ra` | Resumen adicional de resultados |
| `--durations=10` | Mostrar los diez casos más lentos |

Las variables locales pueden contener datos de pruebas sensibles. Selecciona qué logs compartes según el contenido real del proyecto.

`-vv` aumenta verbosidad; no es una orden de impresión de docstrings.

## Depuración interactiva

```console
uv run --locked pytest --pdb -x
uv run --locked pytest --trace tests/test_package.py
```

Son herramientas interactivas para una consola local. No las configures como paso normal de CI.

## Cobertura e informes

```console
uv run --locked pytest --cov --cov-report=term-missing
uv run --locked pytest --cov --cov-report=html
uv run --locked pytest --cov --cov-report=xml
uv run --locked pytest --junitxml=artifacts/tests.xml
```

JUnit registra resultados; coverage mide ejecución de código. `--cov-append` acumula datos previos: úsalo deliberadamente para no mezclar ejecuciones distintas.

La configuración de cobertura y sus límites se explican en [patrones](testing-patterns.md). No hay un porcentaje universal de suficiencia.

## Plugins opcionales

| Capacidad | Ejemplo |
| --- | --- |
| Paralelo | `uv run --locked --group parallel pytest -n 2` |
| Orden aleatorio | `uv run --locked --group random pytest --randomly-seed=20261016` |
| Timeout | `uv run --locked --group timeout pytest --timeout=30` |
| Watch | `uv run --locked --group watch ptw --now .` |
| Benchmark | `uv run --locked --group performance pytest --benchmark-only` |

Async, mocking e Hypothesis se utilizan desde tests que importan sus APIs después de instalar los grupos correspondientes.

La base comprueba contratos de plugins con:

```console
uv run --locked --group async --group parallel --group performance --group property --group mock --group timeout python scripts/check_capabilities.py
```

Esa comprobación no compara rendimiento entre intérpretes.

## Comandos actuales de Make

Make es opcional. Estos atajos existen en el Makefile:

| Target | Uso |
| --- | --- |
| `install` | Sincronizar el entorno |
| `check` | Ejecutar la verificación completa |
| `test` | Ejecutar pytest |
| `format` | Aplicar formato |
| `lint` | Comprobar reglas |
| `type-check` | Ejecutar mypy |
| `security` | Ejecutar Bandit |
| `audit` | Auditar distribuciones instaladas |
| `build` | Construir artefactos |
| `watch` | Ejecutar el watcher |
| `hooks` | Instalar hooks en un repositorio Git |

No se documentan como disponibles los targets históricos que no existen en la implementación actual.

## Dos flujos útiles

Durante desarrollo, selecciona el caso o familia que cambias y ejecuta sus comprobaciones relevantes. Para cerrar el cambio utiliza el verificador completo:

```console
uv run --locked python scripts/check.py
```

Los benchmarks y los comandos interactivos tienen su propio contexto. Registra selección, versiones y condiciones cuando comuniques resultados.

## Fuentes

Consulta 2026-10-16.

| Fuente | Fecha | Aporte |
| --- | --- | --- |
| [pytest: invocación](https://docs.pytest.org/en/stable/how-to/usage.html) | s/f | Selección y depuración |
| [pytest: referencia](https://docs.pytest.org/en/stable/reference/reference.html) | s/f | Flags y configuración |
| [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) | s/f | Reportes y procesos |
| [uv: sync](https://docs.astral.sh/uv/concepts/projects/sync/) | s/f | Selección de entorno |
| [pytest-watcher](https://pypi.org/project/pytest-watcher/) | s/f | Observación de cambios |
