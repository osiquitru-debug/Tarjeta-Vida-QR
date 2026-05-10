import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    h1, h2, h3, p, span, label, div {{ color: #000000 !important; font-family: 'Arial', sans-serif; }}

    /* ESTILO CARNET AZUL CIELO */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 15px;
        padding: 20px;
        max-width: 450px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }}
    .label-sos-rojo {{
        background-color: #f43f5e; color: white !important; padding: 10px;
        border-radius: 8px; font-size: 13px; font-weight: bold; text-align: center; margin-top: 10px;
    }}
    
    /* TARJETAS DE EVOLUCIÓN (BLANCAS Y COMPLETAS) */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px;
        border-left: 10px solid #b7e4c7; 
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .dato-box {{ background: #f8f9fa; padding: 8px; border-radius: 5px; border: 1px solid #eee; text-align: center; }}
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
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA Y CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abrilycompañia")

# --- 4. VISTA INICIO ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=280)
    st.markdown("## *'Tu información médica vital, siempre contigo.'*")

# --- 5. VISTA REGISTRAR (ESTRUCTURA ORIGINAL) ---
elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Nuevo Paciente")
    with st.form("form_registro"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            documento = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("Factor RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        st.subheader("🚨 Contacto de Emergencia")
        e_nombre = st.text_input("Nombre del Contacto")
        e_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": documento, "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh, "entry.1892763134": e_nombre, "entry.2011749615": e_tel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado correctamente."); st.cache_data.clear()

# --- 6. VISTA CONSULTA Y CARNET ---
elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta de Paciente")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            # QR y Visualización
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_s = segno.make(url_p)
            buf = io.BytesIO(); qr_s.save(buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(buf.getvalue()).decode()

            st.markdown(f"""
            <div class="carnet-container">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <img src="{LOGO_URL}" width="75"><b>TARJETA VIDA QR</b>
                </div>
                <div style="display:flex; gap:15px;">
                    <div style="flex:2;">
                        <p style="font-size:18px; margin:0;"><b>{p.get('NOMBRE')}</b></p>
                        <p style="margin:5px 0;">ID: {p.get('DOCUMENTO')}</p>
                        <p style="margin:5px 0;">RH: {p.get('RH')} | EPS: {p.get('EPS')}</p>
                        <div class="label-sos-rojo">🚨 SOS: {nom_e}<br>{tel_e}</div>
                    </div>
                    <div style="flex:1; background:white; padding:10px; border-radius:10px; text-align:center;">
                        <img src="data:image/png;base64,{qr_b64}" width="100">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # PDF CARNET (TAMAÑO TARJETA REAL 85x55mm)
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page(); pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            t_q = f"q_{id_buscado}.png"; qr_s.save(t_q, border=0)
            pdf_c.image(t_q, 58, 12, 22, 22)
            pdf_c.set_font("Arial", 'B', 8); pdf_c.set_xy(5, 18); pdf_c.cell(0, 4, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            pdf_c.set_xy(5, 23); pdf_c.cell(0, 4, f"ID: {p.get('DOCUMENTO')}")
            st.download_button("🪪 Descargar Carnet (Para Impresión)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(t_q): os.remove(t_q)

            # --- REGISTRO DE EVOLUCIÓN ---
            st.divider()
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo"):
                    col1, col2 = st.columns(2)
                    with col1: mot=st.text_area("Motivo"); val=st.text_area("Valoración"); tal=st.text_input("Talla (cm)")
                    with col2: pes=st.text_input("Peso (kg)"); pre=st.text_input("T.A."); epi=st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR CONSULTA"):
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                      data={"entry.2019369477":id_buscado, "entry.611862537":mot, "entry.1088523869":val, "entry.1275746503":tal, "entry.949747647":pes, "entry.2091389798":pre, "entry.616774918":epi})
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL Y PDF ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.subheader("📋 Historial de Evoluciones")
                
                # PDF Historial con todos los datos del paciente
                pdf_h = FPDF(); pdf_h.add_page()
                pdf_h.set_font("Arial", 'B', 16); pdf_h.cell(0, 10, "HISTORIA CLÍNICA - VIDA QR", 0, 1, 'C')
                pdf_h.set_font("Arial", 'B', 11); pdf_h.set_fill_color(240, 240, 240)
                pdf_h.cell(0, 8, f"PACIENTE: {p.get('NOMBRE')}", 1, 1, 'L', True)
                pdf_h.set_font("Arial", '', 10)
                pdf_h.cell(0, 7, f"ID: {p.get('DOCUMENTO')} | RH: {p.get('RH')} | EPS: {p.get('EPS')}", 1, 1, 'L')
                pdf_h.cell(0, 7, f"EMERGENCIA: {nom_e} - TEL: {tel_e}", 1, 1, 'L')
                pdf_h.ln(5)

                for _, f in h_p.iterrows():
                    pdf_h.set_font("Arial", 'B', 10); pdf_h.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 'B', 1, 'L')
                    pdf_h.set_font("Arial", '', 9)
                    pdf_h.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACIÓN: {f.get('10. EPICRISIS')}\nSIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}")
                    pdf_h.ln(4)
                
                st.download_button("📄 Descargar Historial Completo (PDF)", pdf_h.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")

                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p style="margin:10px 0;"><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div style="display:flex; gap:10px; margin-bottom:10px;">
                            <div class="dato-box">📏 {f.get('4. TALLA')} cm</div>
                            <div class="dato-box">⚖️ {f.get('5. PESO')} kg</div>
                            <div class="dato-box">🩸 TA: {f.get('6. PRESIÓN ARTERIAL')}</div>
                        </div>
                        <p style="margin:5px 0;"><b>VALORACIÓN:</b> {f.get('10. EPICRISIS')}</p>
                        <p style="margin:5px 0; color:#555 !important;"><b>EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
