import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL (ESTILO CONSULTORÍA CON CENTRADO) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Enlace del logo estable
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Lato:wght@300;400&display=swap" rel="stylesheet">
    <style>
    .stApp {{
        background-color: #f4fafa !important;
        font-family: 'Lato', sans-serif;
    }}
    
    /* Centrado de Títulos y Contenedores de Imagen */
    .main-title {{
        text-align: center;
        font-family: 'Poppins', sans-serif;
        color: #1e293b !important;
        margin-top: -20px;
    }}
    
    .centered-image {{
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }}

    /* Barra Lateral */
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }}
    
    /* Centrado de imagen en Sidebar */
    [data-testid="stSidebarNav"] + div {{
        display: flex;
        justify-content: center;
        padding: 10px;
    }}

    /* Tarjeta de Paciente */
    .medical-card {{
        background-color: #ffffff;
        padding: 30px;
        border-radius: 4px;
        border-top: 6px solid #22d3ee;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        color: #334155;
    }}
    
    .emergency-box {{
        background-color: #fff1f2;
        padding: 15px;
        border-radius: 4px;
        border-left: 4px solid #f43f5e;
        color: #9f1239;
        font-weight: 600;
        margin-top: 15px;
    }}

    /* Botones Premium */
    div.stButton > button {{
        background-color: #0891b2 !important;
        color: white !important;
        border-radius: 2px !important;
        width: 100%;
        font-weight: 600 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        def limpiar(txt): return str(txt).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except Exception as e:
        st.error(f"Error de sistema: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    # Centrado manual en sidebar usando columnas
    col_side1, col_side2, col_side3 = st.columns([1, 4, 1])
    with col_side2:
        st.image(LOGO_URL, use_container_width=True)
    
    st.markdown("<h3 style='text-align: center; color: #1e293b;'>MENÚ</h3>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.menu = "Inicio"
    if st.button("📝 REGISTRO"): st.session_state.menu = "Registrar"
    if st.button("🔍 HISTORIAL"): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    # Centrado usando columnas para la imagen principal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, use_container_width=True)
    
    st.markdown("<h1 class='main-title'>TARJETA VIDA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'><i>Intelligence Healthcare Management | Guadalupe, Huila</i></p>", unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(LOGO_URL, width=150)
    st.markdown("<h1 class='main-title'>REGISTRO CLÍNICO</h1>", unsafe_allow_html=True)
    
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Identificación", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_especiales = st.text_area("Notas / Alergias / Preexistencias")
        if st.form_submit_button("COMPLETAR REGISTRO"):
            st.success("✅ Datos sincronizados.")

elif st.session_state.menu == "Consulta":
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(LOGO_URL, width=150)
    st.markdown("<h1 class='main-title'>CONSULTA MÉDICA</h1>", unsafe_allow_html=True)
    
    busqueda_raw = st.text_input("Identificación del paciente").strip()
    id_buscado = busqueda_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0; text-align: center;'>👤 {p.get('NOMBRE')}</h2>
                <hr style='border: 0.5px solid #e2e8f0; margin: 15px 0;'>
                <p style='text-align: center;'><b>{p.get('TIPO DE DOCUMENTO')}:</b> {p.get('DOCUMENTO')} | <b>EDAD:</b> {p.get('EDAD')} años</p>
                <div class="emergency-box" style='text-align: center;'>🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.error("Paciente no encontrado.")
