import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. EL "ADN" VISUAL (ESTÉTICA RECUPERADA) ---
st.markdown("""
    <style>
    /* Fondo Verde Menta */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Texto Negro Real (Máximo Contraste) */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    
    .logo-container { display: flex; justify-content: center; margin: 20px 0; }

    /* Celdas de Información (Pacientes) */
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    
    /* Celdas de Emergencia (Rojo) */
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }

    /* Celdas de Evolución (Azul) */
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Sidebar Morado Suave */
    [data-testid="stSidebar"] { 
        background-color: #f3e8ff !important; 
        border-right: 3px solid #d8b4fe; 
    }
    
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }

    /* Botón Principal Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }

    /* Inputs Blancos */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y CARGA ---
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
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

def generar_pdf_hc(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORTE CLÍNICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"PACIENTE: {paciente.get('NOMBRE', 'N/A')}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"DOC: {paciente.get('DOCUMENTO', 'N/A')} | RH: {paciente.get('RH', 'N/A')} | EPS: {paciente.get('EPS', 'N/A')}", ln=True)
    pdf.ln(5)
    for _, f in historial.iterrows():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL', 'S/F')}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        info = (f"Motivo: {f.get('MOTIVO DE LA CONSULTA', 'N/A')}\n"
                f"Medicina: {f.get('MEDICAMENTOS', 'N/A')}\n"
                f"Talla: {f.get('TALLA', 'N/A')} | Peso: {f.get('PESO', 'N/A')} | TA: {f.get('PRESIÓN ARTERIAL', 'N/A')}\n"
                f"Epicrisis: {f.get('EPICRISIS', 'N/A')}")
        pdf.multi_cell(0, 5, info)
        pdf.ln(4)
    return pdf.output(dest='S').encode('latin-1')

df_p, df_h = cargar_datos()

# --- 4. ESTRUCTURA Y NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="120"></div>', unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

# --- SECCIÓN: REGISTRAR ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Pacientes</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["Cédula", "T.I.", "C.E."])
            doc = st.text_input("Documento")
        with c2:
            cel = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload_p = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": doc.strip(), "entry.1043165037": cel, "entry.1172011247": eps, "entry.162368130": rh}
            requests.post(URL_FORM_PACIENTES, data=payload_p)
            st.success("✅ Registrado.")
            st.cache_data.clear()

# --- SECCIÓN: CONSULTA E HISTORIAL (CON EPICRISIS Y PDF) ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente").strip()
    
    if busq and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == busq]
        if not pac.empty:
            p = pac.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == busq] if df_h is not None else pd.DataFrame()
            
            # Botón PDF
            pdf_bytes = generar_pdf_hc(p, h_p)
            st.download_button("📥 DESCARGAR HISTORIA COMPLETA (PDF)", data=pdf_bytes, file_name=f"HC_{busq}.pdf")

            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="margin:0; color:#c53030;"><b>🚨 EMERGENCIA:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'N/R')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'N/R')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ AGREGAR EVOLUCIÓN (ORDEN DEL SHEET)"):
                with st.form("h_form", clear_on_submit=True):
                    # Orden exacto solicitado: Motivo, Meds, Val, Talla, Peso, Ant, PA, Lab, Epicrisis
                    motivo = st.text_input("Motivo de la Consulta")
                    meds = st.text_area("Medicamentos")
                    val = st.text_input("Valoración")
                    c1, c2, c3 = st.columns(3)
                    talla = c1.text_input("Talla (cm)")
                    peso = c2.text_input("Peso (kg)")
                    pa = c3.text_input("Presión Arterial")
                    ant = st.text_area("Antecedentes Médicos")
                    lab = st.text_area("Laboratorios")
                    epi = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        payload_h = {
                            "entry.2019369477": busq, "entry.611862537": motivo, "entry.2016051626": meds,
                            "entry.1275746503": val, "entry.949747647": talla, "entry.2091389798": peso,
                            "entry.889985940": ant, "entry.882053172": pa, "entry.1088523869": lab, "entry.616774918": epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución guardada.")
                        st.cache_data.clear()
                        st.rerun()

            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                    <p><b>🔍 MOTIVO:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                    <p><b>💊 MEDICAMENTOS:</b> {f.get('MEDICAMENTOS', 'N/A')}</p>
                    <p><b>📏 TALLA:</b> {f.get('TALLA', 'N/A')} | <b>⚖️ PESO:</b> {f.get('PESO', 'N/A')} | <b>💓 TA:</b> {f.get('PRESIÓN ARTERIAL', 'N/A')}</p>
                    <p><b>🧪 LABS:</b> {f.get('LABORATORIOS', 'N/A')}</p>
                    <p><b>📝 EPICRISIS:</b> {f.get('EPICRISIS', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

# --- SECCIÓN: BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>Base de Datos</h1>", unsafe_allow_html=True)
    if df_p is not None: st.dataframe(df_p)
    if df_h is not None: st.dataframe(df_h)
