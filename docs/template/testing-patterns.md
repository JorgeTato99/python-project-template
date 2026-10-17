# Patrones avanzados de testing

Los ejemplos son recetas para adaptar a contratos reales. Las capacidades opcionales se instalan por grupo; consulta [perfiles](../development/perfiles.md). La [guía fundamental](testing-guide.md) desarrolla fixtures, scopes y aislamiento.

## Async: strict y auto

En modo strict, declara tests y fixtures asíncronos explícitamente:

```python
import pytest
import pytest_asyncio

@pytest_asyncio.fixture
async def service():
    resource = {"ready": True}
    yield resource

@pytest.mark.asyncio
async def test_service(service):
    assert service["ready"]
```

Con el grupo `async`, el plugin permite elegir modo auto para un proyecto centrado en asyncio. Esa elección no debe aplicarse globalmente sin considerar otros backends asíncronos.

### Recursos compartidos y loops

```python
@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def shared():
    yield {"ready": True}

@pytest.mark.asyncio(loop_scope="module")
async def test_shared(shared):
    assert shared["ready"]
```

El loop que sostiene la fixture no puede tener un alcance menor que su vida útil. Evita mezclar un recurso de módulo con un runner limitado a una función. La base no instala opciones de asyncio globales cuando el plugin es opcional.

### Concurrencia y cancelación

```python
import asyncio

async def load_all(ids, fetch):
    return await asyncio.gather(*(fetch(item) for item in ids))
```

El test debe controlar `fetch` y comprobar resultados o errores esperados. `return_exceptions=True` cambia el contrato de errores; no es una estrategia automática de tolerancia.

`asyncio.timeout` o `wait_for` permiten límites cooperativos. Un timeout del runner es una protección distinta; no sustituye un diseño de cancelación o cierre del recurso.

## Mock, spy y ubicación del patch

Con el grupo `mock`, `mocker` gestiona restauración. Un mock sustituye comportamiento; un spy también observa llamadas, pero ejecuta el comportamiento real.

Si el módulo bajo prueba hace `from client import send`, el patch normalmente se aplica al nombre `send` de ese módulo. Parchear otro módulo donde se definió originalmente puede no cambiar la referencia utilizada.

No intentes parchear como atributo de módulo una función declarada sólo dentro de un test.

### AsyncMock

```python
from unittest.mock import AsyncMock
import pytest

@pytest.mark.asyncio
async def test_fetch_contract():
    fetch = AsyncMock(return_value={"id": "a"})
    result = await fetch("a")
    assert result == {"id": "a"}
    fetch.assert_awaited_once_with("a")
```

El ejemplo requiere el grupo `async`. Para una prueba real, inyecta el doble en el componente que lo consume. Este fragmento sólo ilustra la API del doble.

### Side effects

Una secuencia de resultados sirve para representar reintentos conocidos. Una excepción puede representar un fallo de la dependencia. Comprueba también el comportamiento final y el número permitido de llamadas; no conviertas un reintento infinito en una prueba verde.

Un context manager de patch acota su vida útil. `monkeypatch` es suficiente para muchos cambios de entorno o atributos sin instalar pytest-mock.

## Parametrización

### Casos e IDs

```python
import pytest

@pytest.mark.parametrize(
    ("value", "expected"),
    [pytest.param(0, 0, id="zero"), pytest.param(-2, 4, id="negative")],
)
def test_square(value, expected):
    assert value * value == expected
```

La operación es ilustrativa. En aplicación importa la función real y selecciona límites relevantes.

### Producto cartesiano

Dos decoradores parametrize combinan casos. Úsalo cuando todas las combinaciones sean pertinentes; un producto grande puede generar coste sin añadir clases de comportamiento nuevas.

### Casos válidos e inválidos

Puedes agruparlos con `pytest.raises` y un contexto que no espere excepción, o separarlos para comunicar contratos diferentes. Los IDs deben permitir identificar el caso fallido.

### Fixtures parametrizadas

