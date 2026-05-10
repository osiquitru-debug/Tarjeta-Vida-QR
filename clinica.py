import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (MANTENIENDO TU ESTILO) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    h1, h2, h3, p, span, label, li, div {{ color: #000000 !important; }}
    
    /* Inputs Blancos */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* Botones Verde Menta */
    div.stButton > button {{
        background-color: #98FF98 !important; 
        color: #000000 !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
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

# --- 3. LOGICA DE PARAMETROS URL (PARA QUE EL QR FUNCIONE) ---
# Si entran por el QR, forzamos que el menú sea "Consulta"
query_params = st.query_params
if "id" in query_params:
    st.session_state.menu = "Consulta"

# --- 4. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=220)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<p style="text-align: center;">© 2026 Abri_Garcia_Sierra</p>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg"):
        c1, c2 = st.columns(2)
        with c1: nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE"]); ndoc = st.text_input("Documento")
        with c2: ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        st.subheader("🚨 Emergencia")
        enom = st.text_input("Nombre de Contacto"); etel = st.text_input("Teléfono de Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    # Capturar el ID del parámetro de la URL automáticamente
    id_url = query_params.get("id", "")
    id_buscado = st.text_input("Ingrese Documento", value=id_url).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- QR FUNCIONAL ---
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr = segno.make(url_p)
            qr_buf = io.BytesIO()
            qr.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # Mapeo de contacto (Asegúrate que coincidan con los encabezados de tu Sheet)
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
                        <img src="data:image/png;base64,{qr_b64}" width="120" style="border: 1px solid #eee; border-radius:10px;">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (ID-1) ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85.6, 54))
            pdf_c.add_page(); pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85.6, 54, 'F')
            qr_tmp = f"t_{id_buscado}.png"; qr.save(qr_tmp)
            pdf_c.image(qr_tmp, 58, 10, 22, 22)
            pdf_c.set_font("Arial", 'B', 10); pdf_c.set_xy(5, 12); pdf_c.cell(0, 5, p.get('NOMBRE')[:25])
            pdf_c.set_font("Arial", '', 8); pdf_c.set_xy(5, 18); pdf_c.cell(0, 5, f"ID: {p.get('DOCUMENTO')}")
            pdf_c.set_xy(5, 23); pdf_c.cell(0, 5, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            pdf_c.set_fill_color(244, 63, 94); pdf_c.rect(5, 34, 50, 12, 'F')
            pdf_c.set_text_color(255,255,255); pdf_c.set_font("Arial", 'B', 7)
            pdf_c.set_xy(5, 35); pdf_c.cell(50, 5, f"SOS: {c_nom}", 0, 1, 'C')
            pdf_c.set_xy(5, 39); pdf_c.cell(50, 5, f"TEL: {c_tel}", 0, 1, 'C')
            st.download_button("🪪 Descargar Carnet (Para Impresión)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(qr_tmp): os.remove(qr_tmp)

            # --- HISTORIAL ---
            st.divider()
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <p style='border-top:1px solid #eee; padding-top:5px;'><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
