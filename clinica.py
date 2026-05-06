import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (TONALIDADES Y CONTRASTES RECUPERADOS) ---
st.markdown("""
    <style>
    /* Fondo Verde Menta Suave */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar Texto Negro Real en toda la aplicación */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    
    /* Contenedor del Logo Centrado */
    .logo-container { display: flex; justify-content: center; margin: 20px 0; }

    /* Tarjetas Médicas (Celdas de información) */
    .medical-card {
        background-color: #ffffff; 
        padding: 22px; 
        border-radius: 15px; 
        border: 2px solid #b2f5ea;
        border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); 
        margin-bottom: 20px;
    }
    
    /* Caja de Emergencia (Tonalidad Roja Suave) */
    .emergency-box {
        background-color: #fff5f5;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed #feb2b2;
        margin-top: 10px;
    }

    /* Tarjetas de Evolución (Tonalidad Azul Suave) */
    .evolution-card {
        background-color: #ffffff; 
        padding: 18px; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        border-left: 10px solid #63b3ed; 
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Sidebar (Tonalidad Morada Suave) */
    [data-testid="stSidebar"] { 
        background-color: #f3e8ff !important; 
        border-right: 3px solid #d8b4fe; 
    }
    
    .stSidebar button { 
        width: 100%; 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 2px solid #d8b4fe !important; 
        font-weight: bold !important; 
        margin-bottom: 10px; 
    }

    /* Inputs Blancos con Borde Definido */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }

    /* Botón de Guardar (Tonalidad Turquesa) */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; 
        color: #000000 !important; 
        border-radius: 12px; 
        font-weight: 900 !important; 
        border: 2px solid #285e61; 
        height: 3.8em; 
        width: 100%;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y CARGA DE DATOS ---
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
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="130"></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# Logo principal
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

# --- SECCIONES ---
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
        e_nom = st.text_input("Nombre del Contacto de Emergencia")
        e_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR NUEVO PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(), "entry.1801154005": edad,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ Paciente {nombre} registrado exitosamente.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial Clínico</h1>", unsafe_allow_html=True)
    doc_bus = st.text_input("Ingrese Documento del Paciente").strip()
    
    if doc_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == doc_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="margin:0; color:#2c5282;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p style="margin:5px 0;"><b>Doc:</b> {doc_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <p style="margin:5px 0;"><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>Celular:</b> {p.get('CELULAR', 'N/A')}</p>
                <p style="margin:5px 0;"><b>Alergias:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
                <div class="emergency-box">
                    <p style="margin:0; color:#c53030;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0;">{p.get('NOMBRE CONTACTO EMERGENCIA', 'No registrado')} — Tel: {p.get('TELEFONO CONTACTO EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("h_form_final", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        motivo = st.text_input("Motivo de Consulta")
                        talla = st.text_input("Talla (cm)")
                        pa = st.text_input("Presión Arterial")
                    with c2:
                        val = st.text_input("Valoración")
                        peso = st.text_input("Peso (kg)")
                    
                    ant = st.text_area("Antecedentes")
                    med = st.text_area("Medicamentos")
                    lab = st.text_area("Laboratorios")
                    epi = st.text_area("Epicrisis (Resumen)")

                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        payload_h = {
                            "entry.2019369477": doc_bus, "entry.611862537": motivo,
                            "entry.1275746503": val, "entry.949747647": talla,
                            "entry.2091389798": peso, "entry.889985940": ant,
                            "entry.2016051626": med, "entry.882053172": pa,
                            "entry.1088523869": lab, "entry.616774918": epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución guardada.")
                        st.cache_data.clear()
                        st.rerun()

            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == doc_bus]
                for i in range(len(h_p)-1, -1, -1):
                    f = h_p.iloc[i]
                    st.markdown(f"""
                    <div class="evolution-card">
                        <p style="border-bottom: 1px solid #edf2f7; padding-bottom: 5px;">📅 <b>Fecha: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                        <p><b>🔍 Motivo:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                        <p><b>📋 Epicrisis:</b> {f.get('EPICRISIS', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>Base de Datos</h1>", unsafe_allow_html=True)
    if df_p is not None:
        st.write("### Listado de Pacientes")
        st.dataframe(df_p)
    if df_h is not None:
        st.write("### Historial de Evoluciones")
        st.dataframe(df_h)
