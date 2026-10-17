# python-project-template

Base reutilizable para proyectos Python: paquete instalable, herramientas de calidad, pruebas, construcción y perfiles opcionales.

- Desarrollo con **CPython 3.15.0**; compatibilidad declarada desde **3.14**.
- Núcleo sin dependencias de aplicación.
- `uv` **0.13.1** como versión de referencia; `uv.lock` conserva la resolución completa.
- Ruff, mypy estricto, pytest y coverage en el entorno de desarrollo.
- API y datos como extras; notebooks y plugins de pruebas como grupos opcionales.

## Empezar

Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) >=0.13.1,<0.14 y copia o clona esta plantilla.

```console
uv sync --locked
uv run --locked python -m python_project_template --version
uv run --locked python scripts/check.py
```

Los comandos funcionan en PowerShell, bash y zsh. No necesitas activar el entorno ni instalar Make. El Makefile ofrece atajos opcionales.

El comando `check.py` comprueba lock, tipos, lint, formato, seguridad del código, pruebas, construcción y distribución. Se detiene con un código distinto de cero ante el primer fallo. La auditoría de dependencias es una orden adicional que consulta servicios externos.

## Personalizar una copia

```console
uv run --locked python scripts/bootstrap.py --name mi-proyecto --description "Descripción del proyecto" --dry-run
uv run --locked python scripts/bootstrap.py --name mi-proyecto --description "Descripción del proyecto"
uv lock
uv sync --locked
uv run --locked ruff format src scripts tests
uv run --locked python -m mi_proyecto --version
uv run --locked python scripts/check.py
```

El script actualiza distribución, namespace y comando, genera un README de aplicación y un CHANGELOG sin el historial de la plantilla y conserva las referencias informativas mientras se adopta la base. Si esos archivos contienen trabajo propio, exige conservarlos con `--keep-readme` o `--keep-changelog`. Conserva el lock previo hasta ejecutar `uv lock`. Personaliza también titular de licencia, documentación y ajustes del repositorio; revisa [adopción](docs/template/adopcion.md).

## Cerrar la adopción en la copia

Cuando hayas adaptado el proyecto, previsualiza y aplica el retiro del material exclusivo de la plantilla:

```console
uv run --locked python scripts/finalize_template.py --dry-run
uv run --locked python scripts/finalize_template.py --apply
uv run --locked python scripts/check.py
```

El cierre conserva un respaldo local bajo `temp/` y se detiene si detecta cambios o contenido nuevo en los archivos retirables. La plantilla original conserva sus guías; el README generado y la documentación de desarrollo permanecen en la aplicación.

## Perfiles opcionales

| Necesidad | Instalación | Comprobación |
| --- | --- | --- |
| API con FastAPI | `uv sync --locked --extra api` | `uv run --locked --extra api python scripts/check_profiles.py api` |
| Datos con NumPy, Polars y Arrow | `uv sync --locked --extra data` | `uv run --locked --extra data python scripts/check_profiles.py data` |
| Notebooks | `uv sync --locked --group notebooks` | `uv run --locked --group notebooks python scripts/check_profiles.py notebooks` |
| Pruebas asíncronas | `uv sync --locked --group async` | Decorar con `pytest.mark.asyncio` y definir scopes explícitos. |
| Hooks con prek | `uv sync --locked --group hooks` | `uv run --locked --group hooks prek validate-config .pre-commit-config.yaml` |

Al ejecutar comandos, conserva los mismos extras/grupos que seleccionaste al instalar. `uv run` sincroniza el entorno según su selección. Más opciones en [perfiles](docs/development/perfiles.md) y [pruebas](docs/development/pruebas.md).

Un frontend JavaScript/TypeScript requiere su configuración propia. Esta plantilla aporta la parte Python de un proyecto full stack; las aplicaciones gráficas pueden añadir su framework de interfaz.

## Comandos habituales

```console
uv run --locked ruff check src scripts tests
uv run --locked ruff format --check src scripts tests
uv run --locked mypy
uv run --locked pytest --cov --cov-report=term-missing
uv run --locked bandit -c pyproject.toml -r src scripts
uv run --locked pip-audit --skip-editable
uv build
```

Para aplicar formato utiliza `ruff format` sin `--check`. La auditoría anterior cubre el entorno seleccionado, incluidas sus herramientas, y omite la distribución local editable.

## Documentación

- [Índice de la plantilla](docs/template/README.md).
- [Antipatrones y decisiones contextuales](docs/template/python-project-anti-patterns.md).
- [Guía razonada del boilerplate](docs/template/python-boilerplate-guide.md).
- [Fundamentos de testing](docs/template/testing-guide.md), [patrones](docs/template/testing-patterns.md) y [comandos](docs/template/testing-commands.md).
- [Documentación permanente de desarrollo](docs/development/README.md).

- [Adopción y personalización](docs/template/adopcion.md).
- [Perfiles y selección de dependencias](docs/development/perfiles.md).
- [Pruebas y ejemplos actuales](docs/development/pruebas.md).
- [Recetas de pruebas](docs/development/recetas-testing.md).
- [Decisiones y fuentes](docs/template/decisiones.md).
- [Reporte técnico de fundamentación](docs/template/evaluacion-tecnica.md).
- [Verificación y límites](docs/template/verificacion.md).
- [Contribuir](CONTRIBUTING.md), [seguridad](SECURITY.md), [cambios](CHANGELOG.md).

## Estructura

```text
src/python_project_template/  Paquete instalable y comando mínimo
scripts/                     Personalización y comprobaciones portables
tests/                       Contratos de instalación, personalización y validación
docs/template/               Explicación, adopción y evidencia de la plantilla
docs/development/            Documentación operativa que permanece
.github/                     CI y mantenimiento de dependencias
temp/                        Copias, investigación y ejecuciones locales; ignorado
pyproject.toml               Metadatos, dependencias y configuración
uv.lock                      Resolución reproducible que se conserva en Git
```

La versión mínima del manifiesto y de los analizadores es 3.14. La matriz de CI está configurada para 3.14.8 y 3.15.0 en Windows/Linux. El estado de ejecución real se documenta en [verificación](docs/template/verificacion.md).

## Licencia

[MIT](LICENSE). Al reutilizar la plantilla, conserva los avisos aplicables y personaliza la identificación de tu proyecto.
