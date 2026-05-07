import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN INICIAL (DEBE SER LO PRIMERO) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- 2. ESTILO CSS (DIRECTO Y GARANTIZADO) ---
st.markdown("""
    <style>
    /* Fondo y texto general */
    .stApp { background-color: #f0fff4 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; }
    
    /* Tarjeta del Paciente */
    .medical-card {
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); 
        margin-bottom: 20px;
    }
    
    /* Caja de Emergencia */
    .emergency-box { 
        background-color: #fff5f5; 
        padding: 12px; 
        border-radius: 10px; 
        border: 2px dashed #f56565; 
        color: #e53e3e; 
        font-weight: bold;
    }
    
    /* Tarjetas de Historial */
    .evo-card {
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #e2e8f0; 
        border-left: 8px solid #63b3ed; 
        margin-bottom: 15px;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLs DE DATOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

# Form Responses
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=2)
def cargar_datos():
    try:
        # Cargamos ambas hojas
        df_pacientes = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        df_historial = pd.read_csv(f"{URL_CSV}&sheet=historial")
        
        # Estandarizar columnas a MAYÚSCULAS
        df_pacientes.columns = df_pacientes.columns.str.strip().str.upper()
        df_historial.columns = df_historial.columns.str.strip().str.upper()
        
        # Limpiar columna DOCUMENTO para evitar el ".0"
        if 'DOCUMENTO' in df_pacientes.columns:
            df_pacientes['DOCUMENTO'] = df_pacientes['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        if 'DOCUMENTO' in df_historial.columns:
            df_historial['DOCUMENTO'] = df_historial['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
            
        return df_pacientes, df_historial
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 5. INTERFAZ DE NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.markdown("---")
    if st.button("📝 Nuevo Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"

# --- 6. VISTA: REGISTRAR ---
if st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("form_p", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Documento")
            edad = st.text_input("Edad")
        with col2:
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
            cel = st.text_input("Celular")
        
        condiciones = st.text_area("Condiciones / Alergias")
        e_nom = st.text_input("Contacto Emergencia")
        e_tel = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1650757004": "App",
                    "entry.1302424820": cedula.strip(), "entry.1801154005": edad,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("Paciente Guardado")
                st.cache_data.clear()

# --- 7. VISTA: CONSULTA (AQUÍ ESTÁ LO QUE BUSCAS) ---
elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta Médica")
    id_bus = st.text_input("Ingrese Documento del Paciente").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- TARJETA ESTÉTICA DEL PACIENTE ---
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>Edad:</b> {p.get('EDAD', 'N/A')}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA', 'N/R')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'N/R')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- FORMULARIO DE EVOLUCIÓN (BASADO EN TU LINK) ---
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        tr = st.text_input("Tratamiento")
                        pr = st.text_area("Procedimientos")
                        ev = st.text_area("Evolución Clínica")
                        nt = st.text_area("Notas de Enfermería")
                    with c2:
                        dg = st.text_area("Diagnóstico")
                        md = st.text_area("Medicamentos")
                        rc = st.text_area("Recomendaciones")
                        ob = st.text_input("Observaciones")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        payload_h = {
                            "entry.2019369477": id_bus, "entry.1088523869": pr,
                            "entry.611862537": tr, "entry.1275746503": ev,
                            "entry.949747647": nt, "entry.2091389798": ob,
                            "entry.889985940": dg, "entry.2016051626": md,
                            "entry.882053172": rc
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("Evolución Guardada")
                        st.cache_data.clear()
                        st.rerun()

            # --- HISTORIAL VISUAL (TARJETAS) ---
            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
            
            if not h_p.empty:
                for _, fila in h_p.sort_index(ascending=False).iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <b>📅 Fecha:</b> {fila.get('MARCA TEMPORAL', 'S/F')}<br>
                        <b>🩺 Diagnóstico:</b> {fila.get('DIAGNOSTICO', 'N/R')}<br>
                        <b>💊 Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/R')}<br>
                        <b>📋 Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/R')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay historial registrado.")
        else:
            st.warning("Paciente no registrado.")
