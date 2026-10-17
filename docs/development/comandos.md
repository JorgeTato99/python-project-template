# Comandos de desarrollo

## Instalación y ejecución

```console
uv sync --locked
uv run --locked python scripts/check_profiles.py core
```

El entorno incluye dev por defecto. Para instalar el paquete sin herramientas utiliza `uv sync --locked --no-default-groups`. Los [perfiles](perfiles.md) describen extras y grupos opcionales.

## Comprobación completa

```console
uv run --locked python scripts/check.py
```

El verificador comprueba lock, tipos, lint, formato, análisis de código, pruebas y distribución. Devuelve fallo ante el primer control que no pase.

## Comprobaciones selectivas

```console
uv run --locked mypy
uv run --locked ruff check src scripts tests
uv run --locked ruff format --check src scripts tests
uv run --locked pytest
uv run --locked pytest --cov --cov-report=term-missing
uv run --locked bandit -c pyproject.toml -r src scripts
uv run --locked pip-audit --skip-editable
uv build
uv run --locked python scripts/verify_distribution.py
```

La auditoría consulta fuentes externas y examina las distribuciones del entorno seleccionado, con el paquete editable omitido. No reemplaza una revisión completa de la aplicación.

## Aplicar formato y actualizar dependencias

```console
uv run --locked ruff format src scripts tests
uv lock --upgrade
uv sync --locked
```

Revisa los cambios y vuelve a comprobar los contratos relevantes. La resolución del entorno y el backend aislado de construcción tienen ámbitos distintos.

## Pruebas opcionales y hooks

```console
uv run --locked --group parallel pytest -n 2
uv run --locked --group random pytest --randomly-seed=20261016
uv run --locked --group watch ptw --now .
uv run --locked --group hooks prek run --all-files
```

Los hooks requieren un repositorio Git y el entorno preparado. Son feedback local; el pipeline ejecuta sus controles por separado.

Make ofrece atajos opcionales con nombres visibles en `make help`. Las órdenes uv funcionan directamente en PowerShell y shells POSIX.
