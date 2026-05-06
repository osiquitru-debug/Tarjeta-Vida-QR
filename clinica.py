import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- CONFIGURACIÓN Y ESTILOS (Mantenemos tus colores y texto negro) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    html, body, [class*="st-"] { color: #000000 !important; font-weight: 600 !important; }
    input, textarea, [data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    /* ... resto de tus estilos ... */
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA CARGAR DATOS (La clave para la Marca de Tiempo) ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargamos las hojas
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        
        # Normalizamos nombres de columnas: quitamos espacios y pasamos a MAYÚSCULAS
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        
        # Limpieza de IDs
        if 'DOCUMENTO' in h.columns:
            h['DOCUMENTO'] = h['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
        return p, h
    except Exception as e:
        st.error(f"Error al cargar: {e}")
        return None, None

# --- FUNCIÓN PDF (Captura automática de la columna de Sheets) ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MÉDICO", ln=True, align='C')
    
    # ... (Bloque de datos del paciente igual al anterior) ...

    if not historial.empty:
        for i, fila in historial.iterrows():
            pdf.set_font("Arial", 'B', 10)
            
            # BUSCAMOS LA MARCA DE TIEMPO AUTOMÁTICA
            # Google Sheets suele llamarla 'MARCA TEMPORAL' o 'TIMESTAMP'
            fecha_auto = fila.get('MARCA TEMPORAL') or fila.get('TIMESTAMP') or "Sin fecha"
            
            pdf.cell(0, 6, txt=f"REGISTRO #{i+1} - FECHA: {fecha_auto}", ln=True)
            
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=f"Tratamiento: {fila.get('TRATAMIENTO', 'N/R')}")
            pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- REGISTRO DE EVOLUCIÓN (Sin enviar fecha manual) ---
# Al no enviar el campo de fecha desde Python, Google Sheets 
# usará su propia función interna para llenar la columna A.
if st.form_submit_button("GUARDAR"):
    payload = {
        "entry.2019369477": id_bus, 
        "entry.611862537": t, 
        "entry.2016051626": m, 
        "entry.1088523869": pr
        # Nota: NO enviamos el entry de la fecha para que Sheets use la suya
    }
    requests.post(URL_FORM_HISTORIAL, data=payload)
    st.rerun()
