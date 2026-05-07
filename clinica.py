import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN Y ESTILO ---
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

# URLs de envío (Terminadas en formResponse)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. FUNCIONES CORE ---
@st.cache_data(ttl=5)
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
    pdf.cell(0, 10, "REPORTE MEDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # Datos Paciente
    pdf.set_fill_color(230, 245, 240)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" PACIENTE: {paciente.get('NOMBRE', 'N/R')}", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    info = (f"Documento: {paciente.get('DOCUMENTO', 'N/R')} | RH: {paciente.get('RH', 'N/R')}\n"
            f"Edad: {paciente.get('EDAD', 'N/R')} | EPS: {paciente.get('EPS', 'N/R')}\n"
            f"Condiciones: {paciente.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}")
    pdf.multi_cell(0, 8, info.encode('latin-1', 'replace').decode('latin-1'))
    
    # Evoluciones
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " HISTORIAL DE EVOLUCIONES", ln=True, fill=True)
    
    for _, fila in historial.iterrows():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"FECHA: {fila.get('MARCA TEMPORAL', 'S/F')}", ln=True)
        pdf.set_font("Arial", '', 9)
        evo_txt = (f"Diagnóstico: {fila.get('DIAGNOSTICO', 'N/R')}\n"
                   f"Tratamiento: {fila.get('TRATAMIENTO', 'N/R')}\n"
                   f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}")
        pdf.multi_cell(0, 5, evo_txt.encode('latin-1', 'replace').decode('latin-1'))
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
    return pdf.output(dest='S')

# --- 4. INTERFAZ ---
df_p, df_h = cargar_datos()

if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.markdown("### PANEL MÉDICO")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# SECCIÓN: REGISTRO (Basado en el primer link)
if st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Documento de Identidad")
            edad = st.text_input("Edad")
        with col2:
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
            cel = st.text_input("Teléfono")
        
        condiciones = st.text_area("Condiciones Especiales / Alergias")
        e_nom = st.text_input("Nombre de contacto emergencia")
        e_tel = st.text_input("Teléfono de contacto emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload_p = {
                    "entry.346175428": nombre,
                    "entry.1650757004": "Web_App",
                    "entry.1302424820": cedula.strip(),
                    "entry.1801154005": edad,
                    "entry.1043165037": cel,
                    "entry.1172011247": eps,
                    "entry.162368130": rh,
                    "entry.346363": condiciones,
                    "entry.1892763134": e_nom,
                    "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload_p)
                st.success(f"✅ Paciente {nombre} registrado.")
                st.cache_data.clear()

# SECCIÓN: CONSULTA (Basado en el segundo link - 10 campos)
elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    id_bus = st.text_input("Ingrese Documento del Paciente").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == id_bus]
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA', 'S/D')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'S/D')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.download_button("🖨️ Descargar Historia Clínica", data=generar_pdf(p, h_p), file_name=f"HC_{id_bus}.pdf")
            
            with st.expander("✍️ REGISTRAR NUEVA ATENCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        tratamiento = st.text_input("Tratamiento")
                        procedimientos = st.text_area("Procedimientos")
                        evolucion = st.text_area("Evolución Clínica")
                        notas = st.text_area("Notas de Enfermería")
                        obs = st.text_input("Observaciones")
                    with c2:
                        medicamentos = st.text_area("Medicamentos")
                        diagnostico = st.text_area("Diagnóstico")
                        recomendaciones = st.text_area("Recomendaciones")
                        examenes = st.text_input("Exámenes")
                        otro = st.text_input("Dato Adicional") # entry.616774918 aprox
                    
                    if st.form_submit_button("💾 GUARDAR EVOLUCIÓN"):
                        payload_h = {
                            "entry.2019369477": id_bus,
                            "entry.1088523869": procedimientos,
                            "entry.611862537": tratamiento,
                            "entry.1275746503": evolucion,
                            "entry.949747647": notas,
                            "entry.2091389798": obs,
                            "entry.889985940": diagnostico,
                            "entry.2016051626": medicamentos,
                            "entry.882053172": recomendaciones,
                            "entry.616774918": examenes
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución guardada.")
                        st.cache_data.clear()
                        st.rerun()

            st.subheader("📋 Antecedentes Clínicos")
            for _, fila in h_p.sort_index(ascending=False).iterrows():
                st.markdown(f"""
                <div class="evo-card">
                    <small>📅 {fila.get('MARCA TEMPORAL', 'S/F')}</small><br>
                    <b>Diagnóstico:</b> {fila.get('DIAGNOSTICO', 'N/R')}<br>
                    <b>Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/R')}<br>
                    <b>Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/R')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Paciente no encontrado.")
