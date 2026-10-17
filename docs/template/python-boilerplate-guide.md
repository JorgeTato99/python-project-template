# Guía razonada del boilerplate Python

Esta referencia explica qué aporta cada pieza y cómo extenderla. El procedimiento completo está en [adopción](adopcion.md); los comandos diarios permanecen en [desarrollo](../development/README.md).

## Alcance y lectores

La base sirve para iniciar proyectos Python con instalación, calidad, pruebas y distribución comunes. Un backend, una aplicación gráfica o un proyecto de datos puede compartir ese núcleo y elegir componentes diferentes.

El repositorio conserva material para entender la plantilla. Una copia derivada puede retirarlo después de adoptar las decisiones. La aplicación conserva sus instrucciones, políticas y comprobaciones.

## Inventario por responsabilidad

| Pieza | Responsabilidad | Adaptación habitual |
| --- | --- | --- |
| `pyproject.toml` | Metadatos, dependencias y configuración de herramientas | Nombre, descripción, versiones y perfiles |
| `uv.lock` | Resolución concreta | Actualización controlada y revisión del diff |
| `.python-version` | Intérprete de desarrollo | Versión acordada y comprobada |
| `src/` | Paquete instalable | Código e interfaces de aplicación |
| `tests/` | Comprobaciones del proyecto | Casos de negocio y límites |
| `scripts/check.py` | Secuencia portable de validadores | Controles adecuados al proyecto |
| `scripts/verify_distribution.py` | Instalación no editable y sdist | Artefactos y alcance de construcción |
| `scripts/check_profiles.py` | Contratos representativos de perfiles | Bibliotecas efectivamente elegidas |
| `scripts/check_capabilities.py` | APIs de plugins optativos | Capacidades de testing necesarias |
| `docs/development/` | Operación del proyecto | Convenciones y comandos vigentes |
| `docs/template/` | Explicación y adopción de la base | Material retirable en la copia derivada |
| `tests/template/` | Contratos de las utilidades de generación | Se retiran con esas utilidades |

### Archivos de entorno y repositorio

`.editorconfig` comunica convenciones al editor. No ejecuta lint ni cambia por sí mismo todos los archivos existentes.

`.gitattributes` regula aspectos como tratamiento de texto y saltos de línea en Git. `.gitignore` evita que los archivos coincidentes se añadan normalmente; no elimina contenido ya versionado ni constituye un control de acceso.

`.env.example` documenta variables previstas. No carga automáticamente un archivo `.env`: la aplicación debe elegir e implementar ese mecanismo.

`py.typed` comunica que la distribución publica información de tipos. Los consumidores deben recibir el archivo dentro del paquete.

## Cómo leer pyproject.toml

### Construcción

`[build-system]` elige el backend y sus requisitos. uv actúa como frontend de construcción; uv_build produce los artefactos de esta base Python pura.

Una aplicación con extensiones nativas propias o un proceso de build especial puede necesitar otro backend. Consumir una dependencia compilada no significa que la aplicación deba compilar una extensión propia.

### Metadatos y dependencias de aplicación

`[project]` contiene nombre, versión, descripción, README, licencia y mínimo de Python. `dependencies` es una **clave de tipo array dentro de esa tabla**, no una tabla `[project.dependencies]`.

```toml
[project]
name = "ejemplo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
```

`[project.optional-dependencies]` agrupa extras que un consumidor puede activar. `[project.scripts]` publica comandos de la distribución.

### Herramientas y grupos

`[dependency-groups]` declara herramientas de desarrollo no distribuidas como requisitos del paquete. La composición mediante `include-group` evita repetir listas.

`[tool.*]` configura herramientas concretas. El mínimo de Python del proyecto y los objetivos de analizadores deben ser coherentes, aunque el intérprete elegido para desarrollo sea más reciente.

