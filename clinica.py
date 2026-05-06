import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (TEXTO NEGRO Y ESTILOS ORIGINALES) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div { color: #000000 !important; font-weight: 600 !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    input, textarea { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIÓN PDF (FECHA EN TÍTULO Y DATOS COMPLETOS) ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MÉDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # Datos del Paciente
    pdf.set_fill_color(240, 255, 244)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DATOS DEL PACIENTE", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"Nombre: {paciente.get('NOMBRE', 'N/R')}", ln=True)
    pdf.cell(0, 8, txt=f"ID: {paciente.get('DOCUMENTO', 'N/R')} | RH: {paciente.get('RH', 'N/R')} | Edad: {paciente.get('EDAD', 'N/R')}", ln=True)
    pdf.cell(0, 8, txt=f"EPS: {paciente.get('EPS', 'N/R')} | Celular: {paciente.get('CELULAR', 'N/R')}", ln=True)
    pdf.multi_cell(0, 8, txt=f"Condiciones: {paciente.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}")
    pdf.ln(5)
    
    # Evoluciones
    pdf.set_fill_color(243, 232, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True, fill=True)
    
    if not historial.empty:
        for i, fila in historial.iterrows():
            pdf.set_font("Arial", 'B', 10)
            pdf.ln(3)
            fecha = fila.get('MARCA DE TIEMPO', '')
            pdf.cell(0, 6, txt=f"REGISTRO #{i+1} - Fecha: {fecha}", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=f"Tratamiento: {fila.get('TRATAMIENTO', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Procedimientos: {fila.get('PROCEDIMIENTOS', 'N/R')}")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

def obtener_valor(df_row, keywords):
    for col in df_row.index:
        if all(word.upper() in col.upper() for word in keywords):
            return df_row[col]
    return "No registrado"

# --- 6. NAVEGACIÓN LATERAL (RESTAURADA) ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 7. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Número de Documento")
        condiciones = st.text_area("Condiciones Especiales / Alergias")
        edad = st.text_input("Edad")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = st.text_input("EPS")
        cel = st.text_input("Celular")
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": cedula.strip(),
                    "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones, 
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == id_bus].reset_index(drop=True)
            
            st.download_button("🖨️ Descargar PDF Completo", data=generar_pdf(p, h_p), file_name=f"Reporte_{id_bus}.pdf")

            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <p><b>Condiciones:</b> {obtener_valor(p, ["CONDICIONES"])}</p>
                <div class="emergency-box">
                    <p style="margin:0; color: #c53030 !important;"><b>🚨 EMERGENCIA:</b></p>
                    <p style="margin:0;">{p.get('NOMBRE CONTACTO EMERGENCIA', '')} - {p.get('TELEFONO CONTACTO EMERGENCIA', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for i in range(len(h_p)-1, -1, -1):
                fila = h_p.iloc[i]
                ts = fila.get('MARCA DE TIEMPO', '')
                st.markdown(f"""
                <div class="evolution-card">
                    <b>Evolución #{i+1} - Fecha: {ts}</b><br>
                    🩺 <b>Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/A')}<br>
                    💊 <b>Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/A')}<br>
                    📋 <b>Procedimientos:</b> {fila.get('PROCEDIMIENTOS', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución")
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                pr = st.text_area("Procedimientos")
                if st.form_submit_button("GUARDAR"):
                    requests.post(URL_FORM_HISTORIAL, data={
                        "entry.2019369477": id_bus, "entry.611862537": t, 
                        "entry.2016051626": m, "entry.1088523869": pr
                    })
                    st.cache_data.clear()
                    st.rerun()

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    if df_p is not None: st.dataframe(df_p)
