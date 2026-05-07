import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 8px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px; color: #1a202c;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #e2e8f0; border-left: 4px solid #63b3ed;
        margin-bottom: 10px; color: #2d3748;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        # Cargamos los datos forzando a que sean texto
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Normalizamos nombres de columnas para evitar errores de tipeo
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        # Creamos una columna de búsqueda limpia (sin decimales ni espacios)
        p['ID_BUSQUEDA'] = p.iloc[:, 1].str.split('.').str[0].str.strip()
        h['ID_BUSQUEDA'] = h.iloc[:, 1].str.split('.').str[0].str.strip()
        
        return p, h
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registro", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("SISTEMA MÉDICO")
    st.subheader("Guadalupe, Huila")
    st.write("Bienvenido al gestor de historias clínicas.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("form_reg", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        doc = st.text_input("Número de Documento")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        if st.form_submit_button("GUARDAR"):
            payload = {"entry.346175428": nombre, "entry.1302424820": doc, "entry.162368130": rh}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_input = st.text_input("Documento del Paciente").strip()
    # Limpiamos el input para que coincida con la base de datos
    id_clave = id_input.split('.')[0]

    if id_clave and df_p is not None:
        paciente = df_p[df_p['ID_BUSQUEDA'] == id_clave]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.iloc[2]}</h2>
                <p><b>ID:</b> {p.iloc[1]} | <b>RH:</b> {p.iloc[6]} | <b>EPS:</b> {p.iloc[5]}</p>
            </div>""", unsafe_allow_html=True)
            
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("form_evo", clear_on_submit=True):
                    val = st.text_area("Valoración"); mot = st.text_area("Motivo")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        h_pay = {"entry.2019369477": id_clave, "entry.1088523869": val, "entry.611862537": mot}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL")
            h_p = df_h[df_h['ID_BUSQUEDA'] == id_clave].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <b>📅 {f.iloc[0]}</b><br>
                        <b>Motivo:</b> {f.iloc[3]}<br>
                        <b>Valoración:</b> {f.iloc[2]}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Sin registros previos.")
        else:
            st.error(f"No se encontró el paciente con ID: {id_clave}")
