import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
cliente = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

excluir = ("image", "tts", "live", "embedding", "audio", "robotics", "computer", "veo", "imagen")
candidatos = []
for m in cliente.models.list():
    nombre = m.name.replace("models/", "")
    if ("flash" in nombre or "lite" in nombre) and not any(x in nombre for x in excluir):
        candidatos.append(nombre)

print(f"Modelos a probar: {len(candidatos)}\n")
for nombre in candidatos[:12]:
    t0 = time.time()
    try:
        r = cliente.models.generate_content(model=nombre, contents="Responde solo: ok")
        print(f"OK     {nombre}  ({time.time() - t0:.1f} s)")
    except Exception as e:
        print(f"FALLA  {nombre}  ({time.time() - t0:.1f} s) {type(e).__name__}: {str(e)[:90]}")