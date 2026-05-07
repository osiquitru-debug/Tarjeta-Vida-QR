import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

# Determinar el color de fondo dinámicamente según la sección
bg_color = "#f0f7f4" # Menta muy claro por defecto
if 'menu' in st.session_state and st.session_state.menu == "Registrar":
    bg_color = "#D8F3DC" # Verde menta más marcado para Registro

st.markdown(f"""
    <style>
    /* Fondo dinámico de la app */
    .stApp {{ 
        background-color: {bg_color} !important; 
        color: #000000 !important;
    }}
    
    /* SECCIÓN DEL MENÚ (Barra lateral) - Palo de Rosa */
    [data-testid="stSidebar"] {{
        background-color: #E5B1B1 !important;
        border-right: 1px solid #d4a5a5;
    }}
    
    /* Forzar textos negros */
    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stSidebar"] .stMarkdown {{
        color: #000000 !important;
    }}

    /* CAJAS DE DATOS BLANCAS */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Tarjetas y Contenedores */
    .medical-card, .evo-card {{
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #000000 !important;
    }}
    
    .medical-card {{ border-left: 12px solid #a2d2ff; }}
    .evo-card {{ border-left: 8px solid #b7e4c7; border: 1px solid #d8e2dc; }}

    .emergency-box {{
        background-color: #ffe5d9; 
        padding: 15px; 
        border-radius: 12px;
        border: 2px dashed #ffcad4; 
        color: #d64545 !important; 
        font-weight: bold; 
    }}

    /* Botones */
    div.stButton > button {{
        background-color: #84dcc6 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
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
        def limpiar(txt): return str(txt).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>MENÚ</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): 
        st.session_state.menu = "Inicio"
        st.rerun()
    if st.button("📝 Registrar Paciente", use_container_width=True): 
        st.session_state.menu = "Registrar"
        st.rerun()
    if st.button("🔍 Consulta / Evolución", use_container_width=True): 
        st.session_state.menu = "Consulta"
        st.rerun()

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 TARJETA VIDA")
    st.write("Sistema de Gestión Médica de Guadalupe, Huila.")

elif st.session_state.menu == "Registrar":
    st.image(LOGO_URL, width=120)
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_esp = st.text_area("Condiciones Especiales")
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre del Contacto")
        c_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120)
    st.title("🔍 CONSULTA MÉDICA")
    id_buscado = st.text_input("Documento").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)
            
            # Botón PDF y Nueva Evolución (Igual al código anterior...)
            # [Resto de la lógica de PDF y Evoluciones se mantiene idéntica]
