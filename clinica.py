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

# --- 2. DISEÑO Y ESTILOS (BASADOS EN LA PALETA DEL LOGO) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #f0f4f8;
    }

    /* FORZAR VISIBILIDAD DE LABELS (ETIQUETAS) */
    label, .stMarkdown p, .stSelectbox label, .stTextInput label {
        color: #1a4f7e !important; /* Azul oscuro del logo para etiquetas */
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Sidebar - Azul profundo */
    [data-testid="stSidebar"] {
        background-color: #1a4f7e !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Títulos */
    h1 {
        color: #1a4f7e;
        text-align: center;
        font-weight: bold;
    }
    h2, h3 {
        color: #008b8b; /* Tono cian oscuro */
        border-bottom: 2px solid #00c4cc;
    }

    /* Tarjetas de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #00c4cc;
        margin-bottom: 20px;
        color: #2d3748;
    }

    /* Botones - Cian del logo */
    div.stButton > button {
        background-color: #00c4cc !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1a4f7e !important;
        box-shadow: 0 4px 12px rgba(0, 196, 204, 0.4);
    }

    /* Contenedor del logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VARIABLES DE CONEXIÓN ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except: return None, None

df_pacientes, df_historial = cargar_datos()

# --- 5. CABECERA ---
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
try:
    # Intento de carga robusta
    resp = requests.get(URL_LOGO_DIRECTA)
    logo_img = Image.open(io.BytesIO(resp.content))
    st.image(logo_img, width=300)
except:
    st.warning("⚠️ El logo no pudo cargarse desde Drive. Revisa que el enlace sea público.")
st.markdown("</div>", unsafe_allow_html=True)

st.title("Sistema Tarjeta Vida")
st.markdown("---")

# --- 6. NAVEGACIÓN ---
menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Seleccione una opción", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Formulario de Registro")
    with st.form("registro_p", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo del Paciente")
        documento = col2.text_input("Número de Documento (Cédula)")
        edad = col1.text_input("Edad Actual")
        rh = col2.selectbox("Grupo Sanguíneo (RH)", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = col1.text_input("Nombre de la EPS")
        celular = col2.text_input("Número de Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nombre = col1.text_input("Nombre del contacto de emergencia")
        e_tel = col2.text_input("Teléfono del contacto de emergencia")
        
        if st.form_submit_button("Guardar Datos del Paciente"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": documento,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.1892763134": e_nombre, "entry.2011749615": e_tel
                }
                if requests.post(URL_FORM_PACIENTES, data=payload).ok:
                    st.success("✅ Registro exitoso.")
                    st.cache_data.clear()
            else: st.warning("⚠️ El nombre y documento son obligatorios.")

elif choice == "Consulta e Historial":
    st.subheader("🔍 Consultar Expediente")
    id_buscar = st.text_input("Ingrese la Cédula a buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        pac = df_pacientes[df_pacientes["DOCUMENTO"] == id_buscar]
        
        if not pac.empty:
            p = pac.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>ID:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📅 Historial de Atenciones"):
                if df_historial is not None:
                    df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                    h = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                    st.dataframe(h.iloc[::-1], use_container_width=True) if not h.empty else st.info("No hay historial.")
            
            st.subheader("✍️ Registrar Evolución Médica")
            with st.form("hist_f", clear_on_submit=True):
                trat = st.text_input("Diagnóstico / Tratamiento")
                obs = st.text_area("Notas y Medicamentos")
                if st.form_submit_button("Guardar Evolución"):
                    payload_h = {"entry.2019369477": id_buscar, "entry.611862537": trat, "entry.2016051626": obs}
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).ok:
                        st.success("✅ Evolución guardada.")
                        st.rerun()
        else: st.error("Paciente no encontrado.")

else:
    st.subheader("📊 Bases de Datos del Sistema")
    t1, t2 = st.tabs(["Listado de Pacientes", "Historial de Evoluciones"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
