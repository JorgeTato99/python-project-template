# Pruebas

Las pruebas comprueban el paquete, sus comandos y herramientas de validación. Añade los contratos del comportamiento real de la aplicación y conserva el aislamiento de recursos.

## Base

```console
uv run --locked pytest
uv run --locked pytest --cov --cov-report=term-missing
```

Se utiliza importlib para importar pruebas y un paquete instalado con estructura `src/`. Los directorios de pruebas no requieren ajustes de `sys.path`.

No se fija un porcentaje universal de cobertura. La cobertura inicial describe las herramientas y el paquete de ejemplo; un proyecto derivado debe establecer sus umbrales y añadir casos de negocio.

## Capacidades opcionales

Instala los grupos que utilices. La configuración base no exige plugins opcionales.

```console
uv run --locked --group parallel pytest -n 2
uv run --locked --group random pytest --randomly-seed=20261016
uv run --locked --group timeout pytest --timeout=30
uv run --locked --group watch ptw --now .
```

Para async, decora las pruebas con `pytest.mark.asyncio`. Una fixture asíncrona compartida entre pruebas debe declarar un `loop_scope` al menos tan amplio como su `scope`:

```python
import pytest
import pytest_asyncio

@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def resource():
    yield {"initialized": True}

@pytest.mark.asyncio(loop_scope="module")
async def test_resource(resource):
    assert resource["initialized"]
```

`request.config.getini("markers")` devuelve una lista de definiciones como strings; no son objetos con atributo `name`. Para mocking, aplica el patch sobre el nombre que realmente consulta el código y sobre atributos existentes.

## Rendimiento

`pytest-benchmark` es opcional. Separa las mediciones de rendimiento de las comprobaciones funcionales y evita ejecutar benchmarks competitivos en paralelo.

Con `benchmark.pedantic`, un `setup` devuelve `(args, kwargs)` y se utiliza `iterations=1` si hay setup. Un benchmark de una función async debe incluir la ejecución/espera de la operación: medir la creación de una coroutine no mide su trabajo.

No se promete un factor de aceleración universal para xdist ni para otras herramientas.

## Comprobación de plugins

`scripts/check_capabilities.py` ejercita async, scopes compartidos, mocking, property testing, benchmark pedantic, timeouts y dos workers de xdist en un directorio temporal. Se ejecuta con los grupos instalados explícitamente:

```console
uv run --locked --group async --group parallel --group performance --group property --group mock --group timeout python scripts/check_capabilities.py
```

Es una prueba de compatibilidad funcional de plugins, no un benchmark comparativo de motores ni de versiones de Python.
