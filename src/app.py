import streamlit as st
from asistente import responder

st.set_page_config(page_title="Asistente de documentos", page_icon="📄")
st.title("📄 Asistente de documentos")
st.caption("Pregunta sobre tus PDF. Responde solo con lo que está en ellos y cita la fuente.")

pregunta = st.text_input("Tu pregunta")
if st.button("Preguntar") and pregunta.strip():
    with st.spinner("Buscando y generando respuesta..."):
        respuesta, fragmentos = responder(pregunta)
    st.markdown(respuesta)
    with st.expander("Fragmentos recuperados"):
        for f in fragmentos:
            st.markdown(f"**{f['archivo']} — pág. {f['pagina']}** (distancia {f['distancia']:.3f})")
            st.write(f["texto"][:400] + "...")