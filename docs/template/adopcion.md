# Adopción, personalización y cierre

El repositorio de la plantilla conserva su documentación informativa. La aplicación derivada puede retirarla al completar este flujo. La limpieza es una operación separada; cambiar el nombre no elimina las guías.

## 1. Preparar una copia

Copia el contenido publicable o utiliza el repositorio como plantilla. Conserva archivos ocultos como `.github/`, `.python-version`, `.gitignore` y `.pre-commit-config.yaml`. Excluye `temp/`, entornos y resultados generados.

La versión de uv requerida es >=0.13.1,<0.14. Si la instalada es anterior, puedes utilizar `uv tool run --from uv==0.13.1 uv ...` sin actualizarla globalmente.

```console
uv sync --locked
uv run --locked python scripts/check.py
```

## 2. Personalizar

```console
uv run --locked python scripts/bootstrap.py --name ejemplo-servicio --description "Descripción del proyecto" --dry-run
uv run --locked python scripts/bootstrap.py --name ejemplo-servicio --description "Descripción del proyecto"
uv lock
uv sync --locked
uv run --locked ruff format src scripts tests
uv run --locked python -m ejemplo_servicio --version
```

El nombre utiliza minúsculas, números y guiones, comenzando por una letra. El namespace usa guiones bajos. Se rechazan nombres reservados y colisiones con módulos de la biblioteca estándar.

El bootstrap:

- Cambia distribución, namespace y comando.
- Genera una portada de aplicación desde `readme-project.md.in`.
- Genera un CHANGELOG propio desde `changelog-project.md.in`, sin versiones de la plantilla.
- Mantiene intactos los archivos exclusivos de la plantilla y sus hashes.
- Registra el estado de adopción ligado al manifiesto entregado.
- Conserva el lock anterior hasta ejecutar `uv lock`.

La previsualización no escribe archivos. Una segunda ejecución con el mismo nombre es válida; otro renombrado requiere una copia nueva o una migración específica.

Aplica formato después de sincronizar: el nombre elegido puede cambiar la longitud y los saltos de línea del código.

### README propio y procedencia

Si el README ya contiene trabajo propio, el bootstrap se detiene. Utiliza `--keep-readme` para conservarlo y ajusta sus referencias manualmente.

Cuando el repositorio original esté publicado, `--template-url https://github.com/usuario/repositorio` permite añadir su enlace a la portada generada. También puede configurarse en el manifiesto por quien mantiene la plantilla. Sin URL configurada no se inventa un enlace.

### Dos historiales independientes

El `CHANGELOG.md` del repositorio original documenta las versiones de la plantilla. Al adoptar una copia, el bootstrap lo sustituye por una guía de uso con `[Unreleased]` vacío y el nombre del nuevo proyecto. No atribuye a la aplicación las versiones, funcionalidades ni comprobaciones de la base.

Si el archivo ya fue editado, se detiene antes de escribir. Utiliza `--keep-changelog` para conservarlo byte a byte y revisa manualmente su contenido y referencias. Las ejecuciones posteriores con el mismo nombre conservan el historial de la aplicación. Ambos proyectos deciden sus versiones de forma independiente.

El formato conserva la estructura de guía, categorías estándar, resumen por versión y fecha ISO del referente elegido. Las categorías sin contenido se omiten; los enlaces a tags o comparaciones se añaden cuando existan.

## 3. Adaptar el proyecto

Personaliza licencia, contactos, políticas, descripción y versión. Selecciona los perfiles necesarios y desarrolla el comportamiento de la aplicación.

`docs/development/` contiene instrucciones permanentes. Añade allí —o en otras carpetas del proyecto— decisiones y documentación propias. Las guías explicativas de la base permanecen en `docs/template/` mientras las necesites.

## 4. Revisar y aplicar el cierre

```console
uv run --locked python scripts/finalize_template.py --dry-run
uv run --locked python scripts/finalize_template.py --apply
uv run --locked python scripts/check.py
```

El primer comando muestra las rutas concretas y cualquier conflicto. El segundo exige que el plan sea aplicable; no solicita otra confirmación interactiva.

| Se retira del árbol publicable | Se conserva |
| --- | --- |
| Material inventariado de `docs/template/` | `docs/development/` y otras guías de aplicación |
| Pruebas exclusivas de `tests/template/` y su conftest | Pruebas funcionales del proyecto |
| Bootstrap, finalizador y actualizador del inventario | Verificadores de calidad, perfiles y distribución |
| Estado y manifiesto de la adopción | README y CHANGELOG de aplicación, políticas, licencia, código y lock |

Las cachés de Python generadas dentro de las carpetas retirables también aparecen en el plan. No se utiliza un borrado recursivo de `docs/`, `tests/` o `scripts/`.

### Protección del trabajo propio

Los hashes de referencia proceden de la plantilla original. No se recalculan durante bootstrap para tratar modificaciones como originales.

Si una guía fue editada antes o después de personalizar, un archivo nuevo aparece en las carpetas retirables o queda una referencia desde un archivo persistente, el cierre completo se detiene antes de mover archivos.

Conserva o reubica los cambios que quieras mantener. Si se trata de pruebas nuevas, mueve también las fixtures de las que dependan a su ámbito permanente. No hay una opción para forzar la retirada de cambios detectados.

La plantilla original no admite el cierre: primero debe personalizarse una copia.

### Respaldo y recuperación

Los archivos se trasladan a `temp/finalization-<identificador>/files/`. El recibo JSON registra sus rutas y hashes. Ese respaldo local queda excluido de Git y de las distribuciones.

Si un movimiento falla, se intenta restaurar lo trasladado. Si la recuperación no puede completarse, el mensaje conserva la ruta del respaldo para revisar y recuperar los archivos; no se elimina ese respaldo automáticamente.

Después de un cierre correcto los scripts de generación ya no están en el árbol activo. La verificación habitual sigue siendo `scripts/check.py`. No es necesario volver a ejecutar el cierre.

## Mantener el repositorio de la plantilla

Esta sección es para su mantenedor, antes de distribuir una versión nueva:

```console
uv run --locked ruff format src scripts tests
uv run --locked python scripts/update_template_manifest.py
uv run --locked python scripts/check.py
```

El actualizador registra los archivos informativos y utilidades retirables y normaliza sus saltos de línea a LF. Debe ejecutarse después de cambiar ese material. Se rechaza su uso en una copia personalizada.

Una vez conocido el repositorio, el mantenedor puede añadir `--source-url https://github.com/usuario/repositorio`. La URL anterior se conserva al actualizar el inventario sin esa opción.

No regeneres hashes en una aplicación derivada para eludir conflictos de limpieza. Si eliges conservar las explicaciones, puedes mantenerlas y no ejecutar el cierre.

## Compatibilidad y distribución

El mínimo declarado es Python 3.14 y la versión de desarrollo está en `.python-version`. Para otra versión compatible, selecciona explícitamente intérprete y entorno. Las [comprobaciones locales](verificacion.md) delimitan lo realmente probado.

Los frontends JavaScript/TypeScript y los frameworks gráficos tienen configuración propia. Esta base aporta herramientas comunes para la parte Python y perfiles optativos.
