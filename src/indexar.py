from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from extraer import extraer_paginas
from fragmentar import fragmentar

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "chroma_db"
MODELO = "paraphrase-multilingual-MiniLM-L12-v2"


def obtener_coleccion(cliente):
    emb = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODELO)
    return cliente.get_or_create_collection(
        name="documentos",
        embedding_function=emb,
        metadata={"hnsw:space": "cosine"},
    )


def indexar():
    cliente = chromadb.PersistentClient(path=str(RUTA_DB))
    try:
        cliente.delete_collection("documentos")
    except Exception:
        pass
    coleccion = obtener_coleccion(cliente)
    fr = fragmentar(extraer_paginas())
    coleccion.add(
        ids=[f"frag-{f['id']}" for f in fr],
        documents=[f["texto"] for f in fr],
        metadatas=[{"archivo": f["archivo"], "pagina": f["pagina"]} for f in fr],
    )
    print(f"Fragmentos indexados: {coleccion.count()}")
    return coleccion


if __name__ == "__main__":
    col = indexar()
    pregunta = "¿Qué microcontrolador usa el Air-Sat?"
    res = col.query(query_texts=[pregunta], n_results=3)
    print(f"\nPrueba: {pregunta}")
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        print(f"\n- {meta['archivo']} pág. {meta['pagina']} (distancia {dist:.3f})")
        print(doc[:200])