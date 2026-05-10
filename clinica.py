import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. ESTILOS Y BLINDAJE VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
    /* FORZAR CELDAS BLANCAS CON LETRA NEGRA EN TODO EL SISTEMA */
    input, textarea, [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }}
    label, p, span, h1, h2, h3, b {{ color: #000000 !important; }}

    /* TARJETAS DE HISTORIAL (BLANCO PURO) */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 25px; 
        border-radius: 12px;
        border: 1px solid #dddddd;
        border-left: 10px solid #2d6a4f; 
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    /* DISEÑO CARNET AZUL CIELO EN PANTALLA */
    .carnet-box {{
        background-color: #a2d2ff;
        border-radius: 15px;
        padding: 20px;
        max-width: 420px;
        margin: auto;
        border: 2px solid #ffffff;
    }}
    .sos-rojo {{
        background-color: #f43f5e; color: white !important; 
        padding: 10px; border-radius: 8px; font-weight: bold; text-align: center; margin-top: 10px;
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

# --- 3. MENÚ ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("---")
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRO", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA / CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abri_Garcia_Sierra")

# --- 4. VISTA CONSULTA Y CARNET (LA CRÍTICA) ---
if st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Carnetización")
    id_buscado = st.text_input("Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- LÓGICA QR Y CARNET ---
            url_seguimiento = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_seguimiento)
            qr_buf = io.BytesIO()
            qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            st.markdown(f"""
            <div class="carnet-box">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <img src="{LOGO_URL}" width="60"><b>TARJETA VIDA QR</b>
                </div>
                <div style="display:flex; gap:15px;">
                    <div style="flex:2;">
                        <p style="font-size:18px; margin:0;"><b>{p.get('NOMBRE')}</b></p>
                        <p style="margin:5px 0;">ID: {p.get('DOCUMENTO')}</p>
                        <p style="margin:5px 0;">RH: {p.get('RH')} | EPS: {p.get('EPS')}</p>
                        <div class="sos-rojo">🚨 SOS: {p.get('NOMBRE EMERGENCIA')}<br>{p.get('TEL EMERGENCIA')}</div>
                    </div>
                    <div style="flex:1; background:white; padding:8px; border-radius:10px; text-align:center;">
                        <img src="data:image/png;base64,{qr_b64}" width="100">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (TAMAÑO TARJETA ID-1) ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page(); pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            
            tmp_q = f"q_{id_buscado}.png"; qr_gen.save(tmp_q, border=0)
            pdf_c.image(tmp_q, 58, 12, 22, 22)
            pdf_c.set_font("Arial", 'B', 10); pdf_c.set_xy(5, 15); pdf_c.cell(0, 5, f"{p.get('NOMBRE')[:25]}")
            pdf_c.set_font("Arial", '', 8); pdf_c.set_xy(5, 20); pdf_c.cell(0, 5, f"ID: {p.get('DOCUMENTO')}")
            pdf_c.set_xy(5, 25); pdf_c.cell(0, 5, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            
            pdf_c.set_fill_color(244, 63, 94); pdf_c.rect(5, 36, 50, 12, 'F'); pdf_c.set_text_color(255,255,255)
            pdf_c.set_xy(5, 37); pdf_c.cell(50, 4, f"SOS: {p.get('NOMBRE EMERGENCIA')}", 0, 1, 'C')
            pdf_c.set_xy(5, 41); pdf_c.cell(50, 4, f"TEL: {p.get('TEL EMERGENCIA')}", 0, 1, 'C')
            
            st.download_button("🪪 Descargar Carnet (Para Imprimir)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_q): os.remove(tmp_q)

            # --- HISTORIAL Y BOTÓN PDF ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.divider()
                st.subheader("📋 Historial de Evoluciones")
                
                # PDF DEL HISTORIAL
                pdf_h = FPDF(); pdf_h.add_page(); pdf_h.set_font("Arial", 'B', 14)
                pdf_h.cell(0, 10, f"HISTORIAL MÉDICO: {p.get('NOMBRE')}", 0, 1, 'C')
                pdf_h.ln(5)
                
                for _, f in h_p.iterrows():
                    # Tarjeta Visual (Blanca con Letra Negra)
                    st.markdown(f"""
                    <div class="evo-card">
                        <p><small>📅 FECHA: {f.get('MARCA TEMPORAL')}</small></p>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>🩺 VALORACIÓN (EPICRISIS):</b> {f.get('10. EPICRISIS')}</p>
                        <p><b>📏 SIGNOS:</b> Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}</p>
                    </div>""", unsafe_allow_html=True)

                    # Añadir al PDF
                    pdf_h.set_font("Arial", 'B', 10); pdf_h.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 'T', 1, 'L')
                    pdf_h.set_font("Arial", '', 9); pdf_h.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACIÓN: {f.get('10. EPICRISIS')}")
                    pdf_h.ln(2)
                
                st.download_button("📄 Descargar Historial Completo", pdf_h.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1: nom = st.text_input("Nombre Completo"); doc = st.text_input("Documento")
        with c2: eps = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-"])
        st.subheader("Contacto de Emergencia")
        e_nom = st.text_input("Nombre de contacto"); e_tel = st.text_input("Teléfono")
        if st.form_submit_button("GUARDAR"):
            st.success("Guardado en el sistema."); st.cache_data.clear()

elif st.session_state.menu == "Inicio":
    st.title("🩺 Bienvenido a Vida QR")
    st.image(LOGO_URL, width=300)
