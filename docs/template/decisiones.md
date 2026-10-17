# Decisiones técnicas

Evaluación al 16 de octubre de 2026. Las decisiones configuran esta plantilla; cada proyecto puede adaptarlas con sus propias restricciones.

| Decisión | Fundamento y alternativa |
| --- | --- |
| Python 3.15.0 de desarrollo; mínimo 3.14 | Release estable y soporte reciente. 3.14.8 es alternativa comprobada para despliegues o dependencias que la requieran. |
| uv y un lock | Gestión consistente de intérprete, entorno, resolución y ejecución. uv.lock es el formato propio de uv; pylock.toml es un estándar de intercambio distinto. |
| uv_build 0.13.1 | Adecuado para un paquete Python puro y layout sencillo. Se fija la versión del backend en build-system; el lock de aplicación no bloquea por sí mismo el aislamiento de construcción. Hatchling es una alternativa para hooks o layouts más complejos. |
| Ruff | Unifica lint y formato; utiliza la misma resolución local, en hooks y CI. |
| Mypy estricto | Comprobaciones explícitas sin desactivar globalmente imports o definiciones sin tipos. ty y Pyrefly son alternativas a evaluar por diagnósticos e integración. |
| Pytest y coverage de base | Mantiene la suite útil con pocos plugins. Las capacidades adicionales se activan según el proyecto. |
| Prek opcional | Runner de hooks con un formato basado en pre-commit y extensiones propias. Los hooks locales reutilizan el lock; los builtins validan archivos, conflictos y ciertos encabezados de claves privadas. |
| Perfiles optativos | Evita que toda aplicación necesite frameworks web o bibliotecas científicas. |

No se eligió un type checker por su lenguaje de implementación ni por un benchmark ajeno. La velocidad publicada por los autores no demuestra equivalencia de detección de errores. ty 0.0.89 se publica como beta; Pyrefly 1.4.0 se publica como estable. Mypy es la selección de esta plantilla, no una exclusión de las otras herramientas.

## Fuentes

| Fuente | Tipo | Fecha | Aporte |
| --- | --- | --- | --- |
| [Python 3.15.0](https://www.python.org/downloads/release/python-3150/) | Oficial | 2026-10 | Release estable |
| [Python 3.14.8](https://www.python.org/downloads/release/python-3148/) | Oficial | 2026-09 | Alternativa de mantenimiento |
| [uv: grupos](https://docs.astral.sh/uv/concepts/projects/dependencies/) | Documentación oficial | s/f | Selección de dependencias |
| [uv: lock y sync](https://docs.astral.sh/uv/concepts/projects/sync/) | Documentación oficial | s/f | Reproducibilidad |
| [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/) | Documentación oficial | 2026-10 | Construcción y límites |
| [Mypy 2.4](https://mypy.readthedocs.io/en/stable/changelog.html) | Proyecto oficial | 2026-10 | Compatibilidad y diagnósticos |
| [ty: typing FAQ](https://docs.astral.sh/ty/reference/typing-faq/) | Documentación oficial | 2026-10 | Diferencias y plugins |
| [Pyrefly](https://github.com/facebook/pyrefly) | Proyecto oficial | s/f | Alternativa de tipado |
| [Pytest](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | Documentación oficial | s/f | Layout e imports |
| [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/decorators/index.html) | Documentación oficial | s/f | Scopes |
| [pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/pedantic.html) | Documentación oficial | s/f | API pedantic |
| [Prek](https://github.com/j178/prek) | Proyecto oficial | s/f | Hooks |
| [pip-audit](https://github.com/pypa/pip-audit) | Proyecto oficial | s/f | Alcance del escaneo |
| [Metadatos PyPI](https://pypi.org/) | Registro primario | 2026-10 | Versiones y artefactos |

Las releases y especificaciones son evidencia primaria. La disponibilidad de wheels aporta evidencia de distribución, que se complementa con instalación y pruebas locales. Consulta los resultados efectivos y sus límites en [verificación](verificacion.md).
