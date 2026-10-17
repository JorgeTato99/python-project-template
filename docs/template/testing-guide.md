# Guía de fundamentos de testing

Esta guía explica cómo diseñar y organizar pruebas. Los comandos operativos están en [desarrollo](../development/pruebas.md); la [referencia de comandos](testing-commands.md) y los [patrones](testing-patterns.md) amplían los ejemplos.

## Empezar por un comportamiento

Una prueba necesita una entrada, una operación y una expectativa observable. Conviene separar Arrange, Act y Assert sin convertir esas etiquetas en comentarios obligatorios.

```python
def divide(total: int, count: int) -> float:
    if count == 0:
        raise ValueError("count debe ser distinto de cero")
    return total / count

def test_divide_preserves_fraction():
    result = divide(7, 2)
    assert result == 3.5
```

En un proyecto real importa la función desde el paquete. Copiar su implementación dentro del test puede hacer que la prueba pase aunque la aplicación siga rota.

Para el caso inválido:

```python
import pytest

def test_divide_rejects_zero():
    with pytest.raises(ValueError, match="distinto de cero"):
        divide(7, 0)
```

Los fragmentos de esta guía son ejemplos didácticos; adapta la función importada y el contrato a la aplicación.

## Descubrimiento, instalación e imports

Pytest busca en `tests/` y reconoce `test_*.py` en esta configuración. El paquete se instala con estructura `src/`; el modo importlib no instala nada por sí mismo.

Si un import falla, comprueba intérprete, sincronización y nombre del paquete antes de modificar `sys.path`. `python -m pytest` es una invocación válida; la convención aquí es ejecutarla dentro del entorno de uv.

[Prácticas de integración](https://docs.pytest.org/en/stable/explanation/goodpractices.html), [modos de importación](https://docs.pytest.org/en/stable/explanation/pythonpath.html).

## Organización por responsabilidades

Type + Mirror es una opción útil cuando ayuda a localizar pruebas por módulo:

```text
src/paquete/services/orders.py
tests/unit/services/test_orders.py
```

También es válido organizar por feature o contrato. Crea categorías cuando haya pruebas que las necesiten; un árbol de directorios vacío no aporta cobertura.

| Categoría | Qué busca comprobar |
| --- | --- |
| Unit | Una unidad con dependencias controladas |
| Integration | Colaboración con otros componentes o recursos |
| End-to-end | Un flujo seleccionado con componentes reales |
| Smoke | Disponibilidad básica de capacidades críticas |
| Regression | Un escenario que antes produjo un defecto |

Las categorías se pueden solapar. Una regresión puede ser una prueba lenta de integración; su nombre no impone un tiempo máximo.

## Fixtures y composición

Una fixture prepara algo que una prueba necesita:

```python
import pytest

@pytest.fixture
def item():
    return {"id": "sample", "active": True}

def test_item_is_active(item):
    assert item["active"] is True
```

Las fixtures pueden depender de otras fixtures. Es preferible componer recursos pequeños a preparar todo el sistema para cada test.

Las incorporadas `tmp_path`, `monkeypatch`, `capsys` y `caplog` cubren muchos casos sin plugins adicionales. Consulta las [recetas](../development/recetas-testing.md).

## Scopes y aislamiento

| Scope | Reutilización |
| --- | --- |
| function | Una instancia por prueba |
| class | Compartida por la clase |
| module | Compartida por módulo |
| package | Compartida por paquete de pruebas |
| session | Compartida dentro de la sesión de ese proceso |

Un recurso más compartido puede reducir setup y aumentar acoplamiento. No selecciones `session` sólo por ser costoso: comprueba aislamiento, mutabilidad y concurrencia.

Una fixture amplia no puede depender indiscriminadamente de otra más estrecha. En async también importa el alcance del event loop.

## Setup, yield y teardown

```python
@pytest.fixture
def resource():
    handle = open_resource()
    try:
        yield handle
    finally:
        handle.close()
```

`open_resource` representa una API de la aplicación. El bloque posterior al yield se intenta cuando la fixture llegó a proporcionar el recurso. Un fallo previo al yield o una terminación forzada requiere considerar otros mecanismos de recuperación.

Agrupa cada adquisición con su liberación. Context managers o finalizadores pueden ser apropiados según la API. [Teardown de fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#handling-errors-for-yield-fixture).

## conftest jerárquico

Una fixture de `tests/conftest.py` es visible para sus descendientes. Un conftest de una subcarpeta limita fixtures a ese ámbito y puede especializar las heredadas.

Esta base sitúa las fixtures exclusivas de generación en `tests/template/`. Al cerrar la adopción se retira esa familia completa; las pruebas funcionales no dependen de sus fixtures.

Para compartir fixtures entre módulos comienza por composición y conftest. Extraer un plugin requiere una ruta importable y registro explícito; evita wildcard imports entre archivos de pruebas.

## Markers y selección

Registra un marker antes de utilizarlo bajo `--strict-markers`. La plantilla registra `integration`; una aplicación puede añadir otros.

`request.config.getini("markers")` devuelve definiciones como strings. No son objetos con atributo `name`.

`-m` filtra expresiones de markers; `-k` selecciona por nombres y expresiones. La selección puede dejar pruebas fuera: registra el comando al comunicar resultados.

## Qué merece una prueba

Prioriza entradas inválidas, límites, invariantes y efectos observables. Una prueba puede incluir varias aserciones del mismo contrato.

Mocks y stubs ayudan a controlar dependencias, pero una suite que sólo comprueba sus propios mocks no acredita las integraciones reales. Complementa con contratos relevantes de esas integraciones.

Un test de regresión debe reproducir el caso del defecto y fallar si se revierte la corrección.

## Diagnóstico de fallos frecuentes

| Síntoma | Comprobar | Siguiente acción |
| --- | --- | --- |
| No se recolectan pruebas | `--collect-only`, nombres y testpaths | Corregir descubrimiento o selección |
| Opción desconocida | Plugin y grupo instalado | Añadir el grupo requerido al comando |
| Fixture no encontrada | Nombre y conftest visible | Ajustar ámbito o registro |
| Import fallido | Intérprete, paquete instalado y namespace | Sincronizar el entorno correcto |
| ScopeMismatch | Dependencias y scopes de fixtures | Reducir alcance o hacerlos compatibles |
| Async no ejecutado | Plugin, modo y decoradores | Configurar explícitamente el patrón elegido |
| Sólo falla en conjunto | Estado global, recursos y orden | Aislar y probar con orden distinto |
| Cobertura inesperada | Source, proceso y selección | Distinguir qué se midió |
| CI difiere del equipo | OS, Python, extras y lock | Reproducir esas condiciones |

## Fuentes

Consulta 2026-10-16.

| Fuente | Fecha | Aporte |
| --- | --- | --- |
| [pytest: integración](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | s/f | Paquetes y descubrimiento |
| [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) | s/f | Composición y ciclo de vida |
| [pytest: invocación](https://docs.pytest.org/en/stable/how-to/usage.html) | s/f | Selección y diagnóstico |
| [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/decorators/index.html) | s/f | Fixtures y loops |
