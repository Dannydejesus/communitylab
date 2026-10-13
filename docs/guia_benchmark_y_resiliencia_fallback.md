# Guía y Documentación: Exploración Semántica y Resiliencia Fallback

**Autor:** Danny González (Data Scientist — Equipo 39 ONE G10 LATAM)  
**Rama:** `feature/danny-gonzalez-data-scientist`  
**Fecha:** Octubre 2026  
**Relación:** Extensión y validación complementaria sobre la rama experimental `feature/DS-Semana3-Nvidia` (Arnold Bustinza)

---

## 1. Contexto y Propósito

En el marco de la integración experimental de **NVIDIA NIM (Nemotron-3.5-Lightning-30b-a3b)** con fallback automático a **Google Gemini 1.5 Flash**, este aporte aborda dos experimentos claramente diferenciados:

1. **Experimento A — Exploración Semántica de Casos Ambiguos (Cualitativo):**  
   Evaluación exploratoria directa e independiente en 4 interacciones de frontera del dataset (`int-006`, `int-011`, `int-016`, `int-020`) utilizando el prompt productivo oficial (`template_analisis`), sin enviar `tipo_original` al modelo.  
   *Nota Metodológica:* Esta exploración no constituye ground truth ni sustituye la evaluación cuantitativa principal basada en el holdout congelado de 30 casos.

2. **Experimento B — Resiliencia Operacional del Fallback (Técnico):**  
   Endurecimiento de la conmutación en `src/agentes/fallback_ia.py` ante escenarios de degradación transitoria de infraestructura en NVIDIA (HTTP 400 con `DEGRADED` y `FUNCTION`), asegurando que errores 400 genéricos (Bad Request comunes) no activen fallback para no ocultar fallas de petición.

---

## 2. Artefactos del Aporte en el PR #27

| Componente | Ruta | Descripción |
| :--- | :--- | :--- |
| **Resiliencia Fallback** | [`src/agentes/fallback_ia.py`](../src/agentes/fallback_ia.py) | Regla `servicio_degradado` (HTTP 400 + DEGRADED + FUNCTION -> Gemini). |
| **Pruebas de Fallback** | [`tests/agents/test_fallback_analisis.py`](../tests/agents/test_fallback_analisis.py) | Pruebas unitarias para degradación (activa fallback) y 400 normal (no activa fallback). |
| **Script de Benchmark** | [`scripts/benchmark_calibracion_ambiguos.py`](../scripts/benchmark_calibracion_ambiguos.py) | Ejecución directa e independiente con `template_analisis` sin fallback. |
| **Evidencia Exploratoria** | [`docs/benchmark_calibracion_casos_ambiguos.json`](benchmark_calibracion_casos_ambiguos.json) | Salida en JSON con metadata de trazabilidad y respuestas directas de ambos LLMs. |
| **Cuaderno Demostrativo** | [`Com_lab.ipynb`](../Com_lab.ipynb) | Cuaderno de demostración actualizado y alineado con la rama experimental. |

---

## 3. Experimento A: Exploración Semántica de Casos Ambiguos

Se evaluaron los 4 casos límite de manera directa e independiente en ambos proveedores utilizando el prompt oficial:

### Caso 1: `int-006` (Ricardo Mena - `#feedback-programa`)
- **Texto:** *"Sería genial tener más talleres prácticos sobre despliegue de modelos en la nube antes del hackathon."*
- **Dilema:** ¿Sentimiento es neutral o positivo? ¿Tema es cloud_infraestructura o programa_hackathon?
- **Observación:** Ambos modelos identifican el mensaje como constructivo (`positivo` / `feedback`), documentando diferentes matices entre el programa del hackathon y la infraestructura cloud.

### Caso 2: `int-011` (Gabriela Núñez - `#historias-egresados`)
- **Texto:** *"El networking que generé en este programa me abrió puertas para colaborar en proyectos open source."*
- **Dilema:** ¿Tema es comunidad o empleabilidad? ¿Sentimiento es positivo o muy_positivo?
- **Observación:** Ambos coinciden en `muy_positivo` y tipo `testimonio`, mostrando una divergencia comprensible en la temática principal (`empleabilidad` vs `comunidad`). El caso continúa como caso de frontera sujeto a curaduría.

### Caso 3: `int-016` (Isabel Quiroga - `#formulario-testimonios`)
- **Texto:** *"Nunca pensé que podría aprender SQL y Python al mismo tiempo, pero la metodología del curso lo hizo posible."*
- **Observación:** Alta concordancia entre ambos modelos (`muy_positivo`, tema `aprendizaje`, tipo `testimonio`).

### Caso 4: `int-020` (Lucía Paredes - `categoria-programacion-basica`)
- **Texto:** *"Sugiero agregar más ejercicios prácticos antes de pasar al módulo de estructuras de datos, se siente un salto grande."*
- **Dilema:** ¿Sentimiento es negativo o neutral? ¿Sugerencia clasifica como feedback o comentario?
- **Observación:** Se observó convergencia en la intención constructiva (`feedback` con sentimiento `neutral` en ambos proveedores bajo el nuevo prompt oficial).

---

## 4. Experimento B: Resiliencia del Fallback Operacional

Se protege la disponibilidad del sistema distinguiendo errores irrecuperables de problemas transitorios de infraestructura en NVIDIA NIM:
- **HTTP 400 + DEGRADED + FUNCTION:** Conmuta de forma automática y transparente a Google Gemini (`servicio_degradado`).
- **HTTP 400 Estándar (Bad Request):** No activa fallback; se registra el error para permitir la depuración del payload.

---

## 5. Cómo Reproducir en Local

```powershell
# 1. Ejecutar el benchmark exploratorio
python scripts/benchmark_calibracion_ambiguos.py

# 2. Ejecutar pruebas unitarias de fallback
python -m pytest tests/agents/test_fallback_analisis.py -q
```
