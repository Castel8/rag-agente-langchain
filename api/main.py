import logging
import sys
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))   # para importar el código del RAG

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")

UMBRAL_DECISION = 0.5   # igual que el dashboard y .predict() de la Actividad 1
modelo = joblib.load(RAIZ / "models" / "modelo_gb.joblib")

app = FastAPI(
    title="API de mantenimiento predictivo y asistente de documentos",
    description=(
        "Microservicio que expone (1) un modelo Gradient Boosting que estima la probabilidad "
        "de falla de una máquina a partir de lecturas de sensores y (2) un asistente RAG que "
        "responde preguntas sobre documentos PDF, citando las fuentes."
    ),
    version="1.0.0",
)


# ---------- Esquemas (validación con Pydantic) ----------
class Lectura(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{
            "air_temp_k": 298.1, "process_temp_k": 308.6, "rpm": 1551,
            "torque_nm": 42.8, "tool_wear_min": 0, "type": "M",
        }]},
    )
    air_temp_k: float = Field(..., ge=250, le=350, description="Temperatura del aire, en kelvin")
    process_temp_k: float = Field(..., ge=250, le=400, description="Temperatura del proceso, en kelvin")
    rpm: float = Field(..., gt=0, le=5000, description="Velocidad de rotación, en rpm")
    torque_nm: float = Field(..., ge=0, le=200, description="Torque, en newton-metro")
    tool_wear_min: float = Field(..., ge=0, le=1000, description="Desgaste de la herramienta, en minutos")
    type: Literal["L", "M", "H"] = Field(..., description="Calidad del producto: L, M o H")


class RespuestaPredict(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"probabilidad_falla": 0.0412, "prediccion": 0}]})
    probabilidad_falla: float = Field(..., ge=0, le=1, description="Probabilidad de falla entre 0 y 1")
    prediccion: Literal[0, 1] = Field(..., description="1 si la probabilidad supera el umbral de 0.5; 0 si no")


class Pregunta(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"pregunta": "¿Qué microcontrolador usa el Air-Sat?"}]},
    )
    pregunta: str = Field(..., min_length=3, max_length=500, description="Pregunta sobre los documentos")


class Fuente(BaseModel):
    archivo: str
    pagina: int


class RespuestaAsk(BaseModel):
    respuesta: str
    fuentes: list[Fuente]
    encontrado: bool

class ErrorDetalle(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"detalle": "type: Input should be 'L', 'M' or 'H'"}]},
    )
    detalle: str


# ---------- Errores con el campo "detalle" ----------
@app.exception_handler(RequestValidationError)
async def error_validacion(request, exc):
    mensajes = []
    for e in exc.errors():
        campo = ".".join(str(x) for x in e["loc"] if x != "body")
        mensajes.append(f"{campo}: {e['msg']}")
    return JSONResponse(status_code=422, content={"detalle": "; ".join(mensajes)})


@app.exception_handler(StarletteHTTPException)
async def error_http(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detalle": exc.detail})


@app.exception_handler(Exception)
async def error_interno(request, exc):
    log.exception("Error inesperado")
    return JSONResponse(status_code=500, content={"detalle": "Error interno del servidor."})


# ---------- Endpoints ----------
@app.get("/health", tags=["Estado"], summary="Verifica que el servicio está activo")
def health():
    return {"estado": "ok"}


@app.post(
    
    "/predict", response_model=RespuestaPredict, tags=["Modelo"],
    summary="Probabilidad de falla de una máquina",
    description="Recibe las lecturas de sensores y calcula internamente la potencia y la "
                "diferencia de temperatura con las mismas fórmulas del entrenamiento.",
)
def predict(lectura: Lectura):
    fila = pd.DataFrame([{
        "air_temp_k": lectura.air_temp_k,
        "process_temp_k": lectura.process_temp_k,
        "rpm": lectura.rpm,
        "torque_nm": lectura.torque_nm,
        "tool_wear_min": lectura.tool_wear_min,
        "power_w": lectura.torque_nm * lectura.rpm * 2 * np.pi / 60,
        "temp_diff_k": lectura.process_temp_k - lectura.air_temp_k,
        "type": lectura.type,
    }])
    prob = float(modelo.predict_proba(fila)[0, 1])
    log.info("predict type=%s rpm=%s torque=%s -> prob=%.4f", lectura.type, lectura.rpm, lectura.torque_nm, prob)
    return {"probabilidad_falla": round(prob, 4), "prediccion": int(prob >= UMBRAL_DECISION)}


def _rag():
    import asistente   # la primera vez carga Chroma y el modelo de embeddings (tarda unos segundos)
    return asistente


@app.post(
    "/ask", response_model=RespuestaAsk, tags=["RAG"],
    summary="Pregunta sobre los documentos",
    description="Busca los fragmentos más cercanos a la pregunta y redacta la respuesta solo con "
                "esa información. Si no hay información relevante, devuelve encontrado = false.",
    responses=
    {
        422: {"model": ErrorDetalle, "description": "Pregunta inválida (menos de 3 o más de 500 caracteres)"},
        503: {"model": ErrorDetalle, "description": "El modelo de lenguaje no está disponible"},
        504: {"model": ErrorDetalle, "description": "Se superó el tiempo máximo"},
    },
)
def ask(p: Pregunta):
    a = _rag()
    fragmentos = a.recuperar(p.pregunta, k=a.K)
    if not fragmentos or fragmentos[0]["distancia"] > a.UMBRAL:
        return {"respuesta": a.NO_ENCONTRADO, "fuentes": [], "encontrado": False}

    prompt = a.PROMPT.format(
        no_encontrado=a.NO_ENCONTRADO,
        contexto=a.armar_contexto(fragmentos),
        pregunta=p.pregunta,
    )
    try:
        texto = (a.cliente.models.generate_content(model=a.MODELO, contents=prompt).text or "").strip()
    except Exception as e:
        log.error("Falló el modelo de lenguaje: %s", type(e).__name__)
        if "timeout" in type(e).__name__.lower():
            raise HTTPException(status_code=504, detail="La solicitud tardó demasiado.")
        raise HTTPException(status_code=503, detail="El modelo de lenguaje no está disponible. Intenta más tarde.")

    if texto == a.NO_ENCONTRADO:
        return {"respuesta": texto, "fuentes": [], "encontrado": False}

    # Solo las fuentes que la respuesta cita; si no cita ninguna, los 3 fragmentos más cercanos
    citados = [f for f in fragmentos if f"{f['archivo']}, pág. {f['pagina']}" in texto] or fragmentos[:3]
    vistos, fuentes = set(), []
    for f in citados:
        clave = (f["archivo"], f["pagina"])
        if clave not in vistos:
            vistos.add(clave)
            fuentes.append({"archivo": f["archivo"], "pagina": f["pagina"]})
    return {"respuesta": texto, "fuentes": fuentes, "encontrado": True}