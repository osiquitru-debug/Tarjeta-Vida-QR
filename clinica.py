import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (TU CÓDIGO ORIGINAL - SIN CAMBIOS) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    input, textarea, [data-baseweb="select"] > div {{ background-color: #ffffff !important; color: #000000 !important; }}
    h1, h2, h3, p, span, label, li, div {{ color: #000000 !important; }}
    div.stButton > button {{
        background-color: #98FF98 !important; color: #000000 !important; 
        border-radius: 10px !important; font-weight: bold !important; 
    }}
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 2px dashed #f43f5e; color: #b91c1c !important; font-weight: bold; margin-top: 10px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
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

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", key="nav_inicio"): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", key="nav_reg"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", key="nav_cons"): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=220)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<p style="text-align: center; color: #555;">© 2026 Vida QR - Abrilycompañia</p>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- QR ÚNICO POR PACIENTE ---
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            qr_buf = io.BytesIO(); qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # --- VISTA PANTALLA ---
            st.markdown(f"""<div class="medical-card">
                <div style="display:flex; justify-content:space-between;">
                    <div><h2>👤 {p.get('NOMBRE')}</h2><p>ID: {p.get('DOCUMENTO')}</p></div>
                    <img src="data:image/png;base64,{qr_b64}" width="100">
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (REPLICA 100% FIEL A IMAGEN ADJUNTA) ---
            pdf = FPDF(orientation='L', unit='mm', format=(85.6, 54))
            pdf.add_page(); pdf.set_auto_page_break(False); pdf.set_margins(0,0,0)

            # Fondo Azul Cielo y QR Blanco
            pdf.set_fill_color(162, 210, 255); pdf.rect(0, 0, 85.6, 54, 'F')
            pdf.set_fill_color(255, 255, 255); pdf.rect(58, 8, 22, 22, 'F')
            
            tmp_qr = f"q_{id_buscado}.png"; qr_gen.save(tmp_qr, border=1)
            pdf.image(tmp_qr, 59, 9, 20)

            # Datos según la imagen (Tabla alineada a la izquierda)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(5, 5); pdf.cell(0, 5, "NOMBRE:")
            pdf.set_font("Arial", '', 8); pdf.set_xy(5, 8); pdf.cell(0, 5, p.get('NOMBRE'))

            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 14); pdf.cell(0, 5, "FECHA DE NACIMIENTO:")
            pdf.set_font("Arial", '', 8); pdf.set_xy(5, 17); pdf.cell(0, 5, p.get('EDAD')) # O campo fecha

            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 23); pdf.cell(0, 5, "TIPO DE SANGRE:")
            pdf.set_font("Arial", '', 8); pdf.set_xy(5, 26); pdf.cell(0, 5, p.get('RH'))

            # Franja Roja SOS Abajo
            pdf.set_fill_color(200, 0, 0); pdf.rect(0, 40, 85.6, 14, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(0, 42); pdf.cell(85.6, 5, "CONTACTO DE EMERGENCIA", 0, 1, 'C')
            pdf.set_xy(0, 47); pdf.cell(85.6, 5, "VER EN QR", 0, 1, 'C')

            st.download_button("📥 Descargar Tarjeta Imprimible", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_qr): os.remove(tmp_qr)
