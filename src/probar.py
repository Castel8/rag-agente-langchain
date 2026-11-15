import chromadb
from indexar import obtener_coleccion, RUTA_DB

cliente = chromadb.PersistentClient(path=str(RUTA_DB))
col = obtener_coleccion(cliente)

pregunta = "¿Qué microcontrolador usa el Air-Sat?"
res = col.query(query_texts=[pregunta], n_results=8)

for i, (doc, meta, dist) in enumerate(
    zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1
):
    tiene = "STM32" in doc
    print(f"{i}. {meta['archivo']} pág. {meta['pagina']} | distancia {dist:.3f} | contiene STM32: {tiene}")