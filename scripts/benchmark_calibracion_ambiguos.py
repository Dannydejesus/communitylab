"""Benchmark de calibración semántica entre NVIDIA NIM, Cohere y Gemini."""

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

from langchain_core.messages import HumanMessage
from src.agentes.modelo_ia import obtener_modelo_analisis_estructurado
from src.agentes.modelos import AnalisisMensaje

CASOS_AMBIGUOS = [
    {
        "id": "int-006",
        "autor": "Ricardo Mena",
        "canal": "#feedback-programa",
        "texto": "Sería genial tener más talleres prácticos sobre despliegue de modelos en la nube antes del hackathon.",
        "dilema": "¿Sentimiento es neutral o positivo? ¿Tema es cloud_infraestructura o programa_hackathon?"
    },
    {
        "id": "int-011",
        "autor": "Gabriela Núñez",
        "canal": "#historias-egresados",
        "texto": "El networking que generé en este programa me abrió puertas para colaborar en proyectos open source.",
        "dilema": "¿Tema es comunidad o empleabilidad? ¿Sentimiento es positivo o muy_positivo?"
    },
    {
        "id": "int-016",
        "autor": "Isabel Quiroga",
        "canal": "#formulario-testimonios",
        "texto": "Nunca pensé que podría aprender SQL y Python al mismo tiempo, pero la metodología del curso lo hizo posible.",
        "dilema": "¿Sentimiento es positivo o muy_positivo? ¿Tema es aprendizaje o programacion?"
    },
    {
        "id": "int-020",
        "autor": "Lucía Paredes",
        "canal": "categoria-programacion-basica",
        "texto": "Sugiero agregar más ejercicios prácticos antes de pasar al módulo de estructuras de datos, se siente un salto grande.",
        "dilema": "¿Sentimiento es negativo o neutral? ¿Sugerencia clasifica como feedback o comentario?"
    }
]

# Configuración de codificación para evitar bloqueos de I/O en consola Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

def ejecutar_benchmark():
    print("=" * 80, flush=True)
    print("[*] BENCHMARK DE CALIBRACION SEMANTICA MULTI-LLM (DATA SCIENCE)", flush=True)
    print("Evaluacion en casos limite ambiguos: int-006, int-011, int-016, int-020", flush=True)
    print("=" * 80, flush=True)

    try:
        modelo_nim = obtener_modelo_analisis_estructurado(AnalisisMensaje, proveedor="nvidia_nim")
    except Exception as e:
        print(f"Aviso cargando NIM: {e}", flush=True)
        modelo_nim = None

    try:
        modelo_gemini = obtener_modelo_analisis_estructurado(AnalisisMensaje, proveedor="gemini")
    except Exception as e:
        print(f"Aviso cargando Gemini: {e}", flush=True)
        modelo_gemini = None

    resultados = []

    for caso in CASOS_AMBIGUOS:
        print(f"\n[Caso {caso['id']}] - {caso['autor']} ({caso['canal']})", flush=True)
        print(f"   Texto: \"{caso['texto']}\"", flush=True)
        print(f"   Dilema: {caso['dilema']}", flush=True)

        eval_nim = None
        eval_gemini = None

        if modelo_nim:
            try:
                res_nim = modelo_nim.invoke([HumanMessage(content=caso["texto"])])
                eval_nim = res_nim.model_dump()
                print("   -> Clasificacion Nemotron (NVIDIA NIM):", flush=True)
                print(f"      * Sentimiento   : {res_nim.sentimiento}", flush=True)
                print(f"      * Tema Principal: {res_nim.tema_principal}", flush=True)
                print(f"      * Subtema       : {res_nim.subtema}", flush=True)
            except Exception as err:
                print(f"   [!] NIM no disponible temporalmente ({err.__class__.__name__})", flush=True)
                eval_nim = {"error": str(err.__class__.__name__)}

        if modelo_gemini:
            try:
                res_gem = modelo_gemini.invoke([HumanMessage(content=caso["texto"])])
                eval_gemini = res_gem.model_dump()
                print("   -> Clasificacion Gemini (Fallback Activo):", flush=True)
                print(f"      * Sentimiento   : {res_gem.sentimiento}", flush=True)
                print(f"      * Tema Principal: {res_gem.tema_principal}", flush=True)
                print(f"      * Subtema       : {res_gem.subtema}", flush=True)
            except Exception as err:
                print(f"   [!] Gemini error ({err.__class__.__name__})", flush=True)
                eval_gemini = {"error": str(err.__class__.__name__)}

        resultados.append({
            "id": caso["id"],
            "autor": caso["autor"],
            "texto": caso["texto"],
            "dilema": caso["dilema"],
            "evaluacion_nim": eval_nim,
            "evaluacion_gemini": eval_gemini,
        })

    # Guardar reporte en docs/
    ruta_salida = Path("docs/benchmark_calibracion_casos_ambiguos.json")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80, flush=True)
    print(f"[OK] Benchmark completado. Reporte generado en: {ruta_salida}", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    ejecutar_benchmark()
