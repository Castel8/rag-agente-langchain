import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from recuperar import recuperar, armar_contexto

load_dotenv()
cliente = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)
MODELO = "gemini-3.5-flash-lite"
UMBRAL = 0.65
K = 8
NO_ENCONTRADO = "No encontré esa información en los documentos."

PROMPT = """Eres un asistente que responde preguntas sobre un conjunto de documentos.
Reglas:
1. Responde solo con la información del CONTEXTO. No uses conocimiento externo.
2. Si el contexto no contiene la respuesta, responde exactamente: "{no_encontrado}"
3. Responde en español, de forma breve y precisa.
4. Al final, cita las fuentes usadas con el formato (archivo, pág. N).
5. No agregues sensores, gases, valores ni nombres que no aparezcan literalmente en el CONTEXTO.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}
"""


def llamar_llm(prompt):
    for intento in range(1, 4):
        t0 = time.time()
        try:
            texto = cliente.models.generate_content(model=MODELO, contents=prompt).text
            print(f"Generación OK en {time.time() - t0:.1f} s (intento {intento})")
            return texto
        except Exception as e:
            print(f"Intento {intento} falló tras {time.time() - t0:.1f} s: {type(e).__name__}")
            time.sleep(5 * intento)
    return "El modelo está ocupado o no responde. Intenta de nuevo en unos minutos."


def responder(pregunta):
    t0 = time.time()
    fragmentos = recuperar(pregunta, k=K)
    print(f"Recuperación: {time.time() - t0:.1f} s")
    if fragmentos[0]["distancia"] > UMBRAL:
        return NO_ENCONTRADO, fragmentos
    prompt = PROMPT.format(
        no_encontrado=NO_ENCONTRADO,
        contexto=armar_contexto(fragmentos),
        pregunta=pregunta,
    )
    return llamar_llm(prompt), fragmentos


if __name__ == "__main__":
    preguntas = [
        "¿Qué microcontrolador usa el Air-Sat y con qué sensores mide la contaminación?",
        "¿Cuál es la capital de Francia?",
    ]
    for q in preguntas:
        respuesta, fr = responder(q)
        print(f"\nPREGUNTA: {q}")
        print(f"RESPUESTA: {respuesta}")
        print("Fragmentos usados:")
        for f in fr:
            print(f"  - {f['archivo']} pág. {f['pagina']} (distancia {f['distancia']:.3f})")