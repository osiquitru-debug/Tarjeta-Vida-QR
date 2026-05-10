import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. ESTILOS (VERDE MEDICINAL, CELDAS BLANCAS) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    h1, h2, h3, p, span, label, div {{ color: #000000 !important; font-family: 'Arial', sans-serif; }}

    /* CARNET AZUL CIELO */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 12px;
        padding: 15px;
        max-width: 400px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    .label-sos {{
        background-color: #f43f5e; color: white !important; padding: 8px;
        border-radius: 6px; font-size: 12px; font-weight: bold; text-align: center; margin-top: 8px;
    }}
    
    /* TARJETAS DE EVOLUCIÓN */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 10px;
        border-left: 8px solid #4ade80; 
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .badge-dato {{ background: #f1f5f9; padding: 5px 10px; border-radius: 4px; font-size: 13px; border: 1px solid #e2e8f0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("Sin dato")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("Sin dato")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 3. MENÚ LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA Y CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abrilycompañia")

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=280)
    st.markdown("## *'Tu información médica vital, siempre contigo.'*")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("f_reg"):
        col1, col2 = st.columns(2)
        with col1:
            n = st.text_input("Nombre Completo"); td = st.selectbox("Tipo Doc", ["CC", "TI", "CE"]); doc = st.text_input("Documento")
        with col2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-"])
        en = st.text_input("Contacto Emergencia"); et = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR"):
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", 
                          data={"entry.346175428": n, "entry.1650757004": td, "entry.1302424820": doc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": en, "entry.2011749615": et})
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta")
    id_buscado = st.text_input("Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "Sin dato")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "Sin dato")
            
            # QR y Carnet
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            buf = io.BytesIO(); qr_gen.save(buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(buf.getvalue()).decode()

            st.markdown(f"""
            <div class="carnet-container">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <img src="{LOGO_URL}" width="60"> <b style="font-size:14px;">TARJETA VIDA QR</b>
                </div>
                <div style="display:flex; gap:10px;">
                    <div style="flex:2;">
                        <p style="margin:0; font-size:16px;"><b>{p.get('NOMBRE')}</b></p>
                        <p style="margin:2px 0; font-size:13px;">ID: {p.get('DOCUMENTO')}</p>
                        <p style="margin:2px 0; font-size:13px;">RH: {p.get('RH')} | EPS: {p.get('EPS')}</p>
                        <div class="label-sos">🚨 SOS: {nom_e}<br>{tel_e}</div>
                    </div>
                    <div style="flex:1; background:white; padding:5px; border-radius:8px; text-align:center; display:flex; align-items:center;">
                        <img src="data:image/png;base64,{qr_b64}" width="90">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (TAMAÑO TARJETA 85x55mm) ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page(); pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            tmp_q = f"q_{id_buscado}.png"; qr_gen.save(tmp_q, border=0)
            pdf_c.image(tmp_q, 58, 12, 22, 22)
            pdf_c.image(LOGO_URL, 5, 5, 12)
            pdf_c.set_font("Arial", 'B', 8); pdf_c.set_xy(5, 20); pdf_c.cell(0, 4, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            pdf_c.set_xy(5, 24); pdf_c.cell(0, 4, f"ID: {p.get('DOCUMENTO')} | RH: {p.get('RH')}")
            pdf_c.set_fill_color(244, 63, 94); pdf_c.rect(5, 35, 50, 12, 'F'); pdf_c.set_text_color(255,255,255)
            pdf_c.set_xy(5, 36); pdf_c.cell(50, 4, f"SOS: {nom_e[:18]}", 0, 1, 'C')
            pdf_c.set_xy(5, 40); pdf_c.cell(50, 4, f"TEL: {tel_e}", 0, 1, 'C')
            st.download_button("🪪 Descargar Carnet (85x55mm)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_q): os.remove(tmp_q)

            # --- REGISTRO EVOLUCIÓN ---
            st.divider()
            with st.expander("➕ REGISTRAR EVOLUCIÓN"):
                with st.form("f_ev"):
                    c1, c2 = st.columns(2)
                    with c1: mot=st.text_area("Motivo"); epi=st.text_area("Valoración / Epicrisis"); tal=st.text_input("Talla")
                    with c2: pes=st.text_input("Peso"); pre=st.text_input("T.A."); val=st.text_area("Observaciones")
                    if st.form_submit_button("GUARDAR"):
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                      data={"entry.2019369477":id_buscado, "entry.611862537":mot, "entry.1088523869":val, "entry.1275746503":tal, "entry.949747647":pes, "entry.2091389798":pre, "entry.616774918":epi})
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL PDF PROFESIONAL ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.subheader("📋 Evoluciones Médicas")
                
                pdf_h = FPDF(); pdf_h.add_page(); pdf_h.set_font("Arial", 'B', 16)
                pdf_h.cell(0, 10, "HISTORIA CLÍNICA - VIDA QR", 0, 1, 'C')
                pdf_h.set_font("Arial", 'B', 11); pdf_h.set_fill_color(230, 240, 255)
                pdf_h.cell(0, 8, f"PACIENTE: {p.get('NOMBRE')} | ID: {p.get('DOCUMENTO')}", 1, 1, 'L', True)
                pdf_h.set_font("Arial", '', 10)
                pdf_h.cell(0, 7, f"RH: {p.get('RH')} | EPS: {p.get('EPS')} | SOS: {nom_e} ({tel_e})", 1, 1, 'L')
                pdf_h.ln(5)

                for _, f in h_p.iterrows():
                    pdf_h.set_font("Arial", 'B', 10); pdf_h.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 'T', 1, 'L')
                    pdf_h.set_font("Arial", '', 9)
                    pdf_h.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACIÓN: {f.get('10. EPICRISIS')}\nSIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}")
                    pdf_h.ln(3)
                
                st.download_button("📄 Descargar Historial Completo", pdf_h.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")

                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <p style="margin:0;"><small>📅 {f.get('MARCA TEMPORAL')}</small></p>
                        <p style="margin:10px 0;"><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div style="display:flex; gap:10px; margin:10px 0;">
                            <span class="badge-dato">📏 {f.get('4. TALLA')}</span>
                            <span class="badge-dato">⚖️ {f.get('5. PESO')}</span>
                            <span class="badge-dato">🩸 TA: {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style="margin:5px 0;"><b>VALORACIÓN:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
