import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (CENTRAR LOGO Y TEXTO NEGRO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li { color: #000000 !important; font-weight: 600 !important; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; 
        border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; 
        border-left: 8px solid #63b3ed; margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLS Y RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
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

# --- 5. FUNCIÓN PDF (ACTUALIZADA CON EPICRISIS) ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MÉDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # Datos Personales
    pdf.set_fill_color(240, 255, 244)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DATOS DEL PACIENTE", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"Nombre: {paciente.get('NOMBRE', 'N/R')}", ln=True)
    pdf.cell(0, 8, txt=f"Doc: {paciente.get('DOCUMENTO', 'N/R')} ({paciente.get('TIPO DE DOCUMENTO', 'N/R')})", ln=True)
    pdf.cell(0, 8, txt=f"EPS: {paciente.get('EPS', 'N/R')} | RH: {paciente.get('RH', 'N/R')}", ln=True)
    pdf.multi_cell(0, 8, txt=f"Condiciones: {paciente.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}")
    pdf.ln(5)
    
    # Evoluciones
    pdf.set_fill_color(243, 232, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True, fill=True)
    
    if not historial.empty:
        for i, fila in historial.iterrows():
            pdf.set_font("Arial", 'B', 10)
            fecha = fila.get('MARCA TEMPORAL') or "S/F"
            pdf.ln(2)
            pdf.cell(0, 7, txt=f"REGISTRO #{i+1} - FECHA: {fecha}", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=f"Motivo: {fila.get('MOTIVO DE LA CONSULTA', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Valoración: {fila.get('VALORACIÓN', 'N/R')}")
            pdf.cell(0, 5, txt=f"Talla: {fila.get('TALLA', 'N/R')} | Peso: {fila.get('PESO', 'N/R')} | PA: {fila.get('PRESIÓN ARTERIAL', 'N/R')}", ln=True)
            pdf.multi_cell(0, 5, txt=f"Antecedentes: {fila.get('ANTECEDENTES MEDICOS', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Laboratorios: {fila.get('LABORATORIOS', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Epicrisis: {fila.get('EPICRISIS', 'N/R')}")
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
            pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 6. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 7. LOGO CENTRADO CABECERA ---
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        tipo_doc = st.selectbox("Tipo de documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería", "Pasaporte", "Registro Civil"])
        cedula = st.text_input("Número de Documento")
        edad = st.text_input("Edad")
        cel = st.text_input("Número de Celular")
        eps = st.text_input("EPS")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        condiciones = st.text_area("Condiciones Especiales / Alergias")
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.845812971": tipo_doc,
                    "entry.1302424820": cedula.strip(), "entry.1801154005": edad, 
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones, 
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta de Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == id_bus].reset_index(drop=True)
            st.download_button("🖨️ Descargar PDF", data=generar_pdf(p, h_p), file_name=f"Reporte_{id_bus}.pdf")
            
            # Tarjeta Principal
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="margin:0;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>Doc:</b> {id_bus} ({p.get('TIPO DE DOCUMENTO', 'N/A')}) | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>Cel:</b> {p.get('CELULAR', 'N/A')}</p>
                <p><b>Condiciones:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
                <div class="emergency-box">
                    <b>🚨 EMERGENCIA:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', '')} - {p.get('TELEFONO CONTACTO EMERGENCIA', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Evoluciones detalladas
            st.subheader("Evoluciones Registradas")
            for i in range(len(h_p)-1, -1, -1):
                fila = h_p.iloc[i]
                ts = fila.get('MARCA TEMPORAL') or "S/F"
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="border-bottom: 1px solid #63b3ed; padding-bottom: 5px;"><b>📅 Fecha: {ts}</b></p>
                    <p><b>🔍 Motivo:</b> {fila.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                    <p><b>📝 Valoración:</b> {fila.get('VALORACIÓN', 'N/A')}</p>
                    <p><b>📏 Talla:</b> {fila.get('TALLA', 'N/A')} | <b>⚖️ Peso:</b> {fila.get('PESO', 'N/A')} | <b>💓 PA:</b> {fila.get('PRESIÓN ARTERIAL', 'N/A')}</p>
                    <p><b>📜 Antecedentes:</b> {fila.get('ANTECEDENTES MEDICOS', 'N/A')}</p>
                    <p><b>💊 Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/A')}</p>
                    <p><b>🧪 Laboratorios:</b> {fila.get('LABORATORIOS', 'N/A')}</p>
                    <p><b>📋 Epicrisis:</b> {fila.get('EPICRISIS', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

            # Formulario de Evolución Actualizado
            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución Médica")
                col1, col2 = st.columns(2)
                with col1:
                    motivo = st.text_input("Motivo de la Consulta")
                    talla = st.text_input("Talla (cm)")
                    presion = st.text_input("Presión Arterial")
                with col2:
                    valoracion = st.text_input("Valoración")
                    peso = st.text_input("Peso (kg)")
                    
                antecedentes = st.text_area("Antecedentes Médicos")
                medicamentos = st.text_area("Medicamentos")
                laboratorios = st.text_area("Laboratorios / Procedimientos")
                epicrisis = st.text_area("Epicrisis")
                
                if st.form_submit_button("GUARDAR REGISTRO"):
                    payload_h = {
                        "entry.2019369477": id_bus,
                        "entry.611862537": motivo,
                        "entry.1275746503": valoracion,
                        "entry.949747647": talla,
                        "entry.2091389798": peso,
                        "entry.889985940": antecedentes,
                        "entry.2016051626": medicamentos,
                        "entry.882053172": presion,
                        "entry.1088523869": laboratorios,
                        "entry.616774918": epicrisis
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.cache_data.clear()
                    st.rerun()

elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>Base de Datos</h1>", unsafe_allow_html=True)
    if df_p is not None: st.dataframe(df_p)
