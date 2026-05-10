import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    
    /* FLECHAS BLANCAS */
    [data-testid="stSidebarCollapseIcon"] svg, [data-testid="collapsedControl"] svg {{
        fill: #ffffff !important; color: #ffffff !important;
    }}

    /* DISEÑO CARNET DIGITAL */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 20px;
        padding: 25px;
        width: 100%;
        max-width: 450px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        font-family: 'Arial', sans-serif;
        color: #000000 !important;
    }}
    .carnet-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
    .carnet-body {{ display: flex; gap: 20px; }}
    .carnet-info {{ flex: 2; }}
    .carnet-qr {{ flex: 1; text-align: center; }}
    .carnet-info p {{ margin: 3px 0; font-size: 14px; line-height: 1.2; }}
    .label-emergencia {{
        background-color: #f43f5e; color: white !important; padding: 5px 10px;
        border-radius: 5px; font-size: 12px; display: inline-block; margin-top: 10px;
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

def get_qr_base64(url):
    qr = segno.make(url)
    buff = io.BytesIO()
    qr.save(buff, kind='png', scale=5)
    return base64.b64encode(buff.getvalue()).decode()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA Y CARNET")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip().replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            def obtener_dato(df_row, claves):
                for col in df_row.index:
                    if all(c in col for c in claves): return df_row[col]
                return "No registra"

            nom_e = obtener_dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_e = obtener_dato(p, ["TEL", "CONTACTO", "EMERGENCIA"])
            alert = obtener_dato(p, ["CONDICIONES", "ESPECIALES"])
            
            # Carnet Visual
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_b64 = get_qr_base64(url_p)

            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header">
                    <img src="{LOGO_URL}" width="80">
                    <b style="font-size: 16px;">TARJETA VIDA QR</b>
                </div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>PACIENTE:</b><br>{p.get('NOMBRE')}</p>
                        <p><b>ID:</b> {p.get('DOCUMENTO')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <div class="label-emergencia">📞 SOS: {nom_e}<br>{tel_e}</div>
                    </div>
                    <div class="carnet-qr">
                        <img src="data:image/png;base64,{qr_b64}" width="100">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            
            # --- GENERACIÓN DE PDF CORREGIDA ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page()
            pdf_c.set_fill_color(162, 210, 255)
            pdf_c.rect(0, 0, 85, 55, 'F')
            pdf_c.set_font("Arial", 'B', 10)
            pdf_c.text(5, 10, "TARJETA VIDA QR")
            pdf_c.set_font("Arial", '', 8)
            pdf_c.text(5, 20, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            pdf_c.text(5, 25, f"ID: {p.get('DOCUMENTO')}")
            pdf_c.text(5, 30, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            pdf_c.set_text_color(200, 0, 0)
            pdf_c.text(5, 40, f"SOS: {nom_e[:20]}")
            pdf_c.text(5, 45, f"TEL: {tel_e}")
            
            # Corrección del Error AttributeError
            qr_obj = segno.make(url_p)
            qr_img_buff = io.BytesIO()
            qr_obj.save(qr_img_buff, kind='png', border=0)
            qr_img_buff.seek(0) # Crucial: Volver al inicio
            pdf_c.image(qr_img_buff, x=55, y=10, w=25, h=25, type='PNG') # Especificar tipo

            st.download_button("📥 Descargar Carnet Digital", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")

            # --- HISTORIAL ---
            st.divider()
            st.subheader("📋 Evoluciones")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {f.get('MARCA TEMPORAL')}</small><p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p></div>""", unsafe_allow_html=True)

# (Secciones de Inicio y Registrar iguales al anterior)
elif st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.image(LOGO_URL, width=250)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    with st.form("f_reg"):
        nom = st.text_input("Nombre"); ndoc = st.text_input("Documento")
        if st.form_submit_button("GUARDAR"):
            st.success("Registrado."); st.cache_data.clear()
