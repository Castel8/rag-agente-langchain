import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from recuperar import recuperar, armar_contexto

from langgraph.errors import GraphRecursionError

MAX_PASOS = 12   # tope de pasos del agente; evita bucles infinitos

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

RUTA_DB = RAIZ / "data" / "ai4i.db"
UMBRAL = 0.65   # igual que en asistente.py
K = 8
MODELO = "gemini-3.5-flash-lite"


# ---------- Herramienta 1: documentos (RAG) ----------
@tool
def buscar_documentos(pregunta: str) -> str:
    """Busca información en los documentos cargados (proyecto CANSAT AIR-SAT,
    seguidor de línea y proyecto de ecuaciones diferenciales). Úsala para preguntas
    cuyo contenido esté en esos documentos: descripciones, componentes, conceptos y
    explicaciones. Devuelve fragmentos con su archivo y página. No sirve para datos
    numéricos de fallas de máquinas."""
    try:
        fragmentos = recuperar(pregunta, k=K)
        if not fragmentos or fragmentos[0]["distancia"] > UMBRAL:
            return "No se encontró información relevante en los documentos."
        return armar_contexto(fragmentos)
    except Exception as e:
        return f"Error al buscar en los documentos: {e}"


# ---------- Herramienta 2: base de datos (SQL) ----------
@tool
def consultar_fallas(tipo: str) -> str:
    """Devuelve el número de lecturas, de fallas y la tasa de falla de las máquinas
    según su tipo de calidad (L, M o H). Úsala para preguntas numéricas sobre la base
    de datos de lecturas de sensores de máquinas. Para comparar tipos, llámala una vez
    por cada tipo."""
    tipo = tipo.strip().upper()
    if tipo not in ("L", "M", "H"):
        return "Tipo no válido. Los tipos disponibles son L, M y H."
    if not RUTA_DB.exists():
        return "Base de datos no encontrada. No puedo consultar las fallas."
    try:
        with sqlite3.connect(RUTA_DB) as con:
            filas, fallas = con.execute(
                "SELECT COUNT(*), SUM(falla) FROM lecturas WHERE tipo = ?", (tipo,)
            ).fetchone()
        if not filas:
            return f"Tipo {tipo}: no hay lecturas."
        return (
            f"Tipo {tipo}: {filas} lecturas, {fallas} fallas, "
            f"tasa de falla {100 * fallas / filas:.2f} %."
        )
    except Exception as e:
        return f"Error al consultar la base de datos: {e}"



# ---------- Agente ----------
PROMPT_SISTEMA = """Eres un asistente con dos herramientas:
- buscar_documentos: para preguntas sobre el contenido de los documentos (Air-Sat, seguidor de línea, ecuaciones diferenciales).
- consultar_fallas: para preguntas numéricas sobre fallas de máquinas en la base de datos (tipos L, M, H).

Reglas:
1. Elige la herramienta según la pregunta. Si la pregunta necesita las dos, usa las dos.
2. Responde solo con lo que devuelvan las herramientas. No inventes datos ni uses conocimiento externo.
3. Si ninguna herramienta puede responder la pregunta, o devuelven que no hay información, responde exactamente: "No encontré esa información en mis fuentes."
4. Responde en español, breve y preciso. Al usar documentos, cita la fuente (archivo, pág. N)."""

llm = ChatGoogleGenerativeAI(model=MODELO)
agente = create_agent(
    model=llm,
    tools=[buscar_documentos, consultar_fallas],
    system_prompt=PROMPT_SISTEMA,
)


def texto(msg):
    """Extrae solo el texto de un mensaje (Gemini puede devolver bloques)."""
    c = msg.content
    if isinstance(c, str):
        return c
    return "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")


def ejecutar(pregunta):
    """Devuelve (respuesta, pasos). Cada paso: herramienta, argumentos y resultado."""
    res = None
    for intento in range(1, 4):
        try:
            res = agente.invoke(
                {"messages": [{"role": "user", "content": pregunta}]},
                config={"recursion_limit": MAX_PASOS},
            )
            break
        except GraphRecursionError:
            return "No pude completar la consulta dentro del máximo de pasos permitido.", []
        except Exception as e:
            print(f"  Intento {intento} falló: {type(e).__name__}")
            time.sleep(5 * intento)
    if res is None:
        return "El modelo no responde en este momento. Intenta de nuevo en unos minutos.", []

    pasos = []
    for m in res["messages"]:
        if getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                pasos.append({"herramienta": tc["name"], "argumentos": tc["args"], "resultado": None})
        if m.type == "tool":
            for p in pasos:
                if p["resultado"] is None and p["herramienta"] == m.name:
                    p["resultado"] = str(m.content)
                    break
    return texto(res["messages"][-1]), pasos


def preguntar(pregunta):
    """Versión para consola: imprime la traza y devuelve la respuesta."""
    respuesta, pasos = ejecutar(pregunta)
    for p in pasos:
        print(f"  -> Llama a {p['herramienta']} con {p['argumentos']}")
    for p in pasos:
        print(f"  <- {p['herramienta']} devolvió: {(p['resultado'] or '')[:150].replace(chr(10), ' ')}...")
    return respuesta