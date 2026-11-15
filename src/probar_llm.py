import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELO = "gemini-3.8-flash"

for intento in range(1, 6):
    try:
        r = cliente.models.generate_content(
            model=MODELO,
            contents="Responde solo: conexión exitosa",
        )
        print(r.text)
        break
    except errors.ServerError:
        espera = 5 * intento
        print(f"Intento {intento}: servidor ocupado (503). Reintentando en {espera} s...")
        time.sleep(espera)
else:
    print("El servidor sigue ocupado. Prueba más tarde o con otro modelo.")