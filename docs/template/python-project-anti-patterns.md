# Antipatrones y decisiones de herramientas en proyectos Python

Esta guía recupera y actualiza la referencia original del boilerplate. Distingue problemas verificables de preferencias de herramientas. La configuración elegida de esta plantilla es una recomendación concreta; otras combinaciones pueden ser adecuadas.

Consulta técnica: 2026-10-16. Las versiones y pruebas de esta base se documentan en [decisiones](decisiones.md) y [verificación](verificacion.md). El procedimiento de adopción está en [adopción](adopcion.md).

## 1. Dependencias: intención, resolución y entorno

Son tres cosas diferentes:

| Capa | Qué expresa | En esta plantilla |
| --- | --- | --- |
| Declaración | Dependencias directas y rangos aceptados | `pyproject.toml` |
| Resolución | Versiones concretas y artefactos elegidos | `uv.lock` |
| Entorno | Lo instalado para un intérprete y selección | `.venv/` |

### Problema: dos listas manuales que compiten

Mantener versiones distintas a mano en `pyproject.toml` y `requirements.txt` puede producir entornos incompatibles. El síntoma es que instalación local, CI y despliegue resuelven conjuntos diferentes.

La convención elegida es declarar en el manifiesto, resolver con uv y conservar el lock. Si un proveedor necesita requirements, un archivo **generado** mediante exportación es una salida de interoperabilidad válida; documenta qué grupos/extras incluye y cómo se regenera. [Exportación de uv](https://docs.astral.sh/uv/concepts/projects/export/).

### Problema: usar un snapshot como única declaración del proyecto

`pip freeze` describe paquetes instalados; no decide qué dependencias eran directas ni constituye por sí solo un resultado de resolución. Sirve para diagnóstico o captura de un entorno conocido. Un listado con paquetes transitorios y herramientas locales puede ocultar la intención original. [Documentación de pip freeze](https://pip.pypa.io/en/stable/cli/pip_freeze/).

### Problema: actualizar sin verificar el resultado

Un rango abierto puede admitir nuevas versiones mayores. La actualización debe revisar lock, notas de versiones y casos del proyecto:

```console
uv lock --upgrade
uv sync --locked
uv run --locked python scripts/check.py
```

El lock no se vuelve obsoleto porque aparezca una publicación nueva. `--locked` comprueba coherencia con el manifiesto; no obliga a instalar lo más reciente del índice.

## 2. Entornos e intérpretes

### Problema: instalar o ejecutar con otro Python

Un comando puede funcionar en una consola y fallar en CI porque resuelve otro intérprete o entorno. Comprueba el ejecutable utilizado:

```console
uv run --locked python -c "import sys; print(sys.executable); print(sys.version)"
```

La plantilla fija una versión de desarrollo y declara un mínimo compatible. No son el mismo concepto.

### pip, venv y virtualenv son opciones válidas

Usar `venv` y pip no es obsoleto. Python documenta entornos virtuales y permite invocar directamente su intérprete sin activarlos. La elección de uv aquí coordina resolución, entorno y ejecución; reduce pasos manuales y facilita una convención común. [Python venv](https://docs.python.org/3.14/library/venv.html), [virtualenv](https://virtualenv.pypa.io/en/latest/).

El riesgo que se evita es alterar un Python compartido o instalar fuera del entorno esperado por accidente.

### Problema: describir incorrectamente la selección de grupos

- `uv sync --locked` incluye `dev` por defecto en esta configuración.
- `--group test` añade ese grupo y conserva los predeterminados.
- `--no-default-groups --group test` instala el proyecto y ese grupo.
- `--only-group test` omite también el proyecto y sus dependencias.
- `uv sync` sincroniza de forma exacta por defecto; `uv run` es inexacto por defecto en la versión documentada.

Conserva los extras/grupos necesarios al ejecutar. `--no-sync` usa el entorno existente; su presencia no demuestra por sí sola que esté preparado. [uv: lock y sincronización](https://docs.astral.sh/uv/concepts/projects/sync/).

## 3. Lint, formato y cambios automáticos

### Problema: varias herramientas reescriben la misma decisión

Dos formatters con criterios diferentes pueden cambiar repetidamente los mismos archivos. Elige una autoridad de formato por ámbito y coordina los cambios de configuración.

Ruff reúne lint y formato para esta base. Black, isort, Flake8 y otros plugins pueden formar una combinación válida; hay que valorar reglas necesarias, compatibilidad y coste de mantenerla. Ruff documenta diferencias respecto a Black. [Ruff formatter](https://docs.astral.sh/ruff/formatter/), [Black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html).

Prettier soporta Markdown y YAML. Añadirlo o evitarlo depende del conjunto de lenguajes y del renderizado esperado; una incidencia concreta no invalida todos sus usos. [Formatos de Prettier](https://prettier.io/docs/).

### Problema: confundir comprobar con corregir

```console
uv run --locked ruff check src scripts tests
uv run --locked ruff format --check src scripts tests
```

Estas órdenes verifican. Para modificar explícitamente:

```console
uv run --locked ruff check src scripts tests --fix
uv run --locked ruff format src scripts tests
```

Un pipeline que arregla silenciosamente el árbol puede terminar verde sin demostrar que la revisión recibida ya cumplía las convenciones.

## 4. CI y resultados verdes engañosos

### Problema: ocultar códigos de salida

Añadir `|| true` a una comprobación de seguridad transforma un hallazgo en éxito del shell. La plantilla propaga el primer fallo y prueba controles que deben fallar.

### Problema: atribuir al pipeline más alcance del ejecutado

Una matriz configurada no demuestra que todos sus casos hayan pasado. Registra sistema operativo, intérprete, selección de dependencias y resultado real. Una prueba en Windows no acredita Linux, free threading o GPU.

### Problema: resolver dependencias distintas en cada job

Usa el lock en las instalaciones y ejecuciones del pipeline. Los cachés aceleran el acceso a artefactos; no sustituyen la resolución ni las comprobaciones.

`actions/setup-python` con pip es una alternativa válida y soporta caché. En este repositorio se elige setup-uv por coherencia con el flujo local, sin atribuir un factor de aceleración no medido. [setup-python](https://github.com/actions/setup-python).

## 5. Hooks y mantenimiento

Los hooks dan feedback local. Pueden omitirse y requieren preparación del entorno; CI debe ejecutar los controles relevantes.

Los hooks locales de esta plantilla reutilizan herramientas del lock. Así se evita que el formatter del commit y el del pipeline usen versiones diferentes sin intención.

Prek utiliza un formato basado en pre-commit y añade extensiones. El bloque `repo: builtin` no se puede trasladar sin adaptación al runner pre-commit. Sus builtins van ligados a la versión de prek instalada. [Compatibilidad de prek](https://prek.j178.dev/compatibility/).

`detect-private-key` reconoce ciertos encabezados; no acredita detección general de tokens o contraseñas. El alcance de cada control debe quedar explícito.

## 6. Tipado y confianza en el gate

### Problema: silenciar globalmente el código que interesa revisar

`ignore_missing_imports`, exclusiones amplias o `Any` propagado pueden convertir el análisis en una comprobación débil. Es preferible resolver imports, documentar límites de terceros y aplicar excepciones acotadas cuando proceda.

La plantilla utiliza mypy estricto para sus fuentes y scripts. Eso no sustituye las pruebas ni demuestra corrección de bibliotecas que no se analizan.

### Sintaxis y herramientas según el mínimo soportado

`list[str]` y `dict[str, int]` son adecuados para el mínimo de esta base. Un proyecto que soporte intérpretes antiguos puede tener restricciones distintas.

Mypy, ty y Pyrefly deben valorarse por diagnósticos, configuración, librerías y editor. El lenguaje de implementación o un benchmark ajeno no acredita equivalencia de detección. [Mypy](https://mypy.readthedocs.io/en/stable/), [FAQ de ty](https://docs.astral.sh/ty/reference/typing-faq/).

Un control negativo con un error conocido ayuda a comprobar que el gate puede fallar; no prueba toda la corrección del analizador.

## 7. Construcción y publicación

### Problema: utilizar comandos de empaquetado deprecados

Se distingue entre un archivo `setup.py` utilizado por un backend y ejecutar su CLI histórica para instalar o distribuir. PyPA documenta las sustituciones de esos comandos; setuptools y su configuración siguen teniendo usos válidos. [Discusión de PyPA](https://packaging.python.org/en/latest/discussions/setup-py-deprecated/).

### Problema: un wheel que sólo funciona en el checkout

Construye y verifica una instalación no editable fuera del directorio de trabajo. Comprueba también que el sdist pueda reconstruirse y que no incluya entornos, datasets ni evidencia local.

```console
uv build
uv run --locked python scripts/verify_distribution.py
```

El lock de aplicación no fija por sí mismo el entorno aislado de construcción. El backend está fijado explícitamente en esta plantilla. Eso no demuestra identidad binaria entre todas las plataformas. [Construcción en uv](https://docs.astral.sh/uv/concepts/projects/build/).

### Publicar es otra operación

Twine sigue siendo una herramienta válida de comprobación y publicación. uv ofrece una vía integrada. La elección exige revisar destino, artefactos, permisos y autenticación; construir no publica nada. [Twine](https://twine.readthedocs.io/en/stable/), [guía de paquetes de uv](https://docs.astral.sh/uv/guides/package/).

## Cómo usar esta referencia

Ante una práctica, identifica el problema observable, el contexto, una alternativa y cómo comprobarla. Las convenciones elegidas pueden ser firmes sin convertir todas las alternativas en errores.

Esta guía pertenece al repositorio de la plantilla. El cierre de una copia derivada puede retirarla junto con los demás documentos explicativos, preservando la documentación operativa del proyecto.
