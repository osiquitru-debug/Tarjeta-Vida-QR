import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica", 
    layout="centered", 
    page_icon="🩺"
)

# Estilos CSS Profesionales (Colores basados en tu logo)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f7f4 0%, #d6eaf8 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #1a4f7e !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 0px;
        margin-top: -30px;
    }
    .medical-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #00c4cc;
        margin-bottom: 20px;
    }
    div.stButton > button {
        background-color: #00c4cc;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1a4f7e;
        color: white;
    }
    h1 {
        color: #1a4f7e;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        margin-top: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VARIABLES DE CONEXIÓN ---
SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# ID de tu imagen de Drive extraído del enlace
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH" 
URL_LOGO = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except:
        return None, None

df_pacientes, df_historial = cargar_datos()

# --- 4. CABECERA ---
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image(URL_LOGO, width=280)
st.markdown("</div>", unsafe_allow_html=True)

st.title("Sistema Tarjeta Vida")
st.markdown("<p style='text-align: center; color: #666;'>Gestión Médica Integral</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. NAVEGACIÓN ---
menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- SECCIÓN 1: REGISTRO ---
if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Nuevo Usuario")
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.text_input("Edad")
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = col1.text_input("EPS")
        celular = col2.text_input("Teléfono Celular")
        
        st.markdown("### 🚨 Información de Emergencia")
        e_nombre = col1.text_input("Nombre contacto")
        e_tel = col2.text_input("Teléfono contacto")
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": documento,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.1892763134": e_nombre, "entry.2011749615": e_tel
                }
                if requests.post(URL_FORM_PACIENTES, data=payload).ok:
                    st.success("✅ Registro guardado exitosamente.")
                    st.cache_data.clear()
            else:
                st.warning("⚠️ Nombre y Cédula son obligatorios.")

# --- SECCIÓN 2: CONSULTA ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Consulta de Expediente")
    id_buscar = st.text_input("Ingrese número de Cédula").strip()
    if id_buscar and df_pacientes is not None:
        col_doc = "DOCUMENTO"
        df_pacientes[col_doc] = df_pacientes[col_doc].astype(str).str.strip()
        pac_filtro = df_pacientes[df_pacientes[col_doc] == id_buscar]
        
        if not pac_filtro.empty:
            p = pac_filtro.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>Contacto:</b> {p.get('CELULAR', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📅 Ver Evoluciones Previas"):
                if df_historial is not None:
                    df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                    h_pac = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                    if not h_pac.empty:
                        st.dataframe(h_pac.iloc[::-1], use_container_width=True)
                    else:
                        st.write("No hay historial registrado.")
            
            st.markdown("---")
            st.write("✍️ **Añadir Evolución**")
            with st.form("form_historial", clear_on_submit=True):
                t = st.text_input("Diagnóstico/Tratamiento")
                m = st.text_area("Notas Médicas")
                if st.form_submit_button("Guardar Evolución"):
                    payload_h = {"entry.2019369477": id_buscar, "entry.611862537": t, "entry.2016051626": m}
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).ok:
                        st.success("Evolución registrada.")
                        st.rerun()
        else:
            st.error("Paciente no localizado en la base de datos.")

# --- SECCIÓN 3: BASE DE DATOS ---
else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial General"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
