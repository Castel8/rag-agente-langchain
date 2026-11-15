import chromadb
from indexar import obtener_coleccion, RUTA_DB

_cliente = chromadb.PersistentClient(path=str(RUTA_DB))
_col = obtener_coleccion(_cliente)


def recuperar(pregunta, k=5):
    res = _col.query(query_texts=[pregunta], n_results=k)
    return [
        {"archivo": m["archivo"], "pagina": m["pagina"], "texto": d, "distancia": dist}
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


def armar_contexto(fragmentos):
    return "\n\n".join(
        f"[{f['archivo']}, pág. {f['pagina']}]\n{f['texto']}" for f in fragmentos
    )


if __name__ == "__main__":
    preguntas = [
        "¿Qué microcontrolador usa el Air-Sat?",
        "¿Qué es la transformada de Laplace?",
        "¿Cuál es la capital de Francia?",
    ]
    for q in preguntas:
        fr = recuperar(q)
        print(f"\n{q}")
        print(f"  Mejor: {fr[0]['archivo']} pág. {fr[0]['pagina']}")
        print(f"  Distancias: {[round(f['distancia'], 3) for f in fr]}")