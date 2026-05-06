import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS REFINADO (ESTÉTICA Y ALINEACIÓN) ---
st.markdown("""
    <style>
    /* Fondo general y fuentes */
    .stApp { 
        background-color: #f0fff4 !important; 
    }
    
    /* Forzar texto negro y limpio en toda la app */
    html, body, [class*="st-"] {
        color: #000000 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    h1, h2, h3 { 
        color: #1a365d !important; 
        text-align: center;
        font-weight: 800 !important;
    }

    /* Contenedor del Logo Centrado */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px 0;
        width: 100%;
    }

    /* Estilo de los inputs (Blancos con borde suave) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
        border-radius: 8px !important;
    }

    /* Botones principales */
    div.stButton > button:first-child {
        background-color: #4fd1c5 !important;
        color: #ffffff !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
        height: 3em;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #38b2ac !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Tarjetas de información */
    .medical-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #4fd1c5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .evolution-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        border-left: 8px solid #63b3ed;
        margin-bottom: 15px;
    }

    /* Sidebar Estético */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 5. CABECERA UNIFICADA (LOGO CENTRADO SIEMPRE) ---
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

# --- 6. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.markdown("### Menú de Gestión")
    if st.button("📝 Registro de Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"

# --- 7. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería", "Pasaporte"])
            cedula = st.text_input("Número de Documento")
        with col2:
            celular = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
            
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre,
                    "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(),
                    "entry.1043165037": celular,
                    "entry.1172011247": eps,
                    "entry.162368130": rh
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado correctamente.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1>Consulta de Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Documento a consultar").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>Identificación:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>Celular:</b> {p.get('CELULAR', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Formulario de evolución simplificado para estética
            with st.expander("➕ Agregar Nueva Evolución Médica"):
                with st.form("h_form_new"):
                    motivo = st.text_input("Motivo de Consulta")
                    epi = st.text_area("Epicrisis / Valoración")
                    if st.form_submit_button("Guardar en Historial"):
                        requests.post(URL_FORM_HISTORIAL, data={
                            "entry.2019369477": id_bus,
                            "entry.611862537": motivo,
                            "entry.616774918": epi
                        })
                        st.success("Registro guardado.")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.error("Paciente no encontrado.")