[Guía de pyproject de PyPA](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [grupos de dependencias](https://packaging.python.org/en/latest/specifications/dependency-groups/).

## Operaciones de dependencias con uv

| Operación | Propósito |
| --- | --- |
| `uv add paquete` | Declarar una dependencia directa y resolver |
| `uv add --group test paquete` | Declarar una herramienta en un grupo |
| `uv remove paquete` | Retirar una dependencia directa |
| `uv lock` | Resolver según manifiesto y preferencias del lock existente |
| `uv lock --upgrade` | Buscar actualizaciones dentro de rangos |
| `uv sync --locked` | Instalar la selección sin actualizar el lock |
| `uv run --locked ...` | Preparar la selección y ejecutar un comando |
| `uv export` | Producir un formato de intercambio según su selección |

`dev` se incluye por defecto en esta base. `--group` añade grupos; `--no-default-groups` cambia la selección inicial. `--only-group` también omite el proyecto. Consulta [perfiles](../development/perfiles.md) para ejemplos concretos.

El lock conserva dependencias transitivas. No es necesario declararlas todas como directas: añade aquellas cuya API o comportamiento consume deliberadamente el proyecto.

## Calidad: controles complementarios

| Control | Pregunta |
| --- | --- |
| Lint | ¿Hay patrones problemáticos según las reglas elegidas? |
| Formato | ¿El texto cumple el estilo automático? |
| Tipado | ¿Las interfaces y operaciones respetan las anotaciones analizadas? |
| Pruebas | ¿El comportamiento observado cumple sus contratos? |
| Bandit | ¿Aparecen patrones de seguridad incluidos en sus reglas? |
| Auditoría | ¿Las distribuciones analizadas tienen avisos conocidos en las fuentes consultadas? |
| Distribución | ¿El paquete se instala y ejecuta fuera del checkout? |

Ninguno de estos controles reemplaza a todos los demás. `check.py` ordena los controles locales y conserva códigos de salida; la auditoría de dependencias se ejecuta mediante su comando adicional. El Makefile es un conjunto opcional de atajos; los comandos uv también funcionan directamente en PowerShell.

La verificación usa modos de comprobación. Aplicar `ruff format` o `ruff check --fix` es una operación explícita de edición.

## Hooks y CI

Los hooks de prek proporcionan feedback antes del commit. Los locales utilizan herramientas del entorno preparado; los builtins están ligados a la versión del runner. Los detalles vigentes están en [CONTRIBUTING](../../CONTRIBUTING.md).

La configuración de GitHub Actions contiene:

- **core:** controles, pruebas y distribución en la matriz.
- **profiles:** contratos de API, datos, notebooks y plugins.
- **check:** agregación del resultado de jobs anteriores.
- Artefactos de pruebas y cancelación de ejecuciones supersedidas.
- Permisos declarados y Actions fijadas por SHA.

La configuración de una matriz es una intención de ejecución. [Verificación](verificacion.md) identifica lo realmente ejecutado.

Dependabot propone actualizaciones de las dependencias gestionadas por uv y de Actions. La versión fijada del ejecutable uv se revisa por separado. Una propuesta requiere revisión y comprobaciones; su existencia no acredita compatibilidad.

## Documentación comunitaria

| Archivo | Para qué sirve |
| --- | --- |
| README | Presentar el proyecto y permitir comenzar |
| CONTRIBUTING | Explicar el flujo de contribución |
| SECURITY | Delimitar soporte, contacto y controles |
| CHANGELOG | Comunicar cambios relevantes |
| CODE_OF_CONDUCT | Expresar acuerdos de convivencia |
| LICENSE | Publicar los términos elegidos |

Una aplicación derivada debe personalizar contactos y políticas. El volumen de gobernanza se adapta a sus usuarios y mantenimiento; esta plantilla no obliga a crear procesos empresariales para cada script.

## Adopción y cierre

El bootstrap genera una portada orientada al proyecto. Las guías informativas permanecen disponibles mientras se adoptan las decisiones.

El cierre es una operación independiente: previsualiza archivos concretos, comprueba hashes y conserva respaldo local. No retira código o documentación nuevos del usuario. Un conflicto requiere conservar o reubicar esos cambios antes de volver a aplicar.

El manifiesto y sus hashes los mantiene el autor de la plantilla. No se deben regenerar en una aplicación derivada para eludir conflictos de limpieza.

## Extensiones razonables

Añade componentes al necesitar su comportamiento:

- Persistencia y migraciones, si existe almacenamiento de aplicación.
- Servidor y framework, si existe una API.
- Interfaces gráficas o frontend separado, según producto.
- Contenedores y despliegue, según destino.
- Reglas de cobertura y tipos según riesgo.
- Bibliotecas científicas y reproducción de experimentos según análisis.

Un árbol de carpetas extenso no aporta arquitectura por sí mismo. Las decisiones deben explicar responsabilidades y cómo se verificarán.

## Fuentes

Consulta 2026-10-16; documentos vivos con fecha editorial s/f.

| Fuente | Fecha | Aporte |
| --- | --- | --- |
| [PyPA pyproject](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) | 2026-10 | Metadatos y sintaxis |
| [Dependency groups](https://packaging.python.org/en/latest/specifications/dependency-groups/) | 2024-10 | Semántica estándar |
| [uv: proyectos](https://docs.astral.sh/uv/guides/projects/) | s/f | Flujo de trabajo |
| [uv: construcción](https://docs.astral.sh/uv/concepts/build-backend/) | 2026-10 | Backend y archivos |
| [Git attributes](https://git-scm.com/docs/gitattributes) | s/f | Tratamiento de archivos |
| [Git ignore](https://git-scm.com/docs/gitignore) | s/f | Exclusiones de seguimiento |
