import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA Y DISEÑO (ESTRUCTURA VISUAL ORIGINAL) ---
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
URL_APP_REAL = "https://tarjeta-vida-qr-abrilycompania.streamlit.app/"
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIONES DE PROCESAMIENTO ---
def limpiar_id(val):
    if pd.isna(val): return ""
    return str(val).strip().split('.')[0]

def normalizar(t):
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_col_val(fila, keys):
    for col in fila.index:
        if any(k in normalizar(col) for k in keys):
            return str(fila[col])
    return "N/R"

@st.cache_data(ttl=1)
def cargar_todo():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if c_doc: df[c_doc] = df[c_doc].apply(limpiar_id)
        return p, h
    except: return None, None

def generar_pdf(paciente, historial, doc_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORTE CLINICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"PACIENTE: {get_col_val(paciente, ['NOM'])}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"DOC: {doc_id} | RH: {get_col_val(paciente, ['RH'])} | EPS: {get_col_val(paciente, ['EPS'])}", ln=True)
    pdf.ln(5)
    for _, f in historial.iterrows():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"FECHA: {get_col_val(f, ['MARCA', 'FECHA'])}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        txt = f"Motivo: {get_col_val(f, ['MOTIVO'])}\nValoracion: {get_col_val(f, ['VALORAC'])}\nEpicrisis: {get_col_val(f, ['EPICRIS'])}"
        pdf.multi_cell(0, 5, txt.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(4)
    return pdf.output(dest='S').encode('latin-1', 'replace')

df_p, df_h = cargar_todo()

# --- 5. NAVEGACIÓN Y PARÁMETROS URL (QR) ---
id_url = st.query_params.get("id", "")
if id_url and 'menu' not in st.session_state:
    st.session_state.menu = "Consulta"
elif 'menu' not in st.session_state:
    st.session_state.menu = "Registrar"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="140"></div>', unsafe_allow_html=True)

# --- 6. SECCIÓN: REGISTRAR ---
if st.session_state.menu == "Registrar":
    st.markdown("<h2 style='text-align: center;'>Registro de Pacientes</h2>", unsafe_allow_html=True)
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre Completo")
            td = st.selectbox("Tipo Doc", ["Cédula", "T.I.", "C.E.", "Pasaporte"])
            d = st.text_input("Número de Documento")
        with c2:
            r = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            e = st.text_input("EPS")
            cl = st.text_input("Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        en = st.text_input("Nombre contacto")
        et = st.text_input("Teléfono contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if n and d:
                requests.post(URL_FORM_PACIENTES, data={
                    "entry.346175428": n, "entry.1650757004": td, "entry.1302424820": d.strip(), 
                    "entry.1043165037": cl, "entry.1172011247": e, "entry.162368130": r,
                    "entry.1892763134": en, "entry.2011749615": et
                })
                st.success("✅ Paciente guardado exitosamente.")
                st.cache_data.clear()
            else: st.error("Nombre y Documento son obligatorios.")

# --- 7. SECCIÓN: CONSULTA (QR COMPATIBLE) ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h2 style='text-align: center;'>Consulta e Historial</h2>", unsafe_allow_html=True)
    
    # Si viene de un QR, el campo se llena solo
    busq = limpiar_id(st.text_input("Documento del Paciente", value=id_url))
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in normalizar(c)), "DOCUMENTO")
        p_row = df_p[df_p[c_doc_p] == busq]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in normalizar(c)), "DOCUMENTO")
            h_p = df_h[df_h[c_doc_h] == busq] if df_h is not None else pd.DataFrame()
            
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {get_col_val(p, ['NOM'])}</h3>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {get_col_val(p, ['RH'])} | <b>EPS:</b> {get_col_val(p, ['EPS'])}</p>
                <div class="emergency-box">
                    <p style="margin:0; color:#c53030;"><b>🚨 EMERGENCIA:</b> {get_col_val(p, ['CONTACTO'])} - {get_col_val(p, ['TEL'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c_a, c_b = st.columns(2)
            c_a.download_button("📥 DESCARGAR REPORTE PDF", data=generar_pdf(p, h_p, busq), file_name=f"HC_{busq}.pdf")
            
            # QR dinámico con tu URL oficial
            link_qr = f"{URL_APP_REAL}?id={busq}"
            c_b.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={link_qr}", caption="QR para este Paciente")

            with st.expander("✍️ AGREGAR EVOLUCIÓN MÉDICA"):
                with st.form("f_evo", clear_on_submit=True):
                    mot = st.text_input("Motivo de consulta")
                    val = st.text_input("Valoración")
                    t, ps, pa = st.columns(3)
                    talla = t.text_input("Talla")
                    peso = ps.text_input("Peso")
                    ten = pa.text_input("TA")
                    med = st.text_area("Medicamentos")
                    epi = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("REGISTRAR EN HISTORIAL"):
                        requests.post(URL_FORM_HISTORIAL, data={
                            "entry.2019369477": busq, "entry.611862537": mot, "entry.1275746503": val,
                            "entry.949747647": talla, "entry.2091389798": peso, "entry.882053172": ten,
                            "entry.2016051626": med, "entry.616774918": epi
                        })
                        st.success("Evolución guardada.")
                        st.cache_data.clear(); st.rerun()

            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {get_col_val(f, ['MARCA', 'FECHA'])}</b></p>
                    <p><b>🩺 MOTIVO:</b> {get_col_val(f, ['MOTIVO'])}</p>
                    <p><b>📝 EPICRISIS:</b> {get_col_val(f, ['EPICRIS'])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"El paciente con documento {busq} no está registrado.")

# --- 8. SECCIÓN: BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.write("### 📊 Listado de Pacientes")
    st.dataframe(df_p)
    st.write("### 📊 Historial Clínico Completo")
    st.dataframe(df_h)
