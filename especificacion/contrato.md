# Contrato de la API (API first)

## GET /health
Respuesta 200:
```json
{"estado": "ok"}
```

## POST /predict
Entrada (JSON):
```json
{"air_temp_k": 298.1, "process_temp_k": 308.6, "rpm": 1551,
 "torque_nm": 42.8, "tool_wear_min": 0, "type": "M"}
```

| Campo | Tipo | Regla |
|---|---|---|
| air_temp_k | número | entre 250 y 350 |
| process_temp_k | número | entre 250 y 400 |
| rpm | número | mayor que 0 y hasta 3000 |
| torque_nm | número | entre 0 y 200 |
| tool_wear_min | número | entre 0 y 1000 |
| type | texto | solo "L", "M" o "H" |

La API calcula internamente `power_w` y `temp_diff_k` con las mismas fórmulas del entrenamiento.

Respuesta 200:
```json
{"probabilidad_falla": 0.0412, "prediccion": 0}
```
- `probabilidad_falla`: entre 0 y 1.
- `prediccion`: 1 si la probabilidad supera el umbral de decisión, 0 si no.

## POST /ask
Entrada:
```json
{"pregunta": "¿Qué microcontrolador usa el Air-Sat?"}
```
La pregunta debe tener entre 3 y 500 caracteres.

Respuesta 200:
```json
{"respuesta": "El Air-Sat usa el STM32F411CEU6...",
 "fuentes": [{"archivo": "CANSAT AIR-SAT ENMICE-2025 ENTREGABLE.pdf", "pagina": 2}],
 "encontrado": true}
```
Si la pregunta no está en los documentos: `encontrado` es `false`, `respuesta` es "No encontré esa información en los documentos." y `fuentes` va con los fragmentos recuperados o vacío.

## Errores (todos con el campo `detalle`)
| Código | Cuándo | Ejemplo |
|---|---|---|
| 422 | Entrada inválida | `{"detalle": "type debe ser L, M o H"}` |
| 503 | El modelo de lenguaje no está disponible | `{"detalle": "El modelo de lenguaje no está disponible. Intenta más tarde."}` |
| 504 | Se superó el tiempo máximo (60 s) | `{"detalle": "La solicitud tardó demasiado."}` |