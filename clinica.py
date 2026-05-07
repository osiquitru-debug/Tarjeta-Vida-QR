import streamlit as st
import pandas as pd
import requests

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
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
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

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"
with st.sidebar:
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 5. CONSULTA Y EVOLUCIÓN (CAMPOS ESTRICTAMENTE SOLICITADOS) ---
if st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    id_bus = st.text_input("Documento del Paciente").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # TARJETA DE PACIENTE (ESTÉTICA BASE)
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA', 'S/D')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'S/D')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # FORMULARIO DE HISTORIAL (CAMPOS EXACTOS SOLICITADOS)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("form_h", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        valoracion = st.text_area("Valoración")
                        motivo = st.text_area("Motivo de la Consulta")
                        talla = st.text_input("Talla")
                        peso = st.text_input("Peso")
                        presion = st.text_input("Presión Arterial")
                    with col2:
                        antecedentes = st.text_area("Antecedentes Médicos")
                        medicamentos = st.text_area("Medicamentos")
                        laboratorios = st.text_area("Laboratorios - Procedimientos")
                        epicrisis = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        payload_h = {
                            "entry.2019369477": id_bus,        # Documento
                            "entry.889985940": valoracion,     # Mapeado a Valoración
                            "entry.611862537": motivo,         # Mapeado a Motivo
                            "entry.2016051626": medicamentos,  # Medicamentos
                            "entry.1088523869": laboratorios,  # Lab - Proc
                            "entry.1275746503": epicrisis,     # Epicrisis
                            "entry.882053172": antecedentes,   # Antecedentes
                            "entry.949747647": presion,        # Presión
                            "entry.616774918": talla,          # Talla
                            "entry.2091389798": peso           # Peso
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("Guardado")
                        st.cache_data.clear()
                        st.rerun()

            # HISTORIAL (CAMPOS EXACTOS SOLICITADOS)
            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
            if not h_p.empty:
                for _, f in h_p.sort_index(ascending=False).iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL', 'S/F')}</small><br>
                        <b>Valoración:</b> {f.get('VALORACION', 'N/R')}<br>
                        <b>Motivo de la Consulta:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/R')}<br>
                        <b>Talla:</b> {f.get('TALLA', 'N/R')} | <b>Peso:</b> {f.get('PESO', 'N/R')} | <b>Presión Arterial:</b> {f.get('PRESION ARTERIAL', 'N/R')}<br>
                        <b>Antecedentes Médicos:</b> {f.get('ANTECEDENTES MEDICOS', 'N/R')}<br>
                        <b>Medicamentos:</b> {f.get('MEDICAMENTOS', 'N/R')}<br>
                        <b>Laboratorios - Procedimientos:</b> {f.get('LABORATORIOS - PROCEDIMIENTOS', 'N/R')}<br>
                        <b>Epicrisis:</b> {f.get('EPICRICIS', 'N/R')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay registros previos.")
        else:
            st.warning("Paciente no encontrado.")
