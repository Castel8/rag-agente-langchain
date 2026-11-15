import time
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from asistente import responder

PREGUNTAS = [
    ("¿Qué microcontrolador usa el Air-Sat?", "STM32F411CEU6"),
    ("¿Qué sensor mide el CO2 en el Air-Sat?", "MH-Z19"),
    ("¿Dónde y en qué competencia será lanzado el Air-Sat?", "ENMICE 2025, Guadalajara (México)"),
    ("¿Qué microcontrolador usa el robot seguidor de línea?", "ESP32"),
    ("¿Qué es la transformada de Laplace?", "COMPLETAR con el PDF de Laplace"),
    ("¿Para qué se usa la transformada de Laplace en el proyecto?", "COMPLETAR con el PDF de Laplace"),
    ("¿Qué fenómeno modela el proyecto de ecuaciones diferenciales?", "COMPLETAR con el PDF del terremoto"),
    ("¿En qué se diferencia el microcontrolador del Air-Sat del del seguidor de línea?", "STM32F411CEU6 vs ESP32 (dos documentos)"),
    ("¿Cuál es la capital de Francia?", "No encontrado"),
    ("¿Para qué se usa el sensor MQ-135 en el Air-Sat?", "No encontrado"),
]

ENCABEZADOS = [
    "Pregunta",
    "Respuesta esperada",
    "Respuesta del asistente",
    "Fuentes recuperadas",
    "Correcta (si/no)",
    "Fuente correcta (si/no)",
    "Inventó algo (si/no)",
]

wb = Workbook()
ws = wb.active
ws.title = "Evaluación"
ws.append(ENCABEZADOS)

for pregunta, esperada in PREGUNTAS:
    respuesta, fr = responder(pregunta)
    fuentes = "\n".join(sorted({f"{f['archivo']} p.{f['pagina']}" for f in fr[:4]}))
    ws.append([pregunta, esperada, respuesta, fuentes, "", "", ""])
    print(f"Listo: {pregunta}")
    time.sleep(2)

for letra, ancho in {"A": 40, "B": 32, "C": 60, "D": 45, "E": 14, "F": 16, "G": 16}.items():
    ws.column_dimensions[letra].width = ancho

relleno = PatternFill("solid", fgColor="1F3864")
for celda in ws[1]:
    celda.font = Font(bold=True, color="FFFFFF")
    celda.fill = relleno
    celda.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")

for fila in ws.iter_rows(min_row=2):
    for celda in fila:
        celda.alignment = Alignment(wrap_text=True, vertical="top")

validacion = DataValidation(type="list", formula1='"si,no"', allow_blank=True)
ws.add_data_validation(validacion)
validacion.add(f"E2:G{ws.max_row}")

ws.freeze_panes = "A2"
wb.save("evaluacion.xlsx")
print("\nResultados guardados en evaluacion.xlsx")