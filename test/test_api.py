from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

VALIDO = {"air_temp_k": 298.1, "process_temp_k": 308.6, "rpm": 1551,
          "torque_nm": 42.8, "tool_wear_min": 0, "type": "M"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok"}


def test_predict_valido():
    r = client.post("/predict", json=VALIDO)
    assert r.status_code == 200
    datos = r.json()
    assert 0 <= datos["probabilidad_falla"] <= 1
    assert datos["prediccion"] in (0, 1)


def test_predict_invalido():
    r = client.post("/predict", json={**VALIDO, "type": "X", "rpm": -5})
    assert r.status_code == 422
    detalle = r.json()["detalle"]
    assert "type" in detalle and "rpm" in detalle

def test_ask_pregunta_invalida():
    r = client.post("/ask", json={"pregunta": "a"})
    assert r.status_code == 422
    assert "pregunta" in r.json()["detalle"]