`@pytest.fixture(params=[...])` varía recursos compartidos por familias de tests. No nombres motores de base de datos que el proyecto no instala como si fueran recursos ya disponibles.

## Benchmarking

### Región medida y corrección

El fixture `benchmark` recibe una función y argumentos. Prepara fuera de esa llamada aquello que no quieras medir y comprueba después el resultado.

Un benchmark puede ser correcto funcionalmente y poco representativo. Registra versiones, entradas, repeticiones, concurrencia, materialización y condiciones de caché.

### Pedantic y setup

```python
def test_sum(benchmark):
    result = benchmark.pedantic(
        sum,
        setup=lambda: (([1, 2, 3],), {}),
        iterations=1,
        rounds=2,
    )
    assert result == 6
```

El setup devuelve `(args, kwargs)`. Con setup utiliza `iterations=1`. Este ejemplo comprueba la API; no define una metodología suficiente para comparar sistemas.

### Operaciones async

La región medida debe incluir el trabajo esperado. Pasar directamente una función async a un medidor síncrono puede medir sólo la creación de la coroutine.

Define un adaptador o una metodología que espere la operación y declare si incluye creación del loop, setup y teardown.

### Guardar y comparar

```console
uv run --locked --group performance pytest --benchmark-only --benchmark-save=baseline
uv run --locked --group performance pytest --benchmark-only --benchmark-compare=baseline
```

Una diferencia porcentual requiere interpretar variabilidad y magnitud absoluta. No se fija un umbral universal de regresión.

## Cobertura

Distingue líneas ejecutadas de ramas y de corrección del comportamiento. Una cobertura alta no demuestra aserciones útiles ni detección de todos los fallos.

La fuente configurada debe corresponder al paquete real. Las ejecuciones en otros procesos no quedan cubiertas automáticamente por medir el proceso principal.

No excluyas `__init__`, `__main__` o excepciones por costumbre. Justifica las exclusiones que necesite el proyecto.

Los reportes HTML/XML y JUnit tienen propósitos distintos: JUnit comunica resultados de pruebas; coverage comunica qué código se observó.

## Paralelismo y aislamiento

Con el grupo `parallel`, xdist puede distribuir pruebas. Las fixtures de sesión existen por worker; no representan necesariamente un singleton de toda la ejecución.

Usa recursos aislados por ejecución y worker, transacciones o servicios temporales según el caso. Un identificador de worker por sí solo no garantiza un puerto libre o un nombre global único entre ejecuciones simultáneas.

Mantén la colección de tests consistente entre workers. Al diagnosticar un fallo, reproduce primero en serie y luego con la configuración paralela pertinente.

Los benchmarks competitivos se ejecutan por separado y en serie. No se promete un factor de aceleración fijo para xdist.

## Mantenimiento de la suite

- Conserva casos de regresión con el escenario que fallaba.
- Evita depender del orden de otros tests para setup o limpieza.
- Mantén las fixtures con responsabilidad y alcance claros.
- Utiliza esperas por condiciones con límite cuando corresponda; los sleeps arbitrarios no acreditan disponibilidad.
- Revisa qué demuestra cada aserción al modificar la implementación.

## Fuentes

Consulta 2026-10-16.

| Fuente | Fecha | Aporte |
| --- | --- | --- |
| [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/decorators/index.html) | s/f | Scopes y decoradores |
| [unittest.mock](https://docs.python.org/3.14/library/unittest.mock.html) | s/f | Ubicación de patch y AsyncMock |
| [pytest parametrización](https://docs.pytest.org/en/stable/how-to/parametrize.html) | s/f | Casos y fixtures |
| [pytest-benchmark pedantic](https://pytest-benchmark.readthedocs.io/en/latest/pedantic.html) | s/f | Contrato de setup |
| [Coverage](https://coverage.readthedocs.io/en/latest/) | s/f | Alcance de medición |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/en/stable/) | s/f | Distribución y aislamiento |
