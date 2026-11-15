import streamlit as st
import agente

st.set_page_config(page_title="Asistente de documentos y datos", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg, #0B1F3A 0%, #0E2A4F 100%);}
[data-testid="stSidebar"] {background: #0A1A33; border-right: 1px solid #1E3A5F;}
.block-container {padding-top: 2rem; max-width: 1000px;}
#MainMenu, footer {visibility: hidden;}
.encabezado {background: linear-gradient(90deg, #1D4ED8, #0EA5E9); padding: 1.2rem 1.5rem;
             border-radius: 12px; margin-bottom: 1rem;}
.encabezado h1 {color: #FFFFFF; margin: 0; font-size: 1.7rem;}
.encabezado p {color: #DBEAFE; margin: 0.3rem 0 0 0;}
.tarjeta {background: #12294A; border: 1px solid #1E3A5F; border-left: 4px solid #38BDF8;
          padding: 0.7rem 1rem; border-radius: 8px;}
.tarjeta span {font-size: 0.78rem; color: #94A3B8;}
.tarjeta div {font-weight: 600; color: #E6EEF8;}
</style>
""", unsafe_allow_html=True)

NOMBRES = {"buscar_documentos": "📄 Documentos (RAG)", "consultar_fallas": "🗄️ Base de datos (SQL)"}
AVATAR = {"user": "🧑‍💻", "assistant": "🤖"}
EJEMPLOS = [
    "¿Qué microcontrolador usa el Air-Sat?",
    "¿Qué es la transformada de Laplace?",
    "¿Cuál es la tasa de falla de las máquinas de tipo H?",
    "¿Qué tipo de máquina tiene la mayor tasa de falla?",
    "¿Qué microcontrolador usa el Air-Sat y cuántas lecturas hay de tipo M?",
]

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# ---------- Barra lateral ----------
st.sidebar.title("🤖 Asistente con IA")
st.sidebar.caption("LangChain · Gemini · RAG · SQL")
st.sidebar.markdown("**📌 Cómo funciona**")
st.sidebar.write("El agente analiza cada pregunta y decide si consulta los documentos, "
                 "la base de datos de fallas, ambas o ninguna.")
st.sidebar.markdown("**💡 Preguntas de ejemplo**")
for q in EJEMPLOS:
    if st.sidebar.button(q, use_container_width=True):
        st.session_state.pendiente = q
if st.sidebar.button("🧹 Limpiar conversación", use_container_width=True):
    st.session_state.mensajes = []

# ---------- Encabezado ----------
st.markdown("""
<div class="encabezado">
  <h1>🤖 Asistente inteligente de documentos y datos</h1>
  <p>Consulta documentos técnicos y la base de datos de fallas de máquinas desde un solo lugar.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.markdown('<div class="tarjeta"><span>📄 Fuentes documentales</span><div>PDF indexados (RAG)</div></div>', unsafe_allow_html=True)
c2.markdown('<div class="tarjeta"><span>🗄️ Base de datos</span><div>10 000 lecturas (SQL)</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="tarjeta"><span>🧠 Modelo</span><div>{agente.MODELO}</div></div>', unsafe_allow_html=True)
st.write("")


def mostrar_pasos(pasos):
    if not pasos:
        st.caption("💬 Respondió sin consultar herramientas.")
        return
    with st.expander(f"🔧 Herramientas utilizadas ({len(pasos)})"):
        for i, p in enumerate(pasos, 1):
            st.markdown(f"**{i}. {NOMBRES.get(p['herramienta'], p['herramienta'])}**")
            st.code(str(p["argumentos"]), language="python")
            st.caption((p["resultado"] or "")[:300])


# ---------- Historial ----------
for m in st.session_state.mensajes:
    with st.chat_message(m["rol"], avatar=AVATAR[m["rol"]]):
        st.markdown(m["contenido"])
        if m["rol"] == "assistant":
            mostrar_pasos(m.get("pasos"))

# ---------- Nueva pregunta ----------
pregunta = st.chat_input("Escribe tu pregunta sobre los documentos o las fallas de máquinas")
if "pendiente" in st.session_state:
    pregunta = st.session_state.pop("pendiente")

if pregunta:
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})
    with st.chat_message("user", avatar=AVATAR["user"]):
        st.markdown(pregunta)
    with st.chat_message("assistant", avatar=AVATAR["assistant"]):
        with st.spinner("Consultando las fuentes..."):
            respuesta, pasos = agente.ejecutar(pregunta)
        st.markdown(respuesta)
        mostrar_pasos(pasos)
    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta, "pasos": pasos})