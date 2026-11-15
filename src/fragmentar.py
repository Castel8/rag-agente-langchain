from extraer import extraer_paginas

TAM = 900
SOLAPE = 120


def fragmentar(paginas, tam=TAM, solape=SOLAPE):
    fragmentos = []
    for p in paginas:
        texto = p["texto"]
        inicio = 0
        while inicio < len(texto):
            fin = min(inicio + tam, len(texto))
            if fin < len(texto):
                corte = texto.rfind(" ", inicio, fin)
                if corte > inicio + tam // 2:
                    fin = corte
            trozo = texto[inicio:fin].strip()
            if trozo:
                fragmentos.append({
                    "id": len(fragmentos),
                    "archivo": p["archivo"],
                    "pagina": p["pagina"],
                    "texto": trozo,
                })
            if fin >= len(texto):
                break
            inicio = fin - solape
    return fragmentos


if __name__ == "__main__":
    fragmentos = fragmentar(extraer_paginas())
    print(f"Total de fragmentos: {len(fragmentos)}")
    largo_medio = sum(len(f["texto"]) for f in fragmentos) // len(fragmentos)
    print(f"Largo promedio: {largo_medio} caracteres\n")
    for f in fragmentos[:2]:
        print(f"[{f['id']}] {f['archivo']} pág. {f['pagina']}")
        print(f["texto"], "\n")