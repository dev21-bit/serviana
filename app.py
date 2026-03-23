import streamlit as st
import pandas as pd
import uuid
import os
from openai import OpenAI

st.set_page_config(page_title="ServiAna AI", layout="wide")

api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key) if api_key else None

st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.tag {
    background-color: #2a2f3a;
    padding: 5px 10px;
    border-radius: 10px;
    margin-right: 5px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

if "servicios" not in st.session_state:
    st.session_state.servicios = [
        {"id": str(uuid.uuid4()), "nombre": "Juan Pérez", "servicio": "Electricista", "precio": 300, "ciudad": "Zacatecas", "rating": 4.8},
        {"id": str(uuid.uuid4()), "nombre": "Ana López", "servicio": "Diseñadora gráfica", "precio": 500, "ciudad": "Zacatecas", "rating": 4.9},
        {"id": str(uuid.uuid4()), "nombre": "Carlos Ruiz", "servicio": "Programador", "precio": 800, "ciudad": "Guadalajara", "rating": 4.7},
    ]

st.sidebar.title("ServiAna AI")
menu = st.sidebar.radio("Menú", ["Inicio", "Buscar", "Publicar", "IA", "Top"])

if api_key:
    st.sidebar.success("IA activa")
else:
    st.sidebar.warning("Modo demo")

if menu == "Inicio":
    st.title("ServiAna AI")
    df = pd.DataFrame(st.session_state.servicios)
    col1, col2, col3 = st.columns(3)
    col1.metric("Servicios", len(df))
    col2.metric("Usuarios", "1245")
    col3.metric("Rating", round(df["rating"].mean(),2))
    st.dataframe(df, use_container_width=True)

elif menu == "Buscar":
    st.title("Buscar servicios")
    query = st.text_input("Buscar")
    ciudad = st.selectbox("Ciudad", ["Todas","Zacatecas","Guadalajara"])

    resultados = st.session_state.servicios

    if query:
        resultados = [s for s in resultados if query.lower() in s["servicio"].lower()]

    if ciudad != "Todas":
        resultados = [s for s in resultados if s["ciudad"] == ciudad]

    resultados = sorted(resultados, key=lambda x: x["rating"], reverse=True)

    for s in resultados:
        st.markdown(f"""
        <div class="card">
            <h3>{s['nombre']}</h3>
            <p>{s['servicio']}</p>
            <p>{s['ciudad']}</p>
            <p>Rating: {s['rating']}</p>
            <h4>${s['precio']}</h4>
        </div>
        """, unsafe_allow_html=True)

elif menu == "Publicar":
    st.title("Publicar servicio")
    nombre = st.text_input("Nombre")
    servicio = st.text_input("Servicio")
    precio = st.number_input("Precio", min_value=50)
    ciudad = st.text_input("Ciudad")

    if st.button("Publicar"):
        st.session_state.servicios.append({
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "servicio": servicio,
            "precio": precio,
            "ciudad": ciudad,
            "rating": 5.0
        })
        st.success("Publicado")

elif menu == "IA":
    st.title("Recomendador inteligente")
    user_input = st.text_area("Describe lo que necesitas")

    if st.button("Analizar"):
        if user_input:
            prompt = f"""
            Analiza esta necesidad:
            {user_input}

            Devuelve:
            tipo de profesional,
            presupuesto estimado en México,
            palabras clave
            """

            if client:
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role":"user","content":prompt}]
                )
                resultado = response.choices[0].message.content
            else:
                resultado = "programador, 5000-15000, app, desarrollo"

            st.write(resultado)

            palabras = resultado.lower()

            scores = []
            for s in st.session_state.servicios:
                score = 0
                if s["servicio"].lower() in palabras:
                    score += 2
                if s["ciudad"].lower() in palabras:
                    score += 1
                score += s["rating"]
                scores.append((score, s))

            recomendados = [s for _, s in sorted(scores, reverse=True)]

            for s in recomendados[:5]:
                st.write(f"{s['nombre']} | {s['servicio']} | ${s['precio']} | {s['rating']}")

elif menu == "Top":
    st.title("Top profesionales")
    top = sorted(st.session_state.servicios, key=lambda x: x["rating"], reverse=True)
    for s in top:
        st.write(f"{s['nombre']} | {s['servicio']} | {s['rating']}")