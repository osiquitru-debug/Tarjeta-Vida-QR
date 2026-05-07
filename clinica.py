import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN Y ESTILO (ESTÉTICA BASE ORIGINAL) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #000;
    }
    .emergency-box { 
        background-color: #fff5f5; padding: 10px; border-radius: 8px; 
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; border-left: 5px solid #63b3ed; margin-bottom: 10px;
    }
    h1, h2, h3, label, p { color: #1a202c !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RECURSOS Y URLs ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. FUNCIONES AUXILIARES ---
@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except:
        return None, None

def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "HISTORIAL CLÍNICO - TARJETA VIDA", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Paciente: {paciente.get('NOMBRE', 'N/A')}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 8, f"Documento: {paciente.get('DOCUMENTO', 'N/A')} | RH: {paciente.get('RH', 'N/A')}", ln=True)
    pdf.ln(5)
    
    for _, fila in historial.iterrows():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"Fecha: {fila.get('MARCA TEMPORAL', 'S/F')}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        pdf.multi_cell(0, 6, f"Motivo: {fila.get('MOTIVO DE LA CONSULTA', 'N/R')}\n"
                             f"Valoración: {fila.get('VALORACION', 'N/R')}\n"
                             f"Signos: Talla: {fila.get('TALLA', 'N/R')} | Peso: {fila.get('PESO', 'N/R')} | PA: {fila.get('PRESION ARTERIAL', 'N/R')}\n"
                             f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}\n"
                             f"Epicrisis: {fila.get('EPICRISIS', 'N/R')}")
        pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1', 'replace')

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.markdown("### PANEL MÉDICO")
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Bienvenido a Tarjeta Vida")
    st.info("Utilice el menú lateral para gestionar pacientes o consultar historiales.")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("form_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            doc = st.text_input("Documento de Identidad")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        if st.form_submit_button("GUARDAR"):
            requests.post(URL_FORM_PACIENTES, data={"entry.346175428": nom, "entry.1302424820": doc, "entry.1172011247": eps, "entry.162368130": rh})
            st.success("Registrado.")

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    id_bus = st.text_input("Documento del Paciente").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f'<div class="medical-card"><h2>👤 {p.get("NOMBRE")}</h2><p>ID: {id_bus} | RH: {p.get("RH")}</p></div>', unsafe_allow_html=True)
            
            # FORMULARIO CON 10 CAMPOS
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("evo_f", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        v1 = st.text_area("Valoración")
                        v2 = st.text_area("Motivo de la Consulta")
                        v3 = st.text_input("Talla")
                        v4 = st.text_input("Peso")
                        v5 = st.text_input("Presión Arterial")
                    with col2:
                        v6 = st.text_area("Antecedentes Medicos")
                        v7 = st.text_area("Medicamentos")
                        v8 = st.text_area("Laboratorios - Procedimientos")
                        v9 = st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        requests.post(URL_FORM_HISTORIAL, data={
                            "entry.2019369477": id_bus, "entry.889985940": v1, "entry.611862537": v2, 
                            "entry.616774918": v3, "entry.2091389798": v4, "entry.949747647": v5,
                            "entry.882053172": v6, "entry.2016051626": v7, "entry.1088523869": v8, "entry.1275746503": v9
                        })
                        st.rerun()

            # HISTORIAL Y PDF
            h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
            if not h_p.empty:
                st.download_button("📥 Descargar Historial PDF", data=generar_pdf(p, h_p), file_name=f"Historial_{id_bus}.pdf", mime="application/pdf")
                for _, f in h_p.sort_index(ascending=False).iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                    <b>Motivo:</b> {f.get('MOTIVO DE LA CONSULTA')}<br><b>Valoración:</b> {f.get('VALORACION')}</div>""", unsafe_allow_html=True)
