# Perfiles y dependencias

## Núcleo

`project.dependencies` está vacío. El paquete inicial puede instalarse sin frameworks ni motores analíticos.

`uv sync --locked` incluye el grupo `dev` por defecto. Para instalar el paquete sin herramientas de desarrollo:

```console
uv sync --locked --no-default-groups
```

Para instalar el paquete y únicamente las herramientas de pruebas:

```console
uv sync --locked --no-default-groups --group test
```

`--group test` por sí solo añade el grupo y mantiene los grupos predeterminados. `--only-group test` omite también el proyecto y sus dependencias; resulta adecuado cuando solo se quieren herramientas aisladas.

## Extras de aplicación

- **api:** FastAPI, Uvicorn con complementos estándar y HTTPX. Comprueba un endpoint ASGI en memoria.
- **data:** NumPy, Polars y PyArrow. Comprueba agregación e intercambio Parquet. No prescribe variables, modelos predictivos ni una base de datos de aplicación.

```console
uv sync --locked --extra api
uv run --locked --extra api python scripts/check_profiles.py api
uv sync --locked --extra data
uv run --locked --extra data python scripts/check_profiles.py data
```

Puedes combinar extras. Los ejemplos son perfiles concretos de esta plantilla; se pueden sustituir según el proyecto.

## Herramientas opcionales

| Grupo | Uso |
| --- | --- |
| notebooks | JupyterLab e ipykernel |
| async | pytest-asyncio |
| parallel | pytest-xdist |
| performance | pytest-benchmark |
| property | Hypothesis |
| mock | pytest-mock |
| random | pytest-randomly |
| timeout | pytest-timeout |
| watch | pytest-watcher |
| hooks | prek |
| tools | Validación de YAML |

```console
uv sync --locked --extra data --group notebooks
uv run --locked --extra data --group notebooks jupyter lab
```

Conserva la selección de extras/grupos al usar `uv run`. El lock resuelve todos los perfiles conjuntamente, aunque no se instalen; una dependencia incompatible en un perfil debe corregirse, separarse o declararse conflictiva según el caso.

## Actualización

Los mínimos declarados corresponden a versiones comprobadas al preparar la plantilla. El lock registra versiones exactas. `uv sync --locked` no busca automáticamente las publicaciones más recientes.

`uv lock --upgrade` actualiza la resolución dentro de los rangos. Comprueba los perfiles que cambien antes de aceptar una actualización. La compatibilidad observada cubre los paquetes seleccionados; nuevas bibliotecas científicas, GPU o servicios externos necesitan sus propias verificaciones.
