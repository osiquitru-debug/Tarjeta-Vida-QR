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

# --- 2. DISEÑO CSS PERSONALIZADO (PASTEL) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Inputs y áreas de texto */
    input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1.5px solid #a2d2ff !important;
    }

    /* Estilo del Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f3e8ff !important;
        border-right: 2px solid #e9d5ff;
    }

    /* Botones Laterales de Navegación */
    .stSidebar button {
        width: 100%;
        border-radius: 10px !important;
        border: 1px solid #d8b4fe !important;
        background-color: #ffffff !important;
        color: #581c87 !important;
        margin-bottom: 8px;
        font-weight: bold;
    }
    .stSidebar button:hover {
        background-color: #e9d5ff !important;
        border-color: #a855f7 !important;
    }

    /* Botón de Guardar (Menta) */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #99f6e4 !important;
        color: #134e4a !important;
        border-radius: 12px;
        font-weight: bold !important;
        border: 1px solid #5eead4;
        width: 100%;
        height: 3.2em;
    }

    /* Tarjetas de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 12px solid #b2f5ea;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    .emergency-box {
        background-color: #fff5f5;
        padding: 12px;
        border-radius: 10px;
        border: 1px dashed #feb2b2;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
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

# --- 5. LÓGICA DE NAVEGACIÓN ---
if 'menu' not in st.session_state:
    st.session_state.menu = "Registrar"

def navegar(opcion):
    st.session_state.menu = opcion

with st.sidebar:
    st.markdown("### 🏥 **TARJETA VIDA**")
    st.button("📝 Registrar Paciente", on_click=navegar, args=("Registrar",))
    st.button("🔍 Consulta e Historial", on_click=navegar, args=("Consulta",))
    st.button("📊 Base de Datos", on_click=navegar, args=("Base",))
    st.markdown("---")
    st.caption(f"Sección activa: {st.session_state.menu}")

# --- 6. CABECERA ---
c1, c2, c3 = st.columns([1,2,1])
with c2:
    try:
        logo = Image.open(io.BytesIO(requests.get(URL_LOGO_DIRECTA).content))
        st.image(logo, use_container_width=True)
    except: st.header("🩺 Tarjeta Vida")

st.markdown("<h1 style='text-align: center;'>Gestión Médica Integral</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 7. SECCIONES ---

# --- REGISTRO ---
if st.session_state.menu == "Registrar":
    st.subheader("📝 Nuevo Registro")
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        cedula = col2.text_input("Documento de Identidad")
        edad = col1.text_input("Edad")
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = col1.text_input("EPS")
        cel = col2.text_input("Teléfono Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ce1, ce2 = st.columns(2)
        e_nom = ce1.text_input("Nombre de contacto")
        e_tel = ce2.text_input("Teléfono de contacto")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": cedula,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ {nombre} registrado correctamente.")
                st.cache_data.clear()
            else: st.error("⚠️ Nombre y Documento son obligatorios.")

# --- CONSULTA E HISTORIAL ---
elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Evolución Clínica")
    id_bus = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_bus and df_p is not None:
        df_p["DOCUMENTO"] = df_p["DOCUMENTO"].astype(str).str.strip()
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>ID:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div class="emergency-box">
                    <p style='margin:0; color:#c53030;'><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style='margin:0;'>{p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'No registrado')} — <b>Tel:</b> {p.get('TELEFONO DE CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### 📅 Historial Clínico")
            if df_h is not None:
                df_h["DOCUMENTO"] = df_h["DOCUMENTO"].astype(str).str.strip()
                hist_p = df_h[df_h["DOCUMENTO"] == id_bus]
                if not hist_p.empty:
                    cols = [c for c in ["FECHA", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"] if c in hist_p.columns]
                    st.dataframe(hist_p[cols].iloc[::-1], use_container_width=True, hide_index=True)
                else: st.info("Sin antecedentes registrados.")

            st.markdown("---")
            st.subheader("✍️ Registrar Evolución")
            with st.form("h_form", clear_on_submit=True):
                trat = st.text_input("Tratamiento")
                meds = st.text_area("Medicamentos")
                proc = st.text_area("Procedimientos")
                
                if st.form_submit_button("ACTUALIZAR HISTORIAL"):
                    payload_h = {
                        "entry.2019369477": id_bus, 
                        "entry.611862537": trat, 
                        "entry.2016051626": meds,
                        "entry.1088523869": proc
                    }
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).status_code == 200:
                        st.success("✅ Historial actualizado.")
                        st.cache_data.clear()
                        st.rerun()

# --- BASE DE DATOS ---
else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial General"])
    if df_p is not None: t1.dataframe(df_p, use_container_width=True)
    if df_h is not None: t2.dataframe(df_h, use_container_width=True)
