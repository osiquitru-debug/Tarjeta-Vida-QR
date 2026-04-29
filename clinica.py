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

# --- 2. DISEÑO Y ESTILOS (CONTRASTE TOTAL) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #f8fafc;
    }

    /* FORZAR VISIBILIDAD DE LABELS Y TÍTULOS DE SECCIÓN */
    label, .stMarkdown p, h1, h2, h3, .stSubheader {
        color: #1a4f7e !important; 
        font-weight: 700 !important;
    }

    /* Estilo específico para los nombres de las pestañas (Tabs) */
    button[data-baseweb="tab"] p {
        color: #1a4f7e !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a4f7e !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Tarjetas de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #00c4cc;
        margin-bottom: 20px;
    }
    .medical-card h3, .medical-card p {
        color: #1a4f7e !important;
    }

    /* Botones */
    div.stButton > button {
        background-color: #00c4cc !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        height: 3em;
    }
    div.stButton > button:hover {
        background-color: #1a4f7e !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div {
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
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
col1, col2, col3 = st.columns([1,2,1])
with col2:
    try:
        resp = requests.get(URL_LOGO_DIRECTA)
        logo_img = Image.open(io.BytesIO(resp.content))
        st.image(logo_img, use_container_width=True)
    except:
        st.write("### Tarjeta Vida")

st.markdown("<h1 style='text-align: center;'>Sistema Tarjeta Vida</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. NAVEGACIÓN ---
menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Paciente")
    with st.form("registro_p", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        nombre = col_a.text_input("Nombre Completo")
        documento = col_b.text_input("Número de Cédula")
        edad = col_a.text_input("Edad")
        rh = col_b.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = col_a.text_input("EPS")
        celular = col_b.text_input("Celular")
        
        st.subheader("🚨 Contacto de Emergencia")
        e_nombre = col_a.text_input("Nombre contacto")
        e_tel = col_b.text_input("Teléfono contacto")
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": documento,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.1892763134": e_nombre, "entry.2011749615": e_tel
                }
                if requests.post(URL_FORM_PACIENTES, data=payload).ok:
                    st.success("✅ Paciente registrado.")
                    st.cache_data.clear()
            else: st.warning("⚠️ Nombre y Cédula son obligatorios.")

elif choice == "Consulta e Historial":
    st.subheader("🔍 Consultar Expediente")
    id_buscar = st.text_input("Cédula a buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        pac = df_pacientes[df_pacientes["DOCUMENTO"] == id_buscar]
        
        if not pac.empty:
            p = pac.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>Cédula:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📅 Historial Clínico")
            if df_historial is not None:
                df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                h = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                st.dataframe(h.iloc[::-1], use_container_width=True) if not h.empty else st.info("Sin registros.")
            
            st.subheader("✍️ Nueva Evolución")
            with st.form("hist_f", clear_on_submit=True):
                trat = st.text_input("Tratamiento")
                obs = st.text_area("Observaciones")
                if st.form_submit_button("Guardar Evolución"):
                    payload_h = {"entry.2019369477": id_buscar, "entry.611862537": trat, "entry.2016051626": obs}
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).ok:
                        st.success("✅ Guardado.")
                        st.rerun()
        else: st.error("No encontrado.")

else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes Registrados", "Historial de Evoluciones"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
