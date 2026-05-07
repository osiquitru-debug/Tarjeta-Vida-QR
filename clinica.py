import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA INALTERABLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
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
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }
    .stDownloadButton > button {
        background-color: #3182ce !important; color: white !important; 
        border-radius: 12px; font-weight: bold; width: 100%; border: none;
    }
    input, textarea, [data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO Y CARGA ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        # Normalización estricta de columnas para evitar errores de coincidencia
        p.columns = [c.strip().upper() for c in p.columns]
        h.columns = [c.strip().upper() for c in h.columns]
        if 'DOCUMENTO' in p.columns: p['DOCUMENTO'] = p['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        if 'DOCUMENTO' in h.columns: h['DOCUMENTO'] = h['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. MENÚ LATERAL (ORDEN CORREGIDO) ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE SECCIONES ---
if st.session_state.menu == "Consulta":
    busq = st.text_input("Documento del Paciente").strip()
    if busq and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == busq]
        if not pac.empty:
            p = pac.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == busq] if df_h is not None else pd.DataFrame()
            
            # Tarjeta de Paciente Completa
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <p><b>Celular:</b> {p.get('CELULAR', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 EMERGENCIA:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'Oscar Quintero')}</p>
                    <p style="margin:0;"><b>Tel:</b> {p.get('TELEFONO CONTACTO EMERGENCIA', '3225879465')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Botón PDF
            if not h_p.empty:
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"Historial: {p.get('NOMBRE')}", ln=True)
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 Descargar PDF Historial", pdf_bytes, f"HC_{busq}.pdf")

            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    mot = st.text_input("Motivo"); val = st.text_input("Valoración")
                    c1, c2, c3 = st.columns(3)
                    tll = c1.text_input("Talla (cm)"); pes = c2.text_input("Peso (kg)"); ten = c3.text_input("TA")
                    ant = st.text_area("Antecedentes"); med = st.text_area("Medicamentos")
                    lab = st.text_area("Laboratorios"); epi = st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        pay = {"entry.2019369477": busq, "entry.611862537": mot, "entry.1275746503": val, "entry.949747647": tll, "entry.2091389798": pes, "entry.889985940": ant, "entry.2016051626": med, "entry.882053172": ten, "entry.1088523869": lab, "entry.616774918": epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            # Historial con mapeo verificado columna por columna
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                    <p>📋 <b>VALORACIÓN:</b> {f.get('VALORACIÓN', 'N/A')}</p>
                    <p>📏 <b>TALLA:</b> {f.get('TALLA', 'N/A')} | ⚖️ <b>PESO:</b> {f.get('PESO', 'N/A')} | 💓 <b>TA:</b> {f.get('PRESIÓN ARTERIAL', 'N/A')}</p>
                    <p>🧪 <b>LABORATORIOS:</b> {f.get('LABORATORIOS', 'N/A')}</p>
                    <p>📝 <b>EPICRISIS:</b> {f.get('EPICRISIS', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.menu == "Base":
    st.subheader("Base de Datos"); st.dataframe(df_p); st.dataframe(df_h)

elif st.session_state.menu == "Registrar":
    st.info("Use el formulario de registro para nuevos pacientes.")
