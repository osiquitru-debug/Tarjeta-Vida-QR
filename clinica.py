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

# --- 2. DISEÑO EN TONOS PASTEL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Visibilidad de texto en casillas */
    input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1.5px solid #a2d2ff !important;
    }

    /* Etiquetas y Títulos */
    label, p, h1, h2, h3, .stSubheader {
        color: #2d3748 !important; 
        font-weight: bold !important;
    }

    /* Menú Lateral Lavanda */
    [data-testid="stSidebar"] {
        background-color: #f3e8ff !important;
        border-right: 2px solid #e9d5ff;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #581c87 !important;
    }

    /* Botones Menta */
    div.stButton > button {
        background-color: #99f6e4 !important;
        color: #134e4a !important;
        border-radius: 12px;
        font-weight: bold !important;
        border: 1px solid #5eead4;
    }

    /* Tarjetas de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #b2f5ea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Enlaces de Google Forms (Asegúrate de que los IDs de entrada coincidan en tu Form)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIÓN DE CARGA ---
@st.cache_data(ttl=2)
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
col_1, col_2, col_3 = st.columns([1,2,1])
with col_2:
    try:
        resp = requests.get(URL_LOGO_DIRECTA)
        logo_img = Image.open(io.BytesIO(resp.content))
        st.image(logo_img, use_container_width=True)
    except: st.write("## 🩺 Tarjeta Vida")

st.markdown("<h1 style='text-align: center;'>Gestión Médica Integral</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. MENÚ ---
choice = st.sidebar.selectbox("MENÚ PRINCIPAL", ["Registrar Paciente", "Consulta e Historial", "Base de Datos"])

# --- SECCIÓN 1: REGISTRO ---
if choice == "Registrar Paciente":
    st.subheader("📝 Nuevo Registro de Usuario")
    with st.form("registro_completo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        doc = c2.text_input("Documento de Identidad")
        edad = c1.text_input("Edad")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = c1.text_input("EPS")
        celular = c2.text_input("Teléfono Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nombre = c1.text_input("Nombre del contacto de emergencia")
        e_tel = c2.text_input("Teléfono de contacto de emergencia")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and doc:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": doc,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.1892763134": e_nombre, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ ¡{nombre} registrado!")
                st.cache_data.clear()
            else: st.error("⚠️ Nombre y Documento son obligatorios.")

# --- SECCIÓN 2: CONSULTA E HISTORIAL ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Evolución y Antecedentes")
    id_buscar = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        p_data = df_pacientes[df_pacientes["DOCUMENTO"] == id_buscar]
        
        if not p_data.empty:
            p = p_data.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>Emergencia:</b> {p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'N/A')} ({p.get('TELEFONO DE CONTACTO DE EMERGENCIA', 'N/A')})</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📅 Historial de Atenciones")
            if df_historial is not None:
                df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                h_previo = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                st.dataframe(h_previo.iloc[::-1], use_container_width=True) if not h_previo.empty else st.info("Sin registros previos.")
            
            st.write("---")
            st.subheader("✍️ Registrar Nueva Evolución")
            with st.form("nueva_ev", clear_on_submit=True):
                trat = st.text_input("Tratamiento")
                meds = st.text_area("Medicamentos")
                proc = st.text_area("Procedimientos")
                
                if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                    # Asegúrate de mapear estos entry.ID con los de tu Google Form de Historial
                    payload_h = {
                        "entry.2019369477": id_buscar, 
                        "entry.611862537": trat, 
                        "entry.2016051626": meds,
                        "entry.XXXXXXX": proc # Reemplaza XXXXXXX con el ID de 'Procedimientos' de tu Form
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.success("✅ Datos guardados.")
                    st.cache_data.clear()
                    st.rerun()
        else: st.error("Paciente no encontrado.")

else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
