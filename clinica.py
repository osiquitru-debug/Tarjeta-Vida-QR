import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. CSS REFORZADO (FORZAR TEXTO NEGRO Y COLORES ORIGINALES) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro en todas las etiquetas y entradas */
    label, p, h1, h2, h3, span, div, input, textarea { 
        color: #000000 !important; 
        font-weight: 600 !important; 
    }
    
    /* Casillas de texto blancas con borde azul */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }

    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIÓN PDF (CORRECCIÓN DEFINITIVA DE FECHA Y DATOS) ---
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
    
    # Mapeo de datos completos
    pdf.cell(0, 8, txt=f"Nombre: {paciente.get('NOMBRE', 'N/R')}", ln=True)
    pdf.cell(0, 8, txt=f"Documento: {paciente.get('DOCUMENTO', 'N/R')} | RH: {paciente.get('RH', 'N/R')} | Edad: {paciente.get('EDAD', 'N/R')}", ln=True)
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
            # Buscamos exactamente como Google Sheets nombra la columna
            fecha = fila.get('MARCA TEMPORAL') or fila.get('TIMESTAMP') or "Fecha no disponible"
            
            pdf.cell(0, 6, txt=f"REGISTRO #{i+1} - FECHA: {fecha}", ln=True)
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
        # Normalizar a MAYÚSCULAS para evitar errores de lectura
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 6. MENÚ Y NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.title("Menú")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"

# --- 7. SECCIÓN CONSULTA (DONDE ESTABA EL FALLO) ---
if st.session_state.menu == "Consulta":
    st.header("Consulta de Paciente")
    id_bus = st.text_input("Ingrese Documento").strip()
    
    if id_bus and df_p is not None:
        # Convertimos a string para comparar correctamente
        paciente = df_p[df_p["DOCUMENTO"].astype(str).str.contains(id_bus)]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"].astype(str).str.contains(id_bus)].reset_index(drop=True)
            
            # Botón de Descarga
            st.download_button("🖨️ Descargar Reporte PDF", data=generar_pdf(p, h_p), file_name=f"Reporte_{id_bus}.pdf")
            
            # Mostrar datos en pantalla
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>Alergias:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Historial con fecha al lado del título
            for i, fila in h_p.iterrows():
                fecha_web = fila.get('MARCA TEMPORAL') or fila.get('TIMESTAMP') or ""
                st.markdown(f"""
                <div class="evolution-card">
                    <b>Evolución #{i+1} - {fecha_web}</b><br>
                    🩺 {fila.get('TRATAMIENTO', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
