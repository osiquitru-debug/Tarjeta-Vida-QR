import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA Y DISEÑO (TU CONFIGURACIÓN FAVORITA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .logo-container { display: flex; justify-content: center; margin: 20px 0; }
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y LINKS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"
URL_APP_REAL = "https://tarjeta-vida-qr-abrilycompania.streamlit.app/"

def normalizar(t):
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        
        # PROCESAMIENTO INTELIGENTE DE COLUMNAS
        for df in [p, h]:
            # Buscamos la columna que contenga "DOC" sin importar tildes o espacios
            col_encontrada = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if col_encontrada:
                df.rename(columns={col_encontrada: "DOCUMENTO_LIMPIO"}, inplace=True)
                df["DOCUMENTO_LIMPIO"] = df["DOCUMENTO_LIMPIO"].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. LÓGICA DE NAVEGACIÓN Y QR ---
id_via_url = st.query_params.get("id", "")
if 'menu' not in st.session_state:
    st.session_state.menu = "Consulta" if id_via_url else "Registrar"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="120"></div>', unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

# --- 5. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Pacientes</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["Cédula", "T.I.", "C.E.", "Pasaporte"])
            doc = st.text_input("Documento")
        with c2:
            cel = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre de contacto")
        e_tel = st.text_input("Teléfono de contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nom and doc:
                payload_p = {
                    "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": doc.strip(), 
                    "entry.1043165037": cel, "entry.1172011247": eps, "entry.162368130": rh,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload_p)
                st.success("✅ Paciente guardado.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente", value=id_via_url).strip()
    
    if busq and df_p is not None:
        # Usamos el nombre de columna "normalizado" que creamos en la carga
        pac = df_p[df_p["DOCUMENTO_LIMPIO"] == busq] if "DOCUMENTO_LIMPIO" in df_p.columns else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            h_p = df_h[df_h["DOCUMENTO_LIMPIO"] == busq] if (df_h is not None and "DOCUMENTO_LIMPIO" in df_h.columns) else pd.DataFrame()
            
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="margin:0; color:#c53030;"><b>🚨 EMERGENCIA:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'N/R')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'N/R')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            link_qr = f"{URL_APP_REAL}?id={busq}"
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={link_qr}", caption="Acceso rápido para este paciente")

            with st.expander("✍️ AGREGAR EVOLUCIÓN"):
                with st.form("h_form", clear_on_submit=True):
                    motivo = st.text_input("Motivo de la Consulta")
                    val = st.text_input("Valoración")
                    c1, c2, c3 = st.columns(3)
                    talla, peso, pa = c1.text_input("Talla (cm)"), c2.text_input("Peso (kg)"), c3.text_input("Presión Arterial")
                    meds, epi = st.text_area("Medicamentos")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        payload_h = {
                            "entry.2019369477": busq, "entry.611862537": motivo, "entry.1275746503": val,
                            "entry.949747647": talla, "entry.2091389798": peso, "entry.882053172": pa,
                            "entry.2016051626": meds
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Datos enviados.")
                        st.cache_data.clear()
                        st.rerun()

            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                    <p><b>🔍 MOTIVO:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                    <p><b>📝 VALORACIÓN:</b> {f.get('VALORACION', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Datos Registrados")
    st.write(df_p)
