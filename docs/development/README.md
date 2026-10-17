# Desarrollo del proyecto

Esta documentación permanece en el proyecto y debe actualizarse conforme cambien sus comandos, dependencias y comportamiento.

## Preparar el entorno

```console
uv sync --locked
uv run --locked python scripts/check.py
```

La configuración declara un mínimo de Python y selecciona una versión de desarrollo mediante `.python-version`. Las versiones resueltas están en `uv.lock`.

## Referencias operativas

- [Comandos de desarrollo](comandos.md).
- [Perfiles y dependencias](perfiles.md).
- [Pruebas](pruebas.md).
- [Recetas de testing](recetas-testing.md).
- [Contribuir](../../CONTRIBUTING.md).
- [Política de seguridad](../../SECURITY.md).

## Convenciones

Los identificadores de código utilizan inglés; los comentarios y la documentación de esta base utilizan español. Mantén una convención coherente en tu equipo.

La estructura `src/` corresponde al paquete instalable. Añade pruebas para los comportamientos y límites reales de la aplicación. Los scripts de comprobación propagan los errores y no aplican correcciones de formato automáticamente.

Registra aquí decisiones de operación específicas: configuración de servicios, recursos necesarios, migraciones, ejecución de la aplicación y diagnóstico. Los perfiles disponibles son opciones que pueden adaptarse o sustituirse.
