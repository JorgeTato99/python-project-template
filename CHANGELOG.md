# Changelog

Todas las modificaciones notables de **python-project-template** se documentan en este archivo.

El formato se basa en [Keep a Changelog 1.1.0](https://keepachangelog.com/es-ES/1.1.0/)
y las versiones siguen [Semantic Versioning 2.0.0](https://semver.org/lang/es/).

## 📖 Guía de uso

### Documentar cambios

Registrar cambios terminados en `[Unreleased]`. Usar las categorías estándar y
crear únicamente las que tengan contenido:

| Categoría | Uso |
| --- | --- |
| ✨ Added | Funcionalidades nuevas. |
| 🔄 Changed | Cambios en comportamiento existente. |
| ⚠️ Deprecated | Funcionalidades disponibles cuya retirada se anuncia. |
| 🗑️ Removed | Funcionalidades retiradas. |
| 🐛 Fixed | Correcciones de comportamiento incorrecto. |
| 🔒 Security | Correcciones de vulnerabilidades identificadas. |

- Escribir para quien usa el proyecto: explicar qué cambia y su efecto.
- Empezar las entradas con verbos en infinitivo: agregar, corregir, retirar.
- Agrupar cambios relacionados y enlazar issues o documentación cuando aporten contexto.
- Marcar incompatibilidades con **⚠️ BREAKING** e indicar cómo migrar.
- Reservar Security para vulnerabilidades corregidas; una mejora preventiva corresponde a Changed.
- Documentar resultados reales; no presentar planes o controles configurados como comprobaciones ejecutadas.

### Publicar una versión

1. Mover el contenido de Unreleased a `## [X.Y.Z] - YYYY-MM-DD - Título breve`.
2. Añadir `### 🎯 Resumen` con el propósito de la versión y los límites de compatibilidad relevantes.
3. Mantener las categorías no vacías. Usar subapartados `####` si ayudan a agrupar cambios.
4. Sincronizar la versión del paquete, sus metadatos y el lock cuando corresponda.
5. Conservar Unreleased vacío para el siguiente ciclo, con versiones recientes primero.
6. Añadir enlaces a tags o comparaciones cuando existan; no inventar referencias.
7. Conservar el historial publicado; registrar las correcciones posteriores en una versión nueva.

| Etapa | Criterio de incremento |
| --- | --- |
| Desarrollo inicial `0.y.z` | Usar `0.Y.0` para funcionalidad significativa o incompatibilidades y `0.y.Z` para correcciones compatibles. Es una convención del proyecto; SemVer considera inestable esta etapa. |
| API estable `>=1.0.0` | MAJOR para incompatibilidades, MINOR para funcionalidad compatible y deprecaciones, PATCH para correcciones compatibles. |

El primer registro de versión de un proyecto nuevo puede ser `0.1.0`.
El historial debe reflejar sus propias entregas, con fecha ISO 8601.

Este archivo registra el **historial de la plantilla**. Al personalizar una copia,
el bootstrap genera un CHANGELOG propio desde un formato inicial sin estas
versiones. Si ya existe un historial editado, exige conservarlo explícitamente
con `--keep-changelog`. La versión del proyecto derivado evoluciona de forma independiente.

## [Unreleased]

## [0.1.0] - 2026-10-17 - Base reutilizable para proyectos Python

### 🎯 Resumen

**Tipo de release:** Feature (primera publicación).

Establecer la primera versión pública de la plantilla: paquete instalable,
herramientas comunes de desarrollo y perfiles opcionales, con personalización
y cierre de adopción que preservan el trabajo de la aplicación.

**Compatibilidad:** desarrollar con CPython 3.15.0 y admitir Python desde 3.14.
Las verificaciones locales cubren Windows x86-64 con 3.14.8 y 3.15.0.
El estado de la matriz remota se mantiene en la documentación de verificación.

### ✨ Added

#### Paquete y herramientas

- Incorporar paquete instalable con comando de consola, información de tipos y
  comprobación del wheel fuera del directorio fuente.
- Separar el núcleo sin dependencias de aplicación de los extras de API y datos,
  y ofrecer grupos opcionales de notebooks, hooks y plugins de pruebas.
- Incorporar controles portables de tipos, lint, formato, seguridad, pruebas y
  construcción, con verificación de la reconstrucción del sdist.

#### Adopción y documentación

- Personalizar distribución, namespace y comando con previsualización sin escrituras.
- Generar README y CHANGELOG de aplicación sin heredar el historial de esta base;
  permitir conservar archivos propios mediante opciones explícitas.
- Añadir cierre de adopción con inventario de hashes, bloqueo ante modificaciones,
  comprobación de referencias y respaldo local recuperable.
- Preservar cambios previos y posteriores a la personalización, rechazar rutas
  ajenas, enlaces y junctions y recuperar archivos ante fallos de escritura o traslado.
- Recuperar guías de fundamentos, antipatrones y patrones de testing, separando
  el material informativo de la plantilla de la documentación permanente de desarrollo.

### 🔄 Changed

- Actualizar la base heredada a Python 3.15.0 con mínimo 3.14, uv 0.13.1 y
  resolución de dependencias conservada en uv.lock.
- Centralizar la configuración de herramientas en pyproject.toml y aplicar mypy estricto.
- Sustituir comandos heredados por instrucciones que distinguen extras y grupos
  de uv y conservan la selección del entorno al ejecutar las herramientas.

### 🐛 Fixed

- Propagar los códigos de fallo de los controles de calidad y seguridad para
  evitar que una comprobación fallida se presente como correcta.
