import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (ESTÉTICA PROTEGIDA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] { 
        background-color: #f3e8ff !important; 
        border-right: 3px solid #d8b4fe; 
    }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.5em; width: 100%; text-transform: uppercase;
    }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y LINKS ---
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
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
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. SECCIÓN DE CONSULTA ---
st.markdown("<h1 style='text-align: center;'>🩺 Sistema de Evolución Médica</h1>", unsafe_allow_html=True)
busq = st.text_input("Ingrese Documento del Paciente").strip()

if busq and df_p is not None:
    pac = df_p[df_p["DOCUMENTO"] == busq]
    if not pac.empty:
        p = pac.iloc[0]
        h_p = df_h[df_h["DOCUMENTO"] == busq] if df_h is not None else pd.DataFrame()
        
        # Tarjeta Visual del Paciente
        st.markdown(f"""
        <div class="medical-card">
            <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h2>
            <p style='margin:5px 0;'><b>DOCUMENTO:</b> {busq} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
            <div class="emergency-box">
                <p style="margin:0; color:#c53030;"><b>🚨 CONTACTO DE EMERGENCIA:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'N/R')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'N/R')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📝 REGISTRAR NUEVA EVOLUCIÓN"):
            with st.form("h_form", clear_on_submit=True):
                motivo = st.text_input("Motivo de la Consulta")
                valoracion = st.text_input("Valoración (Ejem: Medicina General)")
                
                c1, c2, c3 = st.columns(3)
                talla = c1.text_input("Talla (cm)")
                peso = c2.text_input("Peso (kg)")
                pa = c3.text_input("Presión Arterial (TA)")
                
                ant = st.text_area("Antecedentes Médicos")
                meds = st.text_area("Medicamentos")
                labs = st.text_area("Laboratorios")
                epi = st.text_area("Epicrisis")
                
                if st.form_submit_button("💾 GUARDAR EVOLUCIÓN"):
                    # Mapeo corregido según tu link de Google Forms
                    payload = {
                        "entry.2019369477": busq,       # Doc
                        "entry.611862537": motivo,      # Motivo
                        "entry.1275746503": valoracion, # Valoración
                        "entry.949747647": talla,       # Talla
                        "entry.2091389798": peso,       # Peso
                        "entry.889985940": ant,         # Antecedentes
                        "entry.2016051626": meds,       # Medicamentos
                        "entry.882053172": pa,          # TA
                        "entry.1088523869": labs,       # Laboratorios
                        "entry.616774918": epi          # Epicrisis
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload)
                    st.success("✅ Datos guardados en la base de datos.")
                    st.cache_data.clear()
                    st.rerun()

        # Visualización del Historial
        st.markdown("### 🕒 Historial de Evoluciones")
        for i in range(len(h_p)-1, -1, -1):
            f = h_p.iloc[i]
            st.markdown(f"""
            <div class="evolution-card">
                <p style="color:#2b6cb0; border-bottom:1px solid #eee; padding-bottom:5px;">📅 <b>FECHA: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                <p><b>🔍 MOTIVO:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                <p><b>📋 VALORACIÓN:</b> {f.get('VALORACIÓN', 'N/A')}</p>
                <p><b>📏 TALLA:</b> {f.get('TALLA', 'N/A')} | <b>⚖️ PESO:</b> {f.get('PESO', 'N/A')} | <b>💓 TA:</b> {f.get('PRESIÓN ARTERIAL', 'N/A')}</p>
                <p><b>📚 ANTECEDENTES:</b> {f.get('ANTECEDENTES MÉDICOS', 'N/A')}</p>
                <p><b>💊 MEDICAMENTOS:</b> {f.get('MEDICAMENTOS', 'N/A')}</p>
                <p><b>🧪 LABORATORIOS:</b> {f.get('LABORATORIOS', 'N/A')}</p>
                <p><b>📝 EPICRISIS:</b> {f.get('EPICRISIS', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Paciente no encontrado.")
