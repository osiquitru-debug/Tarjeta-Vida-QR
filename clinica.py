import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA Y DISEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; font-weight: 700 !important; 
    }
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
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y LINKS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIONES TÉCNICAS ---
def limpiar_id(val):
    if pd.isna(val): return ""
    v = str(val).strip()
    return v.split('.')[0]

def normalizar(t):
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_col(fila, keys):
    for col in fila.index:
        if any(k in normalizar(col) for k in keys):
            return str(fila[col])
    return "N/R"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        # Estandarizar documentos en ambas tablas
        for df in [p, h]:
            doc_col = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if doc_col:
                df[doc_col] = df[doc_col].apply(limpiar_id)
        return p, h
    except: return None, None

def generar_pdf_hc(paciente, historial, doc_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORTE CLINICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"PACIENTE: {get_col(paciente, ['NOM'])}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"DOC: {doc_id} | RH: {get_col(paciente, ['RH'])} | EPS: {get_col(paciente, ['EPS'])}", ln=True)
    pdf.ln(5)
    for _, f in historial.iterrows():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"FECHA: {get_col(f, ['MARCA', 'FECHA'])}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        info = (f"Motivo: {get_col(f, ['MOTIVO'])}\n"
                f"Valoracion: {get_col(f, ['VALORAC'])}\n"
                f"Talla: {get_col(f, ['TALLA'])} | Peso: {get_col(f, ['PESO'])} | TA: {get_col(f, ['PRESION', 'TA'])}\n"
                f"Medicamentos: {get_col(f, ['MEDICAM'])}\n"
                f"Epicrisis: {get_col(f, ['EPICRIS'])}")
        pdf.multi_cell(0, 5, info.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(4)
    return pdf.output(dest='S').encode('latin-1', 'replace')

df_p, df_h = cargar_datos()

# --- 5. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="120"></div>', unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- SECCIONES ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Pacientes</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["Cédula", "T.I.", "C.E.", "Pasaporte"])
            doc = st.text_input("Documento")
        with c2:
            cel = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre de contacto")
        e_tel = st.text_input("Teléfono de contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nom and doc:
                payload = {
                    "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": doc.strip(), 
                    "entry.1043165037": cel, "entry.1172011247": eps, "entry.162368130": rh,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente guardado correctamente.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = limpiar_id(st.text_input("Documento del Paciente"))
    
    if busq and df_p is not None:
        doc_col_p = next((c for c in df_p.columns if "DOC" in normalizar(c)), "DOCUMENTO")
        pac = df_p[df_p[doc_col_p] == busq]
        
        if not pac.empty:
            p = pac.iloc[0]
            doc_col_h = next((c for c in df_h.columns if "DOC" in normalizar(c)), "DOCUMENTO")
            h_p = df_h[df_h[doc_col_h] == busq] if df_h is not None else pd.DataFrame()
            
            st.download_button("📥 DESCARGAR REPORTE PDF", data=generar_pdf_hc(p, h_p, busq), file_name=f"HC_{busq}.pdf")

            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {get_col(p, ['NOM'])}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {get_col(p, ['RH'])} | <b>EPS:</b> {get_col(p, ['EPS'])}</p>
                <div class="emergency-box">
                    <p style="margin:0; color:#c53030;"><b>🚨 EMERGENCIA:</b> {get_col(p, ['CONTACTO', 'NOM'])} - {get_col(p, ['TEL'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ AGREGAR EVOLUCIÓN"):
                with st.form("h_form", clear_on_submit=True):
                    motivo = st.text_input("Motivo de la Consulta")
                    val = st.text_input("Valoración")
                    c1, c2, c3 = st.columns(3)
                    talla, peso, pa = c1.text_input("Talla"), c2.text_input("Peso"), c3.text_input("TA")
                    ant, meds, lab, epi = st.text_area("Antecedentes"), st.text_area("Medicamentos"), st.text_area("Laboratorios"), st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        payload_h = {
                            "entry.2019369477": busq, "entry.611862537": motivo, "entry.1275746503": val,
                            "entry.949747647": talla, "entry.2091389798": peso, "entry.889985940": ant,
                            "entry.2016051626": meds, "entry.882053172": pa, "entry.1088523869": lab, "entry.616774918": epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución registrada.")
                        st.cache_data.clear()
                        st.rerun()

            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {get_col(f, ['MARCA', 'FECHA'])}</b></p>
                    <p><b>🔍 MOTIVO:</b> {get_col(f, ['MOTIVO'])}</p>
                    <p><b>📋 VALORACIÓN:</b> {get_col(f, ['VALORAC'])}</p>
                    <p><b>💊 MEDICAMENTOS:</b> {get_col(f, ['MEDICAM'])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    if df_p is not None: st.write("Pacientes:", df_p)
    if df_h is not None: st.write("Historial:", df_h)
