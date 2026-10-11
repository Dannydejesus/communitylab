# Guía y Documentación de Benchmark Semántico y Resiliencia Fallback

**Autor:** Danny González (Data Scientist — Equipo 39 ONE G10 LATAM)  
**Rama:** `feature/danny-gonzalez-data-scientist`  
**Fecha:** Octubre 2026  
**Relación:** Extensión y validación empírica sobre la actualización NVIDIA NIM (`feature/DS-Semana3-Nvidia` de Arnold Bustinza)

---

## 1. Contexto y Propósito

Tras la integración del adaptador **NVIDIA NIM (Nemotron-3.5-Lightning-30b-a3b)** con fallback automático a **Google Gemini**, surge la necesidad de evaluar dos aspectos críticos de Ciencia de Datos e Ingeniería:

1. **Estabilidad Semántica en Casos Límite Ambiguos:**  
   En `docs/registro_cambios_y_decisiones.md` se identificaron 4 casos del dataset con dilemas de etiquetado humano (`int-006`, `int-011`, `int-016`, `int-020`). Es indispensable medir cómo se comportan ambos modelos (NIM vs Gemini) ante la sutileza de estos textos.
2. **Resiliencia Operativa del Fallback (`src/agentes/fallback_ia.py`):**  
   Durante pruebas en vivo se identificó que errores transitorios de degradación en la infraestructura de NIM (HTTP 400 por función en estado `DEGRADED`) interrumpían el flujo si no estaban explícitamente contemplados en la política de degradación controlada.

---

## 2. Artefactos y Ubicación de Cambios

Los integrantes del equipo pueden revisar directamente los siguientes archivos en la rama `feature/danny-gonzalez-data-scientist`:

| Componente | Ruta | Descripción |
| :--- | :--- | :--- |
| **Script de Benchmark** | [`scripts/benchmark_calibracion_ambiguos.py`](../scripts/benchmark_calibracion_ambiguos.py) | Herramienta CLI de evaluación comparativa automatizada multi-modelo. |
| **Reporte de Resultados** | [`docs/benchmark_calibracion_casos_ambiguos.json`](benchmark_calibracion_casos_ambiguos.json) | Salida serializada en JSON con las respuestas estructuradas de Nemotron y Gemini. |
| **Resiliencia Fallback** | [`src/agentes/fallback_ia.py`](../src/agentes/fallback_ia.py) | Captura de errores 400 por estado `DEGRADED` de endpoints de inferencia para conmutar a Gemini. |
| **Ajuste Configuración** | [`src/agentes/configuracion_ia.py`](../src/agentes/configuracion_ia.py) | Corrección en la lectura de variables de entorno respetando aislamiento de pruebas unitarias. |
| **Cuaderno Demostrativo** | [`Com_lab.ipynb`](../Com_lab.ipynb) | Cuaderno interactivo actualizado con el resumen de estado y evidencia. |

---

## 3. Resultados del Benchmark Empírico

El benchmark evalúa los 4 casos límite y genera las siguientes conclusiones:

### Caso 1: `int-006` (Ricardo Mena - `#feedback-programa`)
- **Texto:** *"Sería genial tener más talleres prácticos sobre despliegue de modelos en la nube antes del hackathon."*
- **Dilema:** ¿Sentimiento es neutral o positivo? ¿Tema es cloud_infraestructura o programa_hackathon?
- **Comportamiento observado:** Ante latencia prolongada o timeout de NIM, el fallback conmuta a Gemini:
  - Sentimiento: `positivo`
  - Tema Principal: `programa_hackathon`
  - Subtema: `talleres de despliegue`
  - Tipo Detectado: `feedback`

### Caso 2: `int-011` (Gabriela Núñez - `#historias-egresados`)
- **Texto:** *"El networking que generé en este programa me abrió puertas para colaborar en proyectos open source."*
- **Dilema:** ¿Tema es comunidad o empleabilidad? ¿Sentimiento es positivo o muy_positivo?
- **Convergencia Multi-Modelo:**
  - **Nemotron (NIM):** Sentimiento `muy_positivo` | Tema `empleabilidad` | Subtema `networking` | Tipo `testimonio`.
  - **Gemini:** Sentimiento `muy_positivo` | Tema `comunidad` | Subtema `networking y colaboración` | Tipo `testimonio`.
  - *Conclusión:* Ambos modelos coinciden en el sentimiento extremo positivo y la naturaleza testimonial, divergiendo sutilmente en el enfoque temático (empleabilidad vs comunidad), ambos válidos según el prisma del analista.

### Caso 3: `int-016` (Isabel Quiroga - `#formulario-testimonios`)
- **Texto:** *"Nunca pensé que podría aprender SQL y Python al mismo tiempo, pero la metodología del curso lo hizo posible."*
- **Convergencia:**
  - **Nemotron (NIM):** Sentimiento `muy_positivo` | Tema `aprendizaje` | Subtema `SQL Python` | Tipo `testimonio`.
  - **Gemini:** Sentimiento `muy_positivo` | Tema `aprendizaje` | Subtema `metodologia de estudio` | Tipo `testimonio`.
  - *Conclusión:* Consistencia idéntica de alto valor para curaduría.

### Caso 4: `int-020` (Lucía Paredes - `categoria-programacion-basica`)
- **Texto:** *"Sugiero agregar más ejercicios prácticos antes de pasar al módulo de estructuras de datos, se siente un salto grande."*
- **Dilema:** ¿Sentimiento es negativo o neutral? ¿Sugerencia clasifica como feedback o comentario?
- **Divergencia Semántica:**
  - **Nemotron (NIM):** Sentimiento `positivo` | Tipo `comentario`.
  - **Gemini:** Sentimiento `neutral` | Tipo `feedback`.
  - *Conclusión para el equipo:* Para fines de gobernanza en curaduría (Data Analyst), Gemini captura con mayor precisión la intención constructiva (`feedback` con sentimiento `neutral`).

---

## 4. Cómo Ejecutar el Benchmark en Local

Para replicar o extender este análisis con otros mensajes o modelos:

```powershell
# 1. Asegurar entorno virtual activo
.\venv\Scripts\Activate.ps1

# 2. Ejecutar script de benchmark
python scripts/benchmark_calibracion_ambiguos.py

# 3. Validar que la suite de tests se mantenga 100% en verde
pytest -q
```

---

## 5. Preguntas Abiertas para Feedback del Equipo

Invitamos a los compañeros del equipo a revisar y comentar:
- **@Arnold (DS):** ¿Consideras conveniente añadir `int-020` como caso de prueba formal en los fixtures de fallback para documentar la diferencia en tipo de activo generado?
- **@Jhonattan (DA):** Desde la óptica de ingesta y curaduría, ¿prefieres que sugerencias del tipo `int-020` sigan etiquetándose como `feedback` o como `comentario`?
- **@Ramses (Arquitectura):** Confirmar si el código de error `servicio_degradado` en `fallback_ia.py` se alinea con la taxonomía de observabilidad en OCI.
