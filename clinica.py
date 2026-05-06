import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div { color: #000000 !important; font-weight: 600 !important; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. URLS DE CONEXIÓN ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. FUNCIÓN PDF OPTIMIZADA ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Principal
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MÉDICO INTEGRAL - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # SECCIÓN: DATOS DEL PACIENTE (CORREGIDO)
    pdf.set_fill_color(230, 245, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="INFORMACIÓN DEL PACIENTE", ln=True, fill=True)
    
    pdf.set_font("Arial", '', 11)
    # Fila 1: Nombre y Documento
    pdf.cell(100, 8, txt=f"Nombre: {paciente.get('NOMBRE', '')}", ln=0)
    pdf.cell(0, 8, txt=f"ID: {paciente.get('DOCUMENTO', '')} ({paciente.get('TIPO DE DOCUMENTO', '')})", ln=True)
    
    # Fila 2: Edad, RH y Celular
    pdf.cell(60, 8, txt=f"Edad: {paciente.get('EDAD', '')}", ln=0)
    pdf.cell(40, 8, txt=f"RH: {paciente.get('RH', '')}", ln=0)
    pdf.cell(0, 8, txt=f"Celular: {paciente.get('CELULAR', '')}", ln=True)
    
    # Fila 3: EPS y Emergencia
    pdf.cell(100, 8, txt=f"EPS: {paciente.get('EPS', '')}", ln=0)
    pdf.cell(0, 8, txt=f"Emergencia: {paciente.get('TELEFONO CONTACTO EMERGENCIA', '')}", ln=True)
    
    # Fila 4: Condiciones Especiales
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="Condiciones/Alergias:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, txt=str(paciente.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna registrada')))
    pdf.ln(5)
    
    # SECCIÓN: HISTORIAL (FECHA JUNTO AL TÍTULO)
    pdf.set_fill_color(243, 232, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True, fill=True)
    
    if not historial.empty:
        for i, fila in historial.iterrows():
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            
            # Recuperar fecha para el título
            fecha = fila.get('MARCA DE TIEMPO', '')
            fecha_str = f" - Fecha: {fecha}" if pd.notnull(fecha) and str(fecha).strip() != "" else ""
            
            pdf.cell(0, 8, txt=f"REGISTRO #{i+1}{fecha_str}", ln=True)
            
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=f"Tratamiento: {fila.get('TRATAMIENTO', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}")
            pdf.multi_cell(0, 5, txt=f"Procedimientos: {fila.get('PROCEDIMIENTOS', 'N/R')}")
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
            pdf.ln(3)
            
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. CARGA Y CONSULTA ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 5. INTERFAZ DE USUARIO ---
st.title("🔍 Consulta de Historial")
id_bus = st.text_input("Documento del Paciente").strip()

if id_bus and df_p is not None:
    paciente = df_p[df_p["DOCUMENTO"].astype(str) == id_bus]
    if not paciente.empty:
        p = paciente.iloc[0]
        h_p = df_h[df_h["DOCUMENTO"].astype(str) == id_bus].reset_index(drop=True)
        
        # Botón de Impresión con los datos corregidos
        st.download_button("🖨️ Generar PDF Completo", 
                           data=generar_pdf(p, h_p), 
                           file_name=f"Historia_{id_bus}.pdf")

        # Visualización en pantalla
        st.markdown(f"""
        <div class="medical-card">
            <h2>👤 {p['NOMBRE']}</h2>
            <p><b>Edad:</b> {p['EDAD']} | <b>RH:</b> {p['RH']} | <b>EPS:</b> {p['EPS']}</p>
            <p><b>Alergias:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
            <div class="emergency-box">
                <b>🚨 EMERGENCIA:</b> {p['NOMBRE CONTACTO EMERGENCIA']} - {p['TELEFONO CONTACTO EMERGENCIA']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario para nueva evolución
        with st.form("nueva_evo"):
            st.subheader("✍️ Registrar Evolución")
            fecha_hoy = datetime.now().strftime('%d/%m/%Y')
            t = st.text_input("Tratamiento")
            m = st.text_area("Medicamentos")
            pr = st.text_area("Procedimientos")
            if st.form_submit_button("GUARDAR"):
                requests.post(URL_FORM_HISTORIAL, data={
                    "entry.2019369477": id_bus, 
                    "entry.611862537": t, 
                    "entry.2016051626": m,
                    "entry.1088523869": pr,
                    "entry.1234567890": fecha_hoy # ID de fecha en tu form
                })
                st.success("Registro guardado. Recarga para ver cambios.")
