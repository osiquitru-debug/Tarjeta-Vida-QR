import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (ESTRUCTURA FIJA SOLICITADA) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

# Estilos CSS originales (Sin modificaciones)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f0f7f4 !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
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
        border-left: 8px solid #b7e4c7; margin-bottom: 12px;
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
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta"): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=220)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
        with c2:
            fnac = st.text_input("Fecha Nacimiento (DD/MM/AAAA)"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        aler = st.text_area("Alergias"); enfer = st.text_area("Enfermedades/Condiciones")
        enom = st.text_input("Contacto Emergencia"); etel = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": fnac, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel, "entry.alerg": aler, "entry.enf": enfer}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado.")

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # QR INDIVIDUAL
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p); qr_buf = io.BytesIO(); qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # --- GENERACIÓN DE CARNET (FIDELIDAD 100% A TU IMAGEN) ---
            pdf = FPDF(orientation='L', unit='mm', format=(85.6, 54))
            pdf.add_page(); pdf.set_auto_page_break(False); pdf.set_margins(0,0,0)
            
            pdf.set_fill_color(162, 210, 255); pdf.rect(0, 0, 85.6, 54, 'F') # Fondo azul
            pdf.set_fill_color(255, 255, 255); pdf.rect(56, 5, 25, 25, 'F') # Recuadro QR
            
            tmp_qr = f"q_{id_buscado}.png"; qr_gen.save(tmp_qr, border=1)
            pdf.image(tmp_qr, 57, 6, 23)

            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 8)
            # Fila 1: Nombre
            pdf.set_xy(5, 5); pdf.cell(50, 4, "NOMBRE:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 8); pdf.cell(50, 4, p.get('NOMBRE')[:35])
            # Fila 2: Fecha Nac
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 13); pdf.cell(50, 4, "FECHA DE NACIMIENTO:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 16); pdf.cell(50, 4, p.get('FECHA NACIMIENTO', '---'))
            # Fila 3: RH
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 21); pdf.cell(50, 4, "TIPO DE SANGRE:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 24); pdf.cell(50, 4, p.get('RH'))
            # Fila 4: Alergias
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 29); pdf.cell(50, 4, "ALERGIAS:"); pdf.set_font("Arial", '', 7); pdf.set_xy(5, 32); pdf.multi_cell(50, 3, p.get('ALERGIAS', 'Ninguna')[:60])

            # Banda SOS (Rojo)
            pdf.set_fill_color(200, 0, 0); pdf.rect(0, 41, 85.6, 13, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(0, 42); pdf.cell(85.6, 5, "CONTACTO DE EMERGENCIA", 0, 1, 'C')
            pdf.set_xy(0, 47); pdf.cell(85.6, 5, f"{p.get('NOMBRE CONTACTO', '---')} - {p.get('TELÉFONO CONTACTO', '---')}", 0, 1, 'C')

            st.download_button("🪪 Descargar Tarjeta Imprimible", pdf.output(), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_qr): os.remove(tmp_qr)
