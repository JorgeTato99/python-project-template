# Verificación de la plantilla

Fecha de comprobación: **2026-10-16**, horario de Ciudad de México. Plataforma local: **Windows x86-64**, CPython convencional con GIL.

| Control | Python 3.14.8 | Python 3.15.0 |
| --- | --- | --- |
| Suite del núcleo | 42 aprobadas | 42 aprobadas |
| Mypy estricto | Correcto | Correcto |
| Ruff: lint y formato | Correcto | Correcto |
| Bandit | Sin hallazgos activos | Sin hallazgos activos |
| Wheel instalado sin modo editable | Correcto | Correcto |
| Reconstrucción del sdist | Correcta | Correcta |
| Perfil API: petición ASGI | Correcto | Correcto |
| Perfil datos: agregación y Parquet | Correcto | Correcto |
| Notebooks: importación de componentes | Correcta | Correcta |
| Contratos de plugins | 5 en paralelo + 1 en serie | 5 en paralelo + 1 en serie |
| Configuración de hooks | Válida | Válida |

Los controles negativos de tipado detectaron un retorno incompatible y una definición sin anotaciones. El control negativo de Bandit detectó `eval` y devolvió un código de fallo. La suite comprueba que el verificador se detiene ante el primer error.

La auditoría de Python 3.15.0 examinó el entorno completo de perfiles/herramientas: **153 distribuciones inventariadas, una distribución local editable omitida y cero vulnerabilidades conocidas reportadas**. Es un resultado fechado de pip-audit, sujeto a la cobertura y actualización de sus fuentes.

Se comprobó una copia personalizada con otro nombre: previsualización, renombrado, regeneración del lock, sincronización, formato y verificación completa. Los ocho hooks de prek pasaron sobre los archivos de esa copia en un repositorio Git temporal, con Python 3.15.0. También se construyeron sdist/wheel mediante el camino estándar PEP 517, además del camino de construcción normal de uv.

## Qué significan las mediciones

Las pruebas de plugins comprueban compatibilidad de sus APIs y ejecución. El ejemplo de benchmark utiliza una operación mínima para comprobar la herramienta; sus tiempos no sustentan una comparación de Python ni de motores analíticos.

La cobertura del reporte de pytest corresponde a esa ejecución de la suite. Los scripts de distribución y perfiles se ejecutan además en procesos independientes; sus líneas no se agregan automáticamente a esa cobertura. No se presenta el porcentaje parcial como cobertura integral del sistema.

## Límites

- La matriz de GitHub Actions está configurada para Windows/Linux y ambas versiones; **la ejecución remota y Linux quedan pendientes de publicar el repositorio y ejecutar CI**.
- No se comprobó macOS, ARM, PyPy, free threading ni versiones futuras de Python.
- La comprobación de notebooks importa JupyterLab/ipykernel; no valida toda la interfaz, extensiones o flujos de notebooks de un usuario.
- La API se verifica mediante transporte ASGI en memoria; no representa una prueba de despliegue, base de datos ni infraestructura.
- Los perfiles son selecciones concretas. Otras bibliotecas de ML/GPU, frameworks gráficos o servicios necesitan verificación adicional.
- El backend y el entorno se fijan por versión; no se ha demostrado identidad byte a byte de todos los artefactos entre equipos.

## Reproducir

```console
uv sync --locked
uv run --locked python scripts/check.py
uv sync --locked --all-extras --all-groups
uv run --locked --no-sync python scripts/check_profiles.py api
uv run --locked --no-sync python scripts/check_profiles.py data
uv run --locked --no-sync python scripts/check_profiles.py notebooks
uv run --locked --no-sync python scripts/check_capabilities.py
uv run --locked --no-sync pip-audit --skip-editable
```

Para repetir en 3.14.8, selecciona ese intérprete y otro entorno mediante `UV_PROJECT_ENVIRONMENT`. El procedimiento de CI especifica ambos explícitamente.

La evidencia resumida publicable está en [validacion.json](evidencia/validacion-inicial.json). El trabajo local conserva inventarios de origen, notas de investigación, logs y verificaciones anteriores bajo `temp/`, que se excluye de Git y de las distribuciones.
