# Evaluación y fundamentación de la plantilla reutilizable para proyectos Python

| Campo | Información |
| --- | --- |
| Identificador | RT-02 |
| Proyecto | python-project-template |
| Fecha | 2026-10-16 |
| Versión | 1.1 |
| Estado | Plantilla implementada y comprobada localmente; adopción por Sofía pendiente |
| Emisor | Evaluación técnica |
| Destinataria y responsable de adopción | Sofía |

## 1. Síntesis y recomendación

**Recomendamos esta plantilla como base de ingeniería para nuevos proyectos Python**, seleccionando los perfiles que correspondan. Ofrece un paquete instalable, dependencias resueltas, pruebas, tipos, análisis de código y comprobaciones portables desde una misma configuración.

La configuración principal utiliza **CPython 3.15.0**, con soporte desde **3.14** y una alternativa comprobada en **3.14.8**. La decisión se fundamenta en releases oficiales, disponibilidad de distribuciones compatibles e instalación y ejecución locales. Las pruebas del núcleo y los perfiles seleccionados pasaron en ambas versiones sobre Windows.

La plantilla contiene herramientas para construir proyectos; la arquitectura, los modelos científicos y la infraestructura de una aplicación derivada se deciden según sus necesidades. La elección final de adopción corresponde a Sofía.

## 2. Objetivo y alcance

**Pregunta de decisión:** ¿qué base común permite iniciar proyectos Python actuales con instalación, calidad y verificación consistentes, sin exigir un tipo único de aplicación?

El alcance incluye versión de Python, configuración de proyecto, resolución de dependencias, construcción, tipado, pruebas, hooks y CI. API y datos son extras de aplicación; notebooks y plugins adicionales son herramientas opcionales.

Los criterios son compatibilidad ejecutable, corrección de los controles, mantenimiento, claridad de adopción y separación de responsabilidades. No se selecciona un frontend JavaScript/TypeScript, una base de datos de aplicación, un conjunto completo de ciencia de datos ni un despliegue específico.

## 3. Opciones priorizadas

| Prioridad | Opción | Fundamento | Cuándo elegirla | Límite |
| --- | --- | --- | --- | --- |
| 1 | Plantilla con Python 3.15.0 | Release estable reciente y comprobación local satisfactoria del núcleo y perfiles. | Proyecto nuevo cuyo conjunto de dependencias y destino admitan esta versión. | Verificar las bibliotecas o plataformas que se añadan. |
| 2 | La misma plantilla con Python 3.14.8 | Alternativa de mantenimiento con las mismas comprobaciones locales correctas. | Restricciones de proveedor, dependencias o plataforma que aconsejen 3.14. | Conservar la selección explícita del intérprete y comprobar las nuevas dependencias. |

En herramientas, la configuración elegida es uv, uv_build, Ruff, mypy estricto y pytest/coverage. ty y Pyrefly son alternativas pertinentes para tipado según diagnósticos, integración y necesidades del editor; no se les asigna un puesto por velocidad publicada. Hatchling es una alternativa de construcción si se requieren hooks o un layout más complejo.

## 4. Evidencia y resultados

Se combinaron investigación primaria, auditoría del material de origen, instalación del grafo de dependencias y comprobaciones funcionales.

| Evidencia local | Resultado | Alcance |
| --- | --- | --- |
| Suite de la plantilla | 68 pruebas correctas por intérprete | Windows, Python 3.14.8 y 3.15.0 |
| API, datos y notebooks | Comprobaciones correctas en ambas versiones | ASGI en memoria, agregación/Parquet e importaciones de notebooks |
| Plugins de pruebas | 5 contratos con dos workers y 1 ejecución serial por intérprete | Async, scopes, mocking, Hypothesis, timeout y benchmark pedantic |
| Distribución | Wheel instalado en entorno limpio y sdist reconstruido | Ambas versiones; importación fuera del checkout |
| Controles negativos | Errores de tipado y uso de eval detectados | Confirma que los controles pueden fallar |
| Auditoría de dependencias | Cero vulnerabilidades conocidas reportadas | Entorno completo 3.15.0, una distribución editable omitida |

