# Requerimientos del microservicio

## Funcionales
- **RF1.** `GET /health` responde 200 con `{"estado": "ok"}`.
- **RF2.** `POST /predict` recibe las lecturas de un sensor y devuelve `probabilidad_falla` (entre 0 y 1) y `prediccion` (0 o 1).
- **RF3.** `POST /ask` recibe una pregunta y devuelve la respuesta y la lista de fuentes (archivo y página).
- **RF4.** Si la pregunta no está en los documentos, `/ask` responde "No encontré esa información en los documentos."
- **RF5.** El servicio valida las entradas: `tipo` solo puede ser L, M o H y las variables numéricas deben estar en rangos plausibles. Si no, responde 422 con un mensaje claro.

## No funcionales
- **RNF1.** Rendimiento: `/predict` responde en menos de 1 segundo y `/ask` en menos de 60 segundos.
- **RNF2.** Seguridad: la clave de API vive en `.env` y nunca en el código ni en el repositorio, que esto se cumpla a cabalidad.
- **RNF3.** Robustez y tiempos de espera: si el modelo de lenguaje externo no está disponible, `/ask` devuelve 503; si la solicitud supera el tiempo máximo (30 s), devuelve 504. En ambos casos la respuesta es un JSON con un campo `detalle` que explica el motivo, nunca un error 500 sin explicación.

## Fuera de alcance
- Aplicación cliente (por ejemplo, avisar al usuario cuando no tiene conexión a internet).
