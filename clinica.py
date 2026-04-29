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

# --- 2. DISEÑO Y ESTILOS (CONTRASTE MEJORADO) ---
st.markdown("""
    <style>
    /* Fondo principal con contraste suave */
    .stApp {
        background-color: #f8fafc;
    }

    /* Sidebar con azul corporativo profundo */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* Títulos con máxima legibilidad */
    h1 {
        color: #1e293b;
        font-weight: 800;
        text-align: center;
        margin-top: -10px;
    }
    h2, h3 {
        color: #0f172a;
        border-bottom: 2px solid #06b6d4;
        padding-bottom: 10px;
    }

    /* Tarjetas de información (Medical Cards) */
    .medical-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        border-left: 6px solid #0891b2;
        margin-bottom: 25px;
    }

    /* Botones de alta visibilidad */
    div.stButton > button {
        background-color: #0891b2 !important; /* Cian oscuro */
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 12px;
        font-weight: bold;
        width: 100%;
        font-size: 16px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #164e63 !important; /* Azul más profundo */
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
    }

    /* Inputs resaltados */
    .stTextInput > div > div > input {
        border: 1px solid #cbd5e1 !important;
    }

    /* Contenedor del logo */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VARIABLES Y CARGA DE IMAGEN ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIONES DE DATOS ---
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

# --- 5. CABECERA Y LOGO ---
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
try:
    # Usamos requests para bajar la imagen y PIL para asegurar que se procese bien
    response = requests.get(URL_LOGO_DIRECTA)
    img = Image.open(io.BytesIO(response.content))
    st.image(img, width=320)
except:
    st.error("No se pudo cargar el logo. Asegúrate de que el archivo en Drive sea 'Público'.")
st.markdown("</div>", unsafe_allow_html=True)

st.title("Sistema Tarjeta Vida")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1em;'>Gestión Médica Integral - Sede Neiva</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. NAVEGACIÓN ---
menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

# --- SECCIÓN: REGISTRO ---
if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Paciente")
    with st.form("form_p", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        doc = col2.text_input("Documento de Identidad")
        edad = col1.text_input("Edad")
        rh = col2.selectbox("Grupo Sanguíneo", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = col1.text_input("EPS")
        cel = col2.text_input("Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = col1.text_input("Nombre de contacto")
        e_tel = col2.text_input("Teléfono de contacto")
        
        if st.form_submit_button("Finalizar Registro"):
            if nombre and doc:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": doc,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                if requests.post(URL_FORM_PACIENTES, data=payload).ok:
                    st.success("¡Paciente registrado correctamente!")
                    st.cache_data.clear()
            else: st.warning("Nombre y Documento son requeridos.")

# --- SECCIÓN: CONSULTA ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Buscar Expediente")
    buscar = st.text_input("Ingrese Cédula para consultar").strip()
    
    if buscar and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        p = df_pacientes[df_pacientes["DOCUMENTO"] == buscar]
        
        if not p.empty:
            res = p.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3 style='border:none; margin:0;'>👤 {res.get('NOMBRE', 'N/A')}</h3>
                <hr style='margin: 10px 0;'>
                <p><b>DOCUMENTO:</b> {res.get('DOCUMENTO', 'N/A')}</p>
                <p><b>EPS:</b> {res.get('EPS', 'N/A')} | <b>RH:</b> {res.get('RH', 'N/A')}</p>
                <p><b>TELÉFONO:</b> {res.get('CELULAR', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🚨 Ver Datos de Emergencia"):
                st.write(f"**Contacto:** {res.get('NOMBRE CONTACTO EMERGENCIA', 'N/A')}")
                st.write(f"**Teléfono:** {res.get('TELEFONO CONTACTO EMERGENCIA', 'N/A')}")

            with st.expander("📅 Ver Evoluciones", expanded=True):
                if df_historial is not None:
                    df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                    h = df_historial[df_historial["DOCUMENTO"] == buscar]
                    st.dataframe(h.iloc[::-1], use_container_width=True) if not h.empty else st.info("No hay historial.")

            st.markdown("### ✍️ Nueva Evolución Médica")
            with st.form("h_form", clear_on_submit=True):
                tra = st.text_input("Tratamiento / Diagnóstico")
                obs = st.text_area("Notas y Medicamentos")
                if st.form_submit_button("Guardar Evolución"):
                    data_h = {"entry.2019369477": buscar, "entry.611862537": tra, "entry.2016051626": obs}
                    if requests.post(URL_FORM_HISTORIAL, data=data_h).ok:
                        st.success("Evolución guardada.")
                        st.rerun()
        else: st.error("Paciente no encontrado.")

# --- SECCIÓN: BASE DE DATOS ---
else:
    st.subheader("📊 Datos del Sistema")
    t1, t2 = st.tabs(["Lista de Pacientes", "Historial General"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
