import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. CSS OPTIMIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
        color: #000000 !important;
    }
    .condition-box {
        background-color: #fffaf0; padding: 10px; border-radius: 8px;
        border: 1px solid #feebc8; margin: 10px 0;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 12px; border-radius: 10px;
        border: 2px dashed #f56565; margin-top: 15px;
    }
    label, p, h2, b { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        p.columns = p.columns.str.strip().str.upper()
        if 'DOCUMENTO' in p.columns:
            p['DOCUMENTO'] = p['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p
    except: return None

def limpiar_texto(valor):
    if pd.isna(valor) or str(valor).lower() == 'nan':
        return "Ninguna"
    return str(valor)

df_p = cargar_datos()

# --- 4. SECCIÓN DE CONSULTA ---
st.markdown("<h1 style='text-align: center;'>🩺 Consulta de Paciente</h1>", unsafe_allow_html=True)
id_bus = st.text_input("Ingrese Documento").strip()

if id_bus and df_p is not None:
    paciente = df_p[df_p["DOCUMENTO"] == id_bus]
    
    if not paciente.empty:
        p = paciente.iloc[0]
        
        # Extracción manual y limpia de campos
        nombre_paciente = p.get('NOMBRE', 'No registrado')
        rh = p.get('RH', 'N/A')
        eps = p.get('EPS', 'Emcosalud')
        celular = p.get('CELULAR', 'N/A')
        
        # Manejo de Alergias y Emergencias
        alergias = limpiar_texto(p.get('ALERGIAS') or p.get('ALERGIA') or p.get('CONDICIONES'))
        e_nombre = limpiar_texto(p.get('NOMBRE CONTACTO EMERGENCIA') or p.get('NOMBRE DEL CONTACTO DE EMERGENCIA'))
        e_tel = limpiar_texto(p.get('TELÉFONO CONTACTO DE EMERGENCIA') or p.get('TELÉFONO CONTACTO'))

        # TARJETA VISUAL
        st.markdown(f"""
        <div class="medical-card">
            <h2 style="margin:0;">👤 {nombre_paciente}</h2>
            <p style="margin:5px 0;"><b>ID:</b> {id_bus} | <b>RH:</b> {rh}</p>
            
            <div class="condition-box">
                <p style="color: #856404 !important; margin: 0; font-size: 0.9em;"><b>⚠️ CONDICIONES Y ALERGIAS:</b></p>
                <p style="margin: 0;">{alergias}</p>
            </div>
            
            <p style="margin:5px 0;"><b>EPS:</b> {eps} | <b>CEL:</b> {celular}</p>
            
            <div class="emergency-box">
                <p style="color: red !important; margin:0; font-size: 0.9em;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                <p style="margin:0;"><b>Nombre:</b> {e_nombre}</p>
                <p style="margin:0;"><b>Tel:</b> {e_tel}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🖨️ Preparar para Impresión"):
            st.info("Usa Ctrl+P para guardar como PDF")
    else:
        st.error("Paciente no encontrado.")
