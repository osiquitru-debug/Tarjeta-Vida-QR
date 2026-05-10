import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN Y CSS BLINDADO ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    /* Fondo General */
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
    /* FORZAR CELDAS DE ESCRITURA BLANCAS CON TEXTO NEGRO */
    input, textarea, [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    /* Estilo de las etiquetas de los campos */
    label, p, span, h1, h2, h3 {{ color: #000000 !important; }}

    /* TARJETAS DE EVOLUCIÓN (BLANCO PURO) */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 10px;
        border: 1px solid #000000;
        margin-bottom: 15px;
    }}

    /* CARNET AZUL CIELO PROFESIONAL */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 12px;
        padding: 15px;
        width: 350px;
        margin: auto;
        border: 1px solid #ffffff;
    }}
    .label-sos {{
        background-color: #f43f5e; color: white !important; 
        padding: 5px; border-radius: 5px; text-align: center; font-weight: bold;
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
    if st.button("🏠 INICIO"): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA / CARNET"): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abri_Garcia_Sierra")

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=250)

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro")
    with st.form("reg_form"):
        st.subheader("Datos Personales")
        c1, c2 = st.columns(2)
        with c1: nom = st.text_input("Nombre"); doc = st.text_input("Documento")
        with c2: eps = st.text_input("EPS"); rh = st.text_input("RH")
        st.subheader("Emergencia")
        e_nom = st.text_input("Contacto"); e_tel = st.text_input("Teléfono")
        if st.form_submit_button("GUARDAR"):
            # Aquí va el post a tu Google Form
            st.success("Registrado.")

elif st.session_state.menu == "Consulta":
    # Lógica de QR funcional: Lee el parámetro 'id' de la URL
    params = st.query_params
    id_actual = params.get("id", "")
    id_buscado = st.text_input("Buscar Documento", value=id_actual).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Link funcional que el QR usará
            url_seguimiento = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr = segno.make(url_seguimiento)
            
            # Carnet en Pantalla
            st.markdown(f"""
            <div class="carnet-container">
                <div style="display:flex; justify-content:space-between;">
                    <img src="{LOGO_URL}" width="50">
                    <b>TARJETA VIDA QR</b>
                </div>
                <p><b>{p.get('NOMBRE')}</b><br>ID: {p.get('DOCUMENTO')}<br>RH: {p.get('RH')}</p>
                <div class="label-sos">SOS: {p.get('NOMBRE EMERGENCIA')}<br>{p.get('TEL EMERGENCIA')}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- PDF CARNET (TAMAÑO TARJETA DE CRÉDITO EXACTO: 85.6 x 53.98 mm) ---
            pdf = FPDF(orientation='L', unit='mm', format=(85.6, 53.98))
            pdf.add_page()
            pdf.set_fill_color(162, 210, 255) # Azul cielo
            pdf.rect(0, 0, 85.6, 53.98, 'F')
            
            # QR
            qr_temp = f"qr_{id_buscado}.png"
            qr.save(qr_temp, border=0)
            pdf.image(qr_temp, 58, 10, 22, 22)
            
            # Textos carnet
            pdf.set_font("Arial", 'B', 10); pdf_c_color = (0,0,0)
            pdf.set_xy(5, 15); pdf.cell(0, 5, f"{p.get('NOMBRE')[:20]}")
            pdf.set_font("Arial", '', 8)
            pdf.set_xy(5, 20); pdf.cell(0, 5, f"ID: {p.get('DOCUMENTO')}")
            pdf.set_xy(5, 25); pdf.cell(0, 5, f"EPS: {p.get('EPS')} | RH: {p.get('RH')}")
            
            # Zona SOS roja
            pdf.set_fill_color(244, 63, 94); pdf.rect(5, 35, 50, 12, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 7)
            pdf.set_xy(5, 36); pdf.cell(50, 5, f"SOS: {p.get('NOMBRE EMERGENCIA')}", 0, 1, 'C')
            pdf.set_xy(5, 40); pdf.cell(50, 5, f"TEL: {p.get('TEL EMERGENCIA')}", 0, 1, 'C')
            
            st.download_button("🪪 Descargar Carnet Físico", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(qr_temp): os.remove(qr_temp)

            # --- EVOLUCIONES ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            st.subheader("Historial Médico")
            for _, f in h_p.iterrows():
                st.markdown(f"""
                <div class="evo-card">
                    <p><b>Fecha:</b> {f.get('MARCA TEMPORAL')}</p>
                    <p><b>Valoración (Epicrisis):</b> {f.get('10. EPICRISIS')}</p>
                    <p><small>Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')}</small></p>
                </div>
                """, unsafe_allow_html=True)