Las releases y capacidades descritas en las fuentes son **evidencia primaria**; los resultados anteriores son **comprobaciones locales**. La preferencia de configuración es **juicio técnico** basado en esa evidencia.

Se corrigieron o sustituyeron ejemplos heredados que mezclaban scopes incompatibles, trataban marcadores como objetos, aplicaban patches sobre funciones locales inexistentes o usaban incorrectamente benchmark pedantic. Los comandos ahora propagan fallos y las instalaciones distinguen extras, grupos predeterminados y grupos aislados.

**No se realizó un benchmark comparativo de rendimiento entre Python 3.14 y 3.15.** La pregunta principal de esta evaluación es compatibilidad y funcionamiento de una base de desarrollo. Los tiempos de una operación mínima del plugin de benchmark no se interpretan como evidencia de superioridad de un intérprete.

## 5. Implicaciones y límites

El beneficio práctico es comenzar con una configuración coherente que puede instalarse, probarse, personalizarse y distribuirse. El núcleo no instala frameworks web ni motores analíticos; cada proyecto activa o sustituye sus perfiles.

El lock fija la resolución de dependencias del entorno. El backend de construcción se fija además a uv_build 0.13.1 en build-system, porque el aislamiento de construcción tiene su propia resolución.

La adopción requiere personalizar identidad, documentación, licencia, contactos, dependencias y criterios de pruebas. Las guías informativas se conservan en la plantilla; la copia genera un README de aplicación y dispone de un cierre explícito que protege modificaciones y conserva respaldo local. El personalizador ofrece previsualización y realiza un renombrado inicial consistente; una migración posterior de identidad se trata por separado.

La comprobación local corresponde a Windows x86-64 con GIL. La matriz Linux/Windows de GitHub Actions está preparada, y su ejecución remota está pendiente de publicar el repositorio. La comprobación de notebooks no cubre toda su interfaz; la API no representa un despliegue real. Las bibliotecas que se añadan necesitan sus propias comprobaciones.

## 6. Fuentes y anexos

| Fuente | Tipo | Fecha | Aporte |
| --- | --- | --- | --- |
| [Python 3.15.0](https://www.python.org/downloads/release/python-3150/) | Oficial | 2026-10 | Release estable |
| [Python 3.14.8](https://www.python.org/downloads/release/python-3148/) | Oficial | 2026-09 | Alternativa de mantenimiento |
| [uv: dependencias](https://docs.astral.sh/uv/concepts/projects/dependencies/) | Documentación oficial | s/f | Grupos y extras |
| [uv: construcción](https://docs.astral.sh/uv/concepts/build-backend/) | Documentación oficial | 2026-10 | Backend y alcance |
| [Pytest: integración](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | Documentación oficial | s/f | Layout e imports |
| [Mypy](https://mypy.readthedocs.io/en/stable/changelog.html) | Proyecto oficial | 2026-10 | Compatibilidad del analizador |
| [pip-audit](https://github.com/pypa/pip-audit) | Proyecto oficial | s/f | Alcance de la auditoría |

- [Decisiones y fuentes complementarias](decisiones.md).
- [Resultados, reproducción y límites](verificacion.md).
- [Resumen de evidencia](evidencia/validacion.json).
- [Adopción y personalización](adopcion.md).
- [Perfiles](../development/perfiles.md) y [pruebas](../development/pruebas.md).
- [Recetas de pruebas](../development/recetas-testing.md).

## 7. Decisión final de Sofía

**Recomendamos adoptar la plantilla con Python 3.15.0 y los perfiles que correspondan al proyecto.** Python 3.14.8 es una alternativa comprobada cuando las restricciones del entorno lo aconsejen.

**La elección final corresponde a Sofía**, quien puede valorar estas opciones y adaptar las herramientas según sus necesidades de análisis y desarrollo.

| Registro de decisión | Estado |
| --- | --- |
| Adopción de la plantilla | Por definir por Sofía |
| Versión de Python | Por registrar |
| Perfiles y ajustes | Por registrar |
| Fecha de selección | Por registrar |
