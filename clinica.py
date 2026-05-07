import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    input, textarea, select { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, label { text-align: center; color: #1a202c; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; text-align: left;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (MÉTODO POSICIONAL) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        # Leemos todo como texto puro
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        
        # Limpieza de la columna ID (Asumimos que es la columna índice 1)
        p['KEY'] = p.iloc[:, 1].astype(str).str.split('.').str[0].str.strip()
        h['KEY'] = h.iloc[:, 1].astype(str).str.split('.').str[0].str.strip()
        
        return p, h
    except:
        return None, None

df_p, df_h = cargar_tablas()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("MENÚ")
    if st.button("Inicio"): st.session_state.menu = "Inicio"
    if st.button("Registrar"): st.session_state.menu = "Registrar"
    if st.button("Consulta"): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("SISTEMA MÉDICO")
    st.write("Bienvenido al sistema de gestión.")

elif st.session_state.menu == "Registrar":
    st.title("REGISTRO")
    with st.form("reg"):
        n = st.text_input("Nombre"); d = st.text_input("Documento")
        if st.form_submit_button("Guardar"):
            payload = {"entry.346175428": n, "entry.1302424820": d} # Ajusta según tus IDs de Form
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Guardado"); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("CONSULTA")
    id_buscar = st.text_input("Documento").strip()
    
    if id_buscar and df_p is not None:
        # Buscamos en la columna KEY que creamos
        p_row = df_p[df_p['KEY'] == id_buscar]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            # USAMOS ILOC PARA EVITAR ERRORES DE NOMBRE DE COLUMNA
            st.markdown(f"""
            <div class="medical-card">
                <h2>PACIENTE: {p.iloc[2]}</h2>
                <p><b>Documento:</b> {p.iloc[1]} | <b>RH:</b> {p.iloc[6]} | <b>EPS:</b> {p.iloc[5]}</p>
            </div>""", unsafe_allow_html=True)
            
            # Formulario de Evolución
            with st.expander("Registrar Evolución"):
                with st.form("evo"):
                    v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo")
                    if st.form_submit_button("Guardar Evolución"):
                        # ... lógica de guardado de form historial ...
                        st.success("Enviado"); st.cache_data.clear()

            st.subheader("HISTORIAL")
            h_p = df_h[df_h['KEY'] == id_buscar].sort_index(ascending=False)
            
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    # Aquí mapeamos por posición exacta del historial (0=Fecha, 2=Val, 3=Motivo, etc)
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>Fecha: {f.iloc[0]}</small><br>
                        <b>Valoración:</b> {f.iloc[2]}<br>
                        <b>Motivo:</b> {f.iloc[3]}<br>
                        <b>Talla:</b> {f.iloc[4]} | <b>Peso:</b> {f.iloc[5]} | <b>Presión:</b> {f.iloc[6]}<br>
                        <b>Medicamentos:</b> {f.iloc[8]}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Sin historial.")
        else:
            st.error(f"No se encontró el ID: {id_buscar}")
