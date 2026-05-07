import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .medical-card { background-color: #ffffff; padding: 22px; border-radius: 15px; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .evolution-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 10px solid #63b3ed; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    div.stButton > button:first-child:not(.stSidebar button) { background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; height: 3.8em; width: 100%; }
    input, textarea, [data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        if 'DOCUMENTO' in h.columns:
            h['DOCUMENTO'] = h['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"
with st.sidebar:
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- SECCIÓN CONSULTA E HISTORIAL ---
if st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente").strip()
    
    if busq and df_p is not None:
        h_p = df_h[df_h["DOCUMENTO"] == busq] if df_h is not None else pd.DataFrame()

        # 1. FORMULARIO DE EVOLUCIÓN (ORDEN DEL LINK)
        with st.expander("✍️ AGREGAR NUEVA EVOLUCIÓN"):
            with st.form("h_form", clear_on_submit=True):
                # Siguiendo el orden de los entries del link proporcionado
                f_motivo = st.text_input("1. Motivo de la Consulta") # entry.611862537
                f_val = st.text_area("2. Valoración")             # entry.1275746503
                col1, col2, col3 = st.columns(3)
                f_talla = col1.text_input("3. Talla (cm)")         # entry.949747647
                f_peso = col2.text_input("4. Peso (kg)")           # entry.2091389798
                f_pa = col3.text_input("5. Presión Arterial")      # entry.882053172
                
                f_ant = st.text_area("6. Antecedentes Médicos")    # entry.889985940
                f_meds = st.text_area("7. Medicamentos")           # entry.2016051626
                f_lab = st.text_area("8. Laboratorios")            # entry.1088523869
                f_epi = st.text_area("9. Epicrisis")               # entry.616774918
                
                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    payload_h = {
                        "entry.2019369477": busq,     # Documento (Pre-llenado en tu link)
                        "entry.611862537": f_motivo,   # Motivo
                        "entry.1275746503": f_val,     # Valoración
                        "entry.949747647": f_talla,    # Talla
                        "entry.2091389798": f_peso,    # Peso
                        "entry.889985940": f_ant,      # Antecedentes
                        "entry.2016051626": f_meds,    # Medicamentos
                        "entry.882053172": f_pa,       # Presión Arterial
                        "entry.1088523869": f_lab,     # Laboratorios
                        "entry.616774918": f_epi       # Epicrisis
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.success("✅ Datos enviados al historial.")
                    st.cache_data.clear()
                    st.rerun()

        # 2. TARJETAS DE EVOLUCIÓN (ORDEN VISUAL AJUSTADO)
        st.markdown("### 🕒 Historial de Evoluciones")
        for i in range(len(h_p)-1, -1, -1):
            f = h_p.iloc[i]
            st.markdown(f"""
            <div class="evolution-card">
                <p style="color:#2b6cb0; margin-bottom:5px;">📅 <b>REGISTRO: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
                <p><b>🔍 MOTIVO:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                <p><b>📋 VALORACIÓN:</b> {f.get('VALORACIÓN', 'N/A')}</p>
                <p><b>📏 SIGNOS VITALES:</b> 
                    Talla: {f.get('TALLA', 'N/A')}cm | 
                    Peso: {f.get('PESO', 'N/A')}kg | 
                    TA: {f.get('PRESIÓN ARTERIAL', 'N/A')}
                </p>
                <p><b>🏥 ANTECEDENTES:</b> {f.get('ANTECEDENTES MÉDICOS', 'N/A')}</p>
                <p><b>💊 MEDICAMENTOS:</b> {f.get('MEDICAMENTOS', 'N/A')}</p>
                <p><b>🧪 LABORATORIOS:</b> {f.get('LABORATORIOS', 'N/A')}</p>
                <p><b>📝 EPICRISIS:</b> {f.get('EPICRISIS', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    if df_h is not None: st.dataframe(df_h)
