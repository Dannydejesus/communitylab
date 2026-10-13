"""Benchmark exploratorio de calibración semántica entre NVIDIA NIM y Gemini."""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Asegurar path raíz del proyecto
raiz = Path(__file__).resolve().parent.parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

load_dotenv(override=True)

from src.agentes.prompts.analisis import template_analisis
from src.agentes.modelo_ia import obtener_modelo_analisis_estructurado
from src.agentes.modelos import AnalisisMensaje

# Casos límite ambiguos para exploración cualitativa (no ground truth)
CASOS_AMBIGUOS = [
    {
        "id": "int-006",
        "autor": "Ricardo Mena",
        "origen": "slack",
        "canal": "#feedback-programa",
        "idioma": "es",
        "texto": "Sería genial tener más talleres prácticos sobre despliegue de modelos en la nube antes del hackathon.",
        "dilema": "¿Sentimiento es neutral o positivo? ¿Tema es cloud_infraestructura o programa_hackathon?"
    },
    {
        "id": "int-011",
        "autor": "Gabriela Núñez",
        "origen": "discord",
        "canal": "#historias-egresados",
        "idioma": "es",
        "texto": "El networking que generé en este programa me abrió puertas para colaborar en proyectos open source.",
        "dilema": "¿Tema es comunidad o empleabilidad? ¿Sentimiento es positivo o muy_positivo?"
    },
    {
        "id": "int-016",
        "autor": "Isabel Quiroga",
        "origen": "formulario_web",
        "canal": "#formulario-testimonios",
        "idioma": "es",
        "texto": "Nunca pensé que podría aprender SQL y Python al mismo tiempo, pero la metodología del curso lo hizo posible.",
        "dilema": "¿Sentimiento es positivo o muy_positivo? ¿Tema es aprendizaje o programacion?"
    },
    {
        "id": "int-020",
        "autor": "Lucía Paredes",
        "origen": "foro_alumnos",
        "canal": "categoria-programacion-basica",
        "idioma": "es",
        "texto": "Sugiero agregar más ejercicios prácticos antes de pasar al módulo de estructuras de datos, se siente un salto grande.",
        "dilema": "¿Sentimiento es negativo o neutral? ¿Sugerencia clasifica como feedback o comentario?"
    }
]

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

def construir_cadena(proveedor: str):
    """Construye la cadena productiva: template_analisis | modelo."""
    modelo = obtener_modelo_analisis_estructurado(
        AnalisisMensaje,
        proveedor=proveedor,
    )
    return template_analisis | modelo

def ejecutar_benchmark():
    print("=" * 80, flush=True)
    print("[*] BENCHMARK EXPLORATORIO DE CALIBRACION SEMANTICA (DATA SCIENCE)", flush=True)
    print("Evaluacion cualitativa directa e independiente en 4 casos ambiguos", flush=True)
    print("Prompt productivo: template_analisis (sin tipo_original en input)", flush=True)
    print("=" * 80, flush=True)

    try:
        cadena_nim = construir_cadena("nvidia_nim")
    except Exception as e:
        print(f"Aviso cargando cadena NVIDIA NIM: {e}", flush=True)
        cadena_nim = None

    try:
        cadena_gemini = construir_cadena("gemini")
    except Exception as e:
        print(f"Aviso cargando cadena Gemini: {e}", flush=True)
        cadena_gemini = None

    resultados = []

    for caso in CASOS_AMBIGUOS:
        print(f"\n[Caso {caso['id']}] - {caso['autor']} ({caso['canal']})", flush=True)
        print(f"   Texto: \"{caso['texto']}\"", flush=True)
        print(f"   Dilema: {caso['dilema']}", flush=True)

        # Entrada para el prompt productivo: canal, idioma, origen, texto (sin tipo_original)
        entrada_llm = {
            "origen": caso["origen"],
            "canal": caso["canal"],
            "idioma": caso["idioma"],
            "texto": caso["texto"],
        }

        eval_nim = None
        eval_gemini = None

        # 1. Evaluación directa NVIDIA NIM
        if cadena_nim:
            try:
                res_nim = cadena_nim.invoke(entrada_llm)
                eval_nim = res_nim.model_dump()
                print("   -> NVIDIA NIM - evaluacion directa:", flush=True)
                print(f"      * Sentimiento   : {res_nim.sentimiento}", flush=True)
                print(f"      * Tema Principal: {res_nim.tema_principal}", flush=True)
                print(f"      * Subtema       : {res_nim.subtema}", flush=True)
                print(f"      * Tipo Detectado: {res_nim.tipo_detectado}", flush=True)
            except Exception as err:
                print(f"   [!] NVIDIA NIM - error de evaluacion directa ({err.__class__.__name__})", flush=True)
                eval_nim = {"error": str(err.__class__.__name__)}

        # 2. Evaluación directa Gemini (ejecutada por separado, no como fallback)
        if cadena_gemini:
            try:
                res_gem = cadena_gemini.invoke(entrada_llm)
                eval_gemini = res_gem.model_dump()
                print("   -> Gemini - evaluacion directa:", flush=True)
                print(f"      * Sentimiento   : {res_gem.sentimiento}", flush=True)
                print(f"      * Tema Principal: {res_gem.tema_principal}", flush=True)
                print(f"      * Subtema       : {res_gem.subtema}", flush=True)
                print(f"      * Tipo Detectado: {res_gem.tipo_detectado}", flush=True)
            except Exception as err:
                print(f"   [!] Gemini - error de evaluacion directa ({err.__class__.__name__})", flush=True)
                eval_gemini = {"error": str(err.__class__.__name__)}

        resultados.append({
            "id": caso["id"],
            "autor": caso["autor"],
            "texto": caso["texto"],
            "dilema": caso["dilema"],
            "evaluacion_nim": eval_nim,
            "evaluacion_gemini": eval_gemini,
        })

    # Estructura de evidencia enriquecida solicitada por Arnold (Pág. 7 del PDF)
    evidencia = {
        "tipo_evaluacion": "exploratoria_casos_ambiguos",
        "rama_base": "feature/DS-Semana3-Nvidia",
        "commit_base": "b141c93",
        "sin_fallback": True,
        "tipo_original_enviado_al_llm": False,
        "proveedores": {
            "nvidia_nim": "nvidia/nemotron-3.5-lightning-30b-a3b",
            "gemini": "gemini-1.5-flash"
        },
        "resultados": resultados
    }

    ruta_salida = Path("docs/benchmark_calibracion_casos_ambiguos.json")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(evidencia, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80, flush=True)
    print(f"[OK] Benchmark exploratorio completado. Evidencia guardada en: {ruta_salida}", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    ejecutar_benchmark()
