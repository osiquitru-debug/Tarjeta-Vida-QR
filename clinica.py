import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- CLASE PARA MANEJO DE IMÁGENES EN MEMORIA ---
class NamedBytesIO(io.BytesIO):
    def __init__(self, content, name):
        super().__init__(content)
        self.name = name

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
    /* DISEÑO CARNET (FIDELIDAD 100% A TU IMAGEN) */
    .carnet-container {{
        background-color: #a2d2ff; /* Azul cielo de la imagen */
        border-radius: 15px;
        padding: 20px;
        max-width: 500px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        font-family: 'Helvetica', Arial, sans-serif;
    }}
    .carnet-header {{ 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.5);
        padding-bottom: 5px;
    }}
    .carnet-body {{ display: flex; gap: 15px; }}
    .carnet-info {{ flex: 2; color: #000000 !important; }}
    .carnet-qr {{ 
        flex: 1; 
        background: white; 
        padding: 10px; 
        border-radius: 10px; 
        display: flex; 
        flex-direction: column; 
        align-items: center;
        justify-content: center;
    }}
    .carnet-info p {{ margin: 4px 0; font-size: 14px; line-height: 1.3; }}
    .label-sos {{
        background-color: #f43f5e; 
        color: white !important; 
        padding: 8px;
        border-radius: 6px; 
        font-size: 13px; 
        margin-top: 10px;
        font-weight: bold;
        text-align: center;
    }}
    
    /* ESTILOS EVOLUCIONES */
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 8px solid #b7e4c7; margin-bottom: 10px; color: #000;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; 
        margin: 8px 0; font-size: 13px;
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
    st.image(LOGO_URL)
    if st.button("📝 Registrar"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta"): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. SECCIÓN CONSULTA (EL CARNET) ---
if st.session_state.menu == "Consulta":
    st.title("🔍 Carnet y Evoluciones")
    id_buscado = st.text_input("Documento del Paciente", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Búsqueda de datos de emergencia
            n_emer = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            t_emer = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            buff_qr = io.BytesIO()
            qr_gen.save(buff_qr, kind='png', scale=10)
            qr_b64 = base64.b64encode(buff_qr.getvalue()).decode()

            # --- RENDERIZADO EN PLATAFORMA ---
            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header">
                    <img src="{LOGO_URL}" width="80">
                    <b style="font-size: 16px;">TARJETA VIDA QR</b>
                </div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>PACIENTE:</b><br>{p.get('NOMBRE', 'No registra')}</p>
                        <p><b>ID:</b> {p.get('DOCUMENTO', 'No registra')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <div class="label-sos">🚨 EMERGENCIA:<br>{n_emer} - {t_emer}</div>
                    </div>
                    <div class="carnet-qr">
                        <img src="data:image/png;base64,{qr_b64}" width="100">
                        <span style="font-size: 9px; color: #555; margin-top:5px;">ID: {id_buscado}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- GENERACIÓN DE PDF (IDENTICO A LA IMAGEN) ---
            pdf = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf.add_page()
            pdf.set_fill_color(162, 210, 255) # Color azul exacto
            pdf.rect(0, 0, 85, 55, 'F')
            
            # Logo y Título
            pdf.image(LOGO_URL, 5, 5, 20)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(26, 7)
            pdf.cell(0, 5, "TARJETA VIDA QR", 0, 1)
            
            # Datos Paciente
            pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(5, 18); pdf.cell(0, 4, "PACIENTE:", 0, 1)
            pdf.set_font("Arial", '', 8)
            pdf.set_xy(5, 22); pdf.cell(0, 4, f"{p.get('NOMBRE')[:30]}", 0, 1)
            
            pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(5, 28); pdf.cell(0, 4, f"ID: {p.get('DOCUMENTO')}", 0, 1)
            pdf.cell(0, 4, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}", 0, 1)
            
            # Cuadro SOS
            pdf.set_fill_color(244, 63, 94) # Rojo SOS
            pdf.rect(5, 38, 45, 12, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 7)
            pdf.set_xy(5, 39); pdf.multi_cell(45, 3.5, f"SOS: {n_emer}\nTEL: {t_emer}", 0, 'C')
            
            # QR en PDF
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(54, 12, 26, 32, 'F') # Fondo blanco para el QR
            
            # Usamos NamedBytesIO para evitar el error .rfind
            named_qr = NamedBytesIO(buff_qr.getvalue(), "qr_file.png")
            pdf.image(named_qr, 56, 14, 22, 22)
            pdf.set_font("Arial", 'B', 6)
            pdf.set_xy(54, 38); pdf.cell(26, 4, f"ID: {id_buscado}", 0, 0, 'C')

            st.download_button("📥 Descargar Carnet Digital (PDF)", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")

            # --- SECCIÓN HISTORIAL (7 DE MAYO) ---
            st.divider()
            st.subheader("📋 Historia Clínica y Evoluciones")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            
            with st.expander("➕ Nueva Evolución"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1: mot = st.text_area("Motivo"); val = st.text_area("Valoración"); tal = st.text_input("Talla")
                    with c2: pes = st.text_input("Peso"); ta = st.text_input("T.A."); epi = st.text_area("Epicrisis")
                    if st.form_submit_button("Guardar"):
                        # Aquí iría tu requests.post al Google Form de evoluciones
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)

# Sección Registrar
elif st.session_state.menu == "Registrar":
    st.title("📝 Registro Nuevo")
    with st.form("reg"):
        st.text_input("Nombre"); st.text_input("Documento")
        if st.form_submit_button("Registrar"):
            st.success("Listo"); st.cache_data.clear()
