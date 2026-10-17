# Documentación de la plantilla

Estas referencias pertenecen al repositorio que distribuye la base. Se mantienen completas para comprender decisiones y aprender a usarla. Una copia derivada puede retirarlas mediante el cierre explícito de adopción.

## Elegir y entender

- [Guía razonada del boilerplate](python-boilerplate-guide.md): inventario, configuración, calidad, CI y extensiones.
- [Antipatrones y decisiones contextuales](python-project-anti-patterns.md): problemas verificables, alternativas y excepciones.
- [Decisiones técnicas](decisiones.md): opciones elegidas y fuentes.
- [Reporte de fundamentación](evaluacion-tecnica.md): recomendación técnica y decisión de adopción.
- [Verificación](verificacion.md): resultados y límites.

## Adoptar una copia

- [Adopción, bootstrap y cierre](adopcion.md).
- `readme-project.md.in`: portada inicial que genera el bootstrap.
- `changelog-project.md.in`: historial inicial del proyecto, con guía y Unreleased vacío.
- `manifest.json`: inventario y hashes del material retirable.
- `state.json`: estado generado sólo al personalizar una copia.

## Aprender a probar

- [Guía de fundamentos](testing-guide.md).
- [Patrones avanzados](testing-patterns.md).
- [Referencia de comandos](testing-commands.md).

## Documentación que permanece

[docs/development](../development/README.md) contiene las instrucciones operativas del proyecto. También permanecen README, CONTRIBUTING, SECURITY, CHANGELOG, licencia, código, verificadores y pruebas funcionales.

El cierre retira sólo material propio identificado en el manifiesto. Si ese material contiene modificaciones o archivos nuevos, detiene la operación para conservarlos. No se regenera el manifiesto en una aplicación para eludir esa protección.
