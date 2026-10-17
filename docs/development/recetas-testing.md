# Recetas de pruebas

Estas recetas muestran patrones para adaptar a código real. Los contratos de los plugins se verifican con `scripts/check_capabilities.py`; los fragmentos ilustrativos no representan cobertura de una aplicación.

## Organización

Los tests unitarios pueden replicar los módulos fuente. Añade integración, regresión o end-to-end cuando haya comportamiento que comprobar. Un test de regresión debe llamar a la función real corregida y reproducir el escenario del fallo.

## Archivos temporales y logs

Utiliza las fixtures incorporadas de pytest en lugar de reconstruirlas:

```python
def test_export(tmp_path):
    path = tmp_path / "salida.txt"
    path.write_text("contenido", encoding="utf-8")
    assert path.read_text(encoding="utf-8") == "contenido"

def test_logs(caplog):
    import logging
    with caplog.at_level(logging.INFO):
        logging.getLogger("example").info("procesado")
    assert "procesado" in caplog.text
```

## Parametrización y límites

```python
import pytest

@pytest.mark.parametrize("value", ["", " ", "../otra-ruta"])
def test_rejects_invalid_value(value):
    with pytest.raises(ValueError):
        validate(value)
```

Sustituye `validate` por una función real y selecciona clases de entrada y límites del dominio.

## Mocking

`monkeypatch` forma parte de pytest. `pytest-mock` es opcional y ofrece el fixture `mocker`.

```python
def test_mock(mocker):
    mocked = mocker.patch("math.sqrt", return_value=4)
    import math
    assert math.sqrt(16) == 4
    mocked.assert_called_once_with(16)
```

En código de negocio aplica el patch donde se consulta el nombre. Una función local a otro test no constituye un atributo del módulo sobre el que hacer patch.

## Async y recursos compartidos

Instala el grupo `async` y utiliza scopes compatibles. El ejemplo completo está en [pruebas](pruebas.md). Para un recurso por función, conserva `scope="function"` y `loop_scope="function"`. Para un recurso compartido a nivel módulo, ambos pueden ser `module`.

No dependas del orden de ejecución de tests para inicializar o limpiar recursos.

## Propiedades

Con el grupo `property`:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=-1000, max_value=1000), max_size=20))
def test_reordering(values):
    assert sum(values) == sum(reversed(values))
```

En una aplicación sustituye esta propiedad ilustrativa por invariantes reales y conserva los casos mínimos que revelen bugs.

## Benchmark pedantic

Con el grupo `performance`:

```python
def test_pedantic(benchmark):
    result = benchmark.pedantic(
        sum,
        setup=lambda: (([1, 2, 3],), {}),
        iterations=1,
        rounds=2,
    )
    assert result == 6
```

Aquí se comprueba la API. Un estudio de rendimiento necesita entradas representativas, número de repeticiones justificado, corrección de resultados, aislamiento y registro de condiciones.

Ejecuta benchmarks en serie; utiliza xdist para pruebas funcionales cuando haya aislamiento de recursos. Para operaciones async, incluye la ejecución esperada dentro de la región medida.

## End-to-end e integración

Una prueba end-to-end utiliza los componentes reales del flujo seleccionado; construir diccionarios dentro del test solo ejemplifica assertions.

Crea datos de prueba aislados, utiliza recursos temporales y define la limpieza mediante fixtures con `yield`, considerando fallos previos al yield y terminaciones forzadas. Las conexiones, permisos y credenciales se configuran específicamente para el entorno de pruebas.
