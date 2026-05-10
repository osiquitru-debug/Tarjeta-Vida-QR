import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (TU CÓDIGO ORIGINAL SIN CAMBIOS) ---
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
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

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
        enom = st.text_input("Contacto Emergencia"); etel = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- QR FUNCIONAL ---
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            qr_buf = io.BytesIO()
            qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # Mapeo de datos para contacto
            c_nom = p.get('NOMBRE DE LA PERSONA DE CONTACTO', p.get('NOMBRE CONTACTO', 'No registra'))
            c_tel = p.get('TELÉFONO DE EMERGENCIA', p.get('TELÉFONO CONTACTO', 'No registra'))

            st.markdown(f"""
            <div class="medical-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:2;">
                        <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                        <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')}</p>
                        <p><b>EPS:</b> {p.get('EPS')}</p>
                        <div class="emergency-box">🚨 EMERGENCIA: {c_nom}<br>📞 Tel: {c_tel}</div>
                    </div>
                    <div style="flex:1; text-align:right;">
                        <img src="data:image/png;base64,{qr_b64}" width="130" style="border-radius:10px;">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- GENERACIÓN DE PDF CARNET 100% FIEL A LA IMAGEN ---
            pdf = FPDF(orientation='P', unit='mm', format='Letter')
            pdf.add_page()
            pdf.set_auto_page_break(False)

            # Medidas estándar ID-1 (85.6 x 54 mm)
            w, h = 85.6, 54
            x, y = (215.9 - w) / 2, 30  # Centrado en hoja carta

            # 1. Fondo Azul Cielo de la Tarjeta
            pdf.set_fill_color(162, 210, 255)
            pdf.rect(x, y, w, h, 'F')

            # 2. Recuadro Blanco para QR (Derecha)
            qr_box_size = 26
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(x + w - qr_box_size - 4, y + 6, qr_box_size, qr_box_size, 'F')
            
            # Insertar QR
            tmp_qr = f"tmp_{id_buscado}.png"; qr_gen.save(tmp_qr, border=1)
            pdf.image(tmp_qr, x + w - qr_box_size - 3, y + 7, qr_box_size - 2)

            # 3. Logo y Textos Superiores
            try: pdf.image(LOGO_URL, x + 4, y + 4, 10)
            except: pass
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(x + 16, y + 6); pdf.cell(40, 5, "VIDA QR")

            # 4. Datos del Paciente (Izquierda)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_xy(x + 5, y + 16); pdf.cell(50, 6, p.get('NOMBRE')[:24])
            
            pdf.set_font("Arial", '', 8)
            pdf.set_xy(x + 5, y + 22); pdf.cell(50, 4, f"ID: {p.get('DOCUMENTO')}")
            pdf.set_xy(x + 5, y + 26); pdf.cell(50, 4, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")

            # 5. Banda Roja de Emergencia (SOS) - Abajo full ancho
            sos_h = 14
            pdf.set_fill_color(200, 0, 0) # Rojo fuerte
            pdf.rect(x, y + h - sos_h, w, sos_h, 'F')
            
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(x, y + h - sos_h + 2)
            pdf.cell(w, 5, f"CONTACTO EMERGENCIA: {c_nom[:25]}", 0, 1, 'C')
            pdf.set_xy(x, y + h - sos_h + 7)
            pdf.cell(w, 5, f"TEL: {c_tel}", 0, 1, 'C')

            # 6. Copyright debajo del carnet
            pdf.set_text_color(80, 80, 80); pdf.set_font("Arial", '', 6)
            pdf.set_xy(x, y + h + 2)
            pdf.cell(w, 4, "© 2026 Vida QR - Abrilycompañia", 0, 0, 'C')

            st.download_button("🪪 Descargar Carnet Fiel (PDF)", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_qr): os.remove(tmp_qr)
