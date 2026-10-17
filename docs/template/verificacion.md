# Verificación de la plantilla

Comprobación local: **Windows x86-64**, CPython convencional con GIL. La actualización de documentación y cierre de adopción conserva las dependencias ya seleccionadas.

| Control | Python 3.14.8 | Python 3.15.0 |
| --- | --- | --- |
| Suite completa de la plantilla | 72 aprobadas | 72 aprobadas |
| Mypy estricto | Correcto | Correcto |
| Ruff: lint y formato | Correcto | Correcto |
| Bandit | Sin hallazgos activos | Sin hallazgos activos |
| Wheel no editable y reconstrucción del sdist | Correctos | Correctos |
| Adopción y cierre de otra copia | Correctos | Correctos |
| Verificación completa del proyecto después del cierre | Correcta | Correcta |

La suite incluye pruebas de generación de README y CHANGELOG propios, preservación explícita de un historial editado y conservación del historial ante ejecuciones repetidas. También comprueba previsualización sin escrituras, preservación de cambios anteriores y posteriores al bootstrap, contenido nuevo, referencias persistentes, rechazo de rutas ajenas, symlinks/junctions de Windows y recuperación ante fallos inyectados.

El flujo integral crea una copia, personaliza su identidad, regenera el lock, instala el entorno, aplica formato, previsualiza el cierre, lo aplica y ejecuta `scripts/check.py` en el proyecto resultante. Las pruebas exclusivas de generación ya no forman parte de ese proyecto.

## Git y saltos de línea

Una prueba adicional preparó un índice Git y exportó los archivos con `core.autocrlf=true`. Bootstrap y previsualización del cierre pasaron sobre esa exportación. Los patrones de atributos fijan LF también para el asset `.md.in`.

El material informativo y sus utilidades tienen hashes versionados. La sincronización del manifiesto es una tarea de mantenimiento de la plantilla; no modifica la evidencia para permitir borrar cambios de una aplicación.

## Controles conservados de la fase inicial

La [verificación inicial](verificacion-inicial.md) conserva el resultado previo a esta reorganización:

- Contratos de API, datos y notebooks comprobados en ambas versiones.
- Cinco contratos funcionales de plugins en paralelo y uno de benchmark API en serie por versión.
- Controles negativos de mypy y Bandit.
- Auditoría del entorno completo 3.15.0: 153 distribuciones inventariadas, una editable omitida y cero vulnerabilidades conocidas reportadas.
- Construcción normal y mediante el camino estándar PEP 517.
- Ocho hooks comprobados en una copia personalizada.

Es evidencia fechada de esas dependencias y operaciones, no una auditoría nueva ni un inventario del árbol reorganizado. Los hashes iniciales corresponden al snapshot de aquella fase.

## Cobertura y alcance

La cobertura de pytest describe el proceso medido; algunos verificadores se ejercitan además en otros procesos. No se presenta el porcentaje como cobertura integral ni se utiliza un umbral universal de suficiencia.

Los ejemplos del plugin de benchmark comprueban su API. Sus tiempos no sustentan una comparación entre intérpretes o motores de datos.

## Límites

- La matriz de GitHub Actions está configurada para Windows/Linux y ambas versiones; la ejecución remota y Linux quedan pendientes de publicar y ejecutar CI.
- No se comprobó macOS, ARM, PyPy, free threading ni versiones futuras.
- La prueba de notebooks importa sus componentes; no comprueba todas sus interfaces o extensiones.
- La API usa transporte ASGI en memoria; no representa un despliegue.
- Bibliotecas, servicios o perfiles añadidos por una aplicación necesitan su propia comprobación.
- El pin de versiones no demuestra identidad byte a byte de artefactos entre equipos.

## Reproducción

En la plantilla original:

```console
uv sync --locked
uv run --locked python scripts/check.py
```

El flujo de adopción y cierre se documenta en [adopción](adopcion.md). Los comandos posteriores al cierre permanecen en [desarrollo](../development/README.md).

El resumen vigente está en [validacion.json](evidencia/validacion.json). La [evidencia inicial](evidencia/validacion-inicial.json) y su snapshot se conservan como historial. Los logs detallados y los fixtures de esta sesión permanecen bajo `temp/`, excluidos de Git y de las distribuciones.
