from pathlib import Path
from pypdf import PdfReader
import re

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DOCS = RAIZ / "docs"


def extraer_paginas(carpeta=CARPETA_DOCS):
    paginas = []

    for pdf in sorted(carpeta.glob("*.pdf")):
        lector = PdfReader(pdf)
        for i, pagina in enumerate(lector.pages, start=1):
            texto = pagina.extract_text() or ""
            texto = re.sub(r"\s+", " ", texto).strip()
            if texto:
                paginas.append({
                    "archivo": pdf.name,
                    "pagina": i,
                    "texto": texto
                })

    return paginas


if __name__ == "__main__":
    paginas = extraer_paginas()
    if not paginas:
        print("No se extrajo texto. Revisa que los PDF estén en docs/.")
    else:
        archivos = sorted({p["archivo"] for p in paginas})
        print(f"PDF procesados: {len(archivos)}")
        for a in archivos:
            n = sum(1 for p in paginas if p["archivo"] == a)
            print(f"- {a}: {n} páginas con texto")
        print("\nMuestra:", paginas[0]["archivo"],
              "pág.", paginas[0]["pagina"])
        print(paginas[0]["texto"][:300])
