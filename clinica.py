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

# --- 2. DISEÑO CSS DE ALTO CONTRASTE (PASTEL SEGURO) ---
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { 
        background-color: #f0fff4 !important; 
    }
    
    /* FORZAR TEXTO NEGRO EN TODA LA APP */
    html, body, [class*="st-"], p, label, h1, h2, h3, h4, span, div {
        color: #000000 !important;
        font-weight: 500;
    }

    /* Inputs y Áreas de texto: Fondo blanco y texto negro */
    input, textarea, [data-baseweb="select"], [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
        border-radius: 8px !important;
    }
    
    /* Arreglo para que el texto escrito sea visible */
    input[type="text"], textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Sidebar Lavanda con texto negro */
    [data-testid="stSidebar"] {
        background-color: #f3e8ff !important;
        border-right: 2px solid #d8b4fe;
    }
    
    /* Botones Laterales */
    .stSidebar button {
        width: 100%;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d8b4fe !important;
        font-weight: bold !important;
        margin-bottom: 10px;
    }

    /* Botón Guardar (Menta Fuerte) */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important;
        color: #000000 !important;
        border-radius: 12px;
        font-weight: 900 !important;
        border: 2px solid #285e61;
        height: 3.5em;
    }

    /* Tarjetas de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #b2f5ea;
        border-left: 15px solid #4fd1c5;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .emergency-box {
        background-color: #fff5f5;
        padding: 12px;
        border-radius: 10px;
        border: 2px dashed #feb2b2;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# URLs de los Forms con tus IDs verificados
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
    st.markdown(f"**📍 SECCIÓN:**  \n{st.session_state.menu}")

# --- 6. CABECERA ---
try:
    logo = Image.open(io.BytesIO(requests.get(URL_LOGO_DIRECTA).content))
    st.image(logo, width=300)
except: 
    st.title("🩺 Tarjeta Vida")

st.markdown("<h1 style='text-align: center; color: black;'>Gestión Médica</h1>", unsafe_allow_html=True)

# --- 7. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.subheader("📝 Nuevo Registro de Paciente")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        cedula = c2.text_input("Cédula / ID")
        edad = c1.text_input("Edad")
        rh = c2.selectbox("RH / Grupo Sanguíneo", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = c1.text_input("EPS / Aseguradora")
        cel = c2.text_input("Teléfono de Contacto")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ce1, ce2 = st.columns(2)
        e_nom = ce1.text_input("Nombre de contacto de emergencia")
        e_tel = ce2.text_input("Teléfono de contacto de emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE EN NUBE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": cedula,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ {nombre} registrado con éxito.")
                st.cache_data.clear()
            else: st.error("⚠️ Error: Nombre y Cédula son campos obligatorios.")

elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Consulta de Pacientes e Historial")
    id_bus = st.text_input("Ingrese Cédula del paciente para buscar").strip()
    
    if id_bus and df_p is not None:
        df_p["DOCUMENTO"] = df_p["DOCUMENTO"].astype(str).str.strip()
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0; color: black;'>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p style='font-size: 1.1em;'><b>ID:</b> {p.get('DOCUMENTO', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div class="emergency-box">
                    <p style='margin:0; color:#c53030; font-size: 1.2em;'><b>🚨 EMERGENCIA:</b></p>
                    <p style='margin:0; font-size: 1.1em;'>{p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'No registrado')}</p>
                    <p style='margin:0; font-size: 1.1em;'><b>TEL:</b> {p.get('TELEFONO DE CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### 📅 Antecedentes Clínicos")
            if df_h is not None:
                df_h["DOCUMENTO"] = df_h["DOCUMENTO"].astype(str).str.strip()
                hist_p = df_h[df_h["DOCUMENTO"] == id_bus]
                if not hist_p.empty:
                    cols = [c for c in ["FECHA", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"] if c in hist_p.columns]
                    st.dataframe(hist_p[cols].iloc[::-1], use_container_width=True, hide_index=True)
                else: st.info("No se encontraron registros de atención anteriores.")

            st.markdown("---")
            st.subheader("✍️ Registrar Evolución en Consulta")
            with st.form("h_form", clear_on_submit=True):
                trat = st.text_input("Tratamiento Recomendado")
                meds = st.text_area("Medicamentos Recetados")
                proc = st.text_area("Procedimientos Realizados")
                
                if st.form_submit_button("GUARDAR ATENCIÓN MÉDICA"):
                    payload_h = {
                        "entry.2019369477": id_bus, "entry.611862537": trat, 
                        "entry.2016051626": meds, "entry.1088523869": proc
                    }
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).status_code == 200:
                        st.success("✅ Historial clínico actualizado.")
                        st.cache_data.clear()
                        st.rerun()
        else: st.error("❌ El paciente con esa cédula no existe en la base de datos.")

else:
    st.subheader("📊 Registros Globales")
    t1, t2 = st.tabs(["Pacientes", "Historial Completo"])
    if df_p is not None: t1.write("### Lista de Pacientes"), t1.dataframe(df_p)
    if df_h is not None: t2.write("### Todo el Historial"), t2.dataframe(df_h)
