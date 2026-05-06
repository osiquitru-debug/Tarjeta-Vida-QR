import streamlit as st
import pandas as pd
import requests
import io
from PIL import Image

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro para visibilidad */
    html, body, [class*="st-"], p, label, h1, h2, h3, span, div {
        color: #000000 !important;
        font-weight: 500;
    }

    /* Inputs con fondo blanco y texto negro real */
    input, textarea, [data-baseweb="select"], [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f3e8ff !important;
        border-right: 2px solid #d8b4fe;
    }
    
    .stSidebar button {
        width: 100%;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d8b4fe !important;
        font-weight: bold !important;
        margin-bottom: 10px;
    }

    /* Botón de Guardar */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important;
        color: #000000 !important;
        border-radius: 12px;
        font-weight: 900 !important;
        border: 2px solid #285e61;
        height: 3.5em;
    }

    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #b2f5ea;
        border-left: 15px solid #4fd1c5;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

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

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.markdown("### 🏥 **MENÚ**")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.subheader("📝 Registro de Nuevo Paciente")
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        
        c1, c2 = st.columns(2)
        # --- NUEVO CAMPO SOLICITADO ---
        tipo_doc = c1.selectbox("Tipo de Documento", [
            "Registro Civil", 
            "Tarjeta de Identidad", 
            "Cedula de Ciudadania", 
            "Cedula de Extranjeria"
        ])
        cedula = c2.text_input("Número de Documento")
        
        c3, c4 = st.columns(2)
        edad = c3.text_input("Edad")
        rh = c4.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c5, c6 = st.columns(2)
        eps = c5.text_input("EPS")
        cel = c6.text_input("Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ce1, ce2 = st.columns(2)
        e_nom = ce1.text_input("Nombre contacto emergencia")
        e_tel = ce2.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                # Se mantienen los IDs configurados anteriormente
                payload = {
                    "entry.346175428": nombre,
                    "entry.1302424820": cedula,
                    "entry.1801154005": edad,
                    "entry.162368130": rh,
                    "entry.1043165037": cel,
                    "entry.1172011247": eps,
                    "entry.1892763134": e_nom,
                    "entry.2011749615": e_tel,
                    # Nota: Si agregas Tipo de Doc al Form, pon aquí su entry.ID
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ Paciente {nombre} registrado.")
                st.cache_data.clear()
            else: st.error("⚠️ Nombre y Documento son obligatorios.")

elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Consulta e Historial")
    id_bus = st.text_input("Ingrese Documento para buscar")
    
    if id_bus and df_p is not None:
        df_p["DOCUMENTO"] = df_p["DOCUMENTO"].astype(str).str.strip()
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>{p.get('TIPO DE DOCUMENTO', 'Documento')}:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div style="background-color: #fff5f5; padding: 10px; border-radius: 8px; border: 1px dashed red;">
                    <p style="color: red; margin:0;"><b>🚨 EMERGENCIA:</b> {p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'No registrado')}</p>
                    <p style="margin:0;"><b>TEL:</b> {p.get('TELEFONO DE CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar Historial
            if df_h is not None:
                df_h["DOCUMENTO"] = df_h["DOCUMENTO"].astype(str).str.strip()
                h_p = df_h[df_h["DOCUMENTO"] == id_bus]
                st.write("### 📅 Evoluciones")
                st.dataframe(h_p[["FECHA", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"]].iloc[::-1], use_container_width=True, hide_index=True)

            # Nueva Evolución
            with st.form("h_form", clear_on_submit=True):
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                pr = st.text_area("Procedimientos")
                if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                    payload_h = {"entry.2019369477": id_bus, "entry.611862537": t, "entry.2016051626": m, "entry.1088523869": pr}
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.success("✅ Historial actualizado.")
                    st.cache_data.clear()
                    st.rerun()
        else: st.error("Paciente no encontrado.")

else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_p is not None: t1.dataframe(df_p)
    if df_h is not None: t2.dataframe(df_h)
