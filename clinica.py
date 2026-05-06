import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (ALTO CONTRASTE Y COLORES PREFERIDOS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Texto Negro Intenso para máxima legibilidad */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    
    .logo-container { display: flex; justify-content: center; margin: 20px 0; }

    .medical-card {
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #b2f5ea;
        border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); 
        margin-bottom: 20px;
    }
    
    /* Recuadro específico para Emergencias dentro de la tarjeta */
    .emergency-box {
        background-color: #fff5f5;
        padding: 12px;
        border-radius: 10px;
        border: 2px dashed #f56565;
        margin-top: 10px;
    }

    .evolution-card {
        background-color: #ffffff; 
        padding: 18px; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        border-left: 8px solid #63b3ed; 
        margin-bottom: 15px;
    }

    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 2px solid #d8b4fe !important; 
        font-weight: bold !important; 
        margin-bottom: 10px; 
    }

    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; 
        color: #000000 !important; 
        border-radius: 12px; 
        font-weight: 900 !important; 
        border: 2px solid #285e61; 
        height: 3.5em; 
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
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
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="140"></div>', unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

# --- SECCIÓN 1: REGISTRAR (CON EMERGENCIA) ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Pacientes</h1>", unsafe_allow_html=True)
    with st.form("form_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería", "Pasaporte"])
            cedula = st.text_input("Número de Documento")
            edad = st.text_input("Edad")
        with c2:
            celular = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
            condiciones = st.text_area("Condiciones Especiales / Alergias")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre del Contacto")
        e_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(), "entry.1801154005": edad,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente y contacto de emergencia guardados.")
                st.cache_data.clear()

# --- SECCIÓN 2: CONSULTA (CON EMERGENCIA VISIBLE) ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busqueda = st.text_input("Documento del Paciente").strip()
    
    if busqueda and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == busqueda]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>Doc:</b> {busqueda} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>Celular:</b> {p.get('CELULAR', 'N/A')}</p>
                <p><b>Alergias:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
                <div class="emergency-box">
                    <p style="color: #c53030 !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0;">{p.get('NOMBRE CONTACTO EMERGENCIA', 'No registrado')} - {p.get('TELEFONO CONTACTO EMERGENCIA', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ Nueva Evolución Médica"):
                with st.form("h_form", clear_on_submit=True):
                    # ... (Campos de historial igual que antes)
                    motivo = st.text_input("Motivo")
                    epi = st.text_area("Epicrisis")
                    if st.form_submit_button("REGISTRAR"):
                        requests.post(URL_FORM_HISTORIAL, data={"entry.2019369477": busqueda, "entry.611862537": motivo, "entry.616774918": epi})
                        st.rerun()

# --- SECCIÓN 3: BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>Base de Datos</h1>", unsafe_allow_html=True)
    if df_p is not None:
        st.subheader("Pacientes")
        st.dataframe(df_p)
