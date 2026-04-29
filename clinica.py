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

# --- 2. DISEÑO Y ESTILOS DE ALTA VISIBILIDAD ---
st.markdown("""
    <style>
    /* Fondo de aplicación blanco puro */
    .stApp {
        background-color: #ffffff !important;
    }

    /* TEXTO DE ESCRITURA: Negro total en todos los campos */
    input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #1a4f7e !important;
    }

    /* ETIQUETAS Y TÍTULOS: Azul Marino del Logo */
    label, p, h1, h2, h3, .stSubheader {
        color: #1a4f7e !important; 
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    /* MENÚ LATERAL: Fondo blanco para que las letras se vean */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    /* Texto del menú lateral en azul */
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] p {
        color: #1a4f7e !important;
    }

    /* PESTAÑAS (TABS) */
    button[data-baseweb="tab"] p {
        color: #1a4f7e !important;
        font-weight: 800 !important;
    }

    /* BOTONES: Cian con letras blancas */
    div.stButton > button {
        background-color: #00c4cc !important;
        color: #ffffff !important;
        border-radius: 8px;
        font-weight: 900 !important;
        border: none;
        text-transform: uppercase;
    }

    /* TARJETAS DE HISTORIAL EXISTENTE */
    .medical-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        border-left: 10px solid #00c4cc;
        color: #1a4f7e !important;
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

# --- 4. FUNCIÓN DE CARGA ---
@st.cache_data(ttl=2) # Actualización rápida para ver historial nuevo
def cargar_datos():
    try:
        # Cargamos ambas hojas asegurando que el historial se lea correctamente
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Normalizamos nombres de columnas a mayúsculas
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except: return None, None

df_pacientes, df_historial = cargar_datos()

# --- 5. CABECERA ---
col_l, col_c, col_r = st.columns([1,3,1])
with col_c:
    try:
        resp = requests.get(URL_LOGO_DIRECTA)
        logo_img = Image.open(io.BytesIO(resp.content))
        st.image(logo_img, use_container_width=True)
    except:
        st.title("TARJETA VIDA")

st.markdown("---")

# --- 6. MENÚ DE NAVEGACIÓN ---
choice = st.sidebar.selectbox("MENÚ PRINCIPAL", ["Registrar Paciente", "Consulta e Historial", "Base de Datos Completa"])

# --- SECCIÓN: REGISTRO ---
if choice == "Registrar Paciente":
    st.subheader("📝 Nuevo Registro Médico")
    with st.form("f_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        doc = c2.text_input("Número de Documento")
        edad = c1.text_input("Edad")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = c1.text_input("Entidad (EPS)")
        cel = c2.text_input("Teléfono")
        
        st.write("### 🚨 Emergencia")
        enom = c1.text_input("Nombre de contacto")
        etel = c2.text_input("Teléfono de contacto")
        
        if st.form_submit_button("REGISTRAR PACIENTE"):
            if nombre and doc:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": doc,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.1892763134": enom, "entry.2011749615": etel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("Paciente guardado correctamente.")
                st.cache_data.clear()
            else: st.error("Faltan datos obligatorios.")

# --- SECCIÓN: CONSULTA (CON HISTORIAL EXISTENTE) ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Consulta de Pacientes e Historial")
    id_busqueda = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_busqueda and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        paciente_encontrado = df_pacientes[df_pacientes["DOCUMENTO"] == id_busqueda]
        
        if not paciente_encontrado.empty:
            p = paciente_encontrado.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p><b>DOCUMENTO:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # MOSTRAR HISTORIAL QUE YA EXISTE
            st.write("### 📅 Evoluciones Registradas")
            if df_historial is not None:
                df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                # Filtramos el historial por el documento del paciente
                h_filtro = df_historial[df_historial["DOCUMENTO"] == id_busqueda]
                
                if not h_filtro.empty:
                    # Mostramos de la más reciente a la más antigua
                    st.dataframe(h_filtro.iloc[::-1], use_container_width=True)
                else:
                    st.info("Este paciente aún no tiene evoluciones registradas.")
            
            # FORMULARIO PARA AGREGAR NUEVA EVOLUCIÓN
            st.write("---")
            st.write("### ✍️ Nueva Evolución")
            with st.form("f_hist", clear_on_submit=True):
                tratamiento = st.text_input("Tratamiento")
                notas = st.text_area("Observaciones Médicas")
                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    payload_h = {"entry.2019369477": id_busqueda, "entry.611862537": tratamiento, "entry.2016051626": notas}
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.success("Evolución guardada.")
                    st.cache_data.clear()
                    st.rerun()
        else: st.error("El paciente no existe en la base de datos.")

# --- SECCIÓN: BASE DE DATOS ---
else:
    st.subheader("📊 Visualización de Datos")
    t1, t2 = st.tabs(["PACIENTES", "HISTORIAL COMPLETO"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
