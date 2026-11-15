from pathlib import Path
import agente

print("1. Tipo inválido:")
print("  ", agente.consultar_fallas.invoke({"tipo": "Z"}))

print("2. Base de datos inexistente:")
original = agente.RUTA_DB
agente.RUTA_DB = Path("no_existe.db")
print("  ", agente.consultar_fallas.invoke({"tipo": "L"}))
agente.RUTA_DB = original

print("3. Máximo de pasos muy bajo:")
agente.MAX_PASOS = 2
print("  ", agente.preguntar("¿Qué tipo de máquina tiene la mayor tasa de falla?"))
agente.MAX_PASOS = 12

print("4. Pregunta sobre datos que ninguna herramienta ofrece:")
print("  ", agente.preguntar("¿Cuántas fallas por desgaste de herramienta (TWF) hay?"))