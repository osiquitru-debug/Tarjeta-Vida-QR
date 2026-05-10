import streamlit as st
import pandas as pd
import requests
import segno
import io
import base64

# --- 1. CONFIGURACIÓN Y ESTÉTICA RESTAURADA (7 DE MAYO) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    /* Fondo verde medicinal original */
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
    /* CELDAS BLANCAS CON TEXTO NEGRO (Blindado) */
    input, textarea, [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }}
    
    /* Tipografía y colores de texto */
    h1, h2, h3, p, span, label, b {{ 
        color: #000000 !important; 
        font-family: 'Arial', sans-serif; 
    }}

    /* BOTONES CLAROS */
    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #adb5bd !important;
    }}

    /* TARJETAS DE HISTORIAL BLANCAS */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px;
        border-left: 10px solid #2d6a4f; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 3. MENÚ LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("---")
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA Y CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abri_Garcia_Sierra")

# --- 4. VISTA INICIO ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=280)
    st.markdown("### *Tu información médica vital, siempre contigo.*")

# --- 5. VISTA REGISTRAR (CONTACTO SEPARADO) ---
elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("form_registro"):
        st.subheader("Datos del Paciente")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE"])
            documento = st.text_input("Número de Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        st.markdown("---")
        st.subheader("🚨 Contacto de Emergencia")
        e_nombre = st.text_input("Nombre de la persona de contacto")
        e_tel = st.text_input("Teléfono de emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            # Payload para tu Google Form
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, 
                "entry.1302424820": documento, "entry.1801154005": edad, 
                "entry.1172011247": eps, "entry.162368130": rh, 
                "entry.1892763134": e_nombre, "entry.2011749615": e_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado con éxito."); st.cache_data.clear()

# --- 6. VISTA CONSULTA (BASE) ---
elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta de Historial")
    id_buscado = st.text_input("Ingrese Documento del Paciente").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.success(f"Paciente encontrado: {p.get('NOMBRE')}")
            
            # Aquí seguiremos con el QR y el carnet una vez confirmes que la estética volvió a ser la correcta.
        else:
            st.error("Paciente no encontrado.")
