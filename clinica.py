import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (ESTÉTICA ORIGINAL) ---
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
        border-radius: 15px;
        padding: 20px;
        max-width: 450px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }}
    .carnet-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
    .carnet-body {{ display: flex; gap: 15px; }}
    .carnet-qr-white {{ flex: 1; background: white; padding: 10px; border-radius: 10px; text-align: center; }}
    .label-sos-rojo {{
        background-color: #f43f5e; color: white !important; padding: 8px;
        border-radius: 8px; font-size: 13px; margin-top: 10px; font-weight: bold; text-align: center;
    }}
    
    /* EVOLUCIONES (CELDAS BLANCAS) */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 18px; 
        border-radius: 10px;
        border-left: 8px solid #b7e4c7; 
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }}
    .grid-datos {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; 
        background: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #f0f0f0; margin: 10px 0;
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
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA Y CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abrilycompañia")

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=250)
    st.markdown("### *'Tu información médica vital, siempre contigo.'*")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1: nom = st.text_input("Nombre"); tdoc = st.selectbox("Tipo", ["CC","TI","CE"]); doc = st.text_input("Documento")
        with c2: ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+","O-","A+","A-","B+","B-"])
        e_n = st.text_input("Nombre Emergencia"); e_t = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR"):
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", 
                          data={"entry.346175428":nom, "entry.1650757004":tdoc, "entry.1302424820":doc, "entry.1801154005":ed, "entry.1172011247":ep, "entry.162368130":rh, "entry.1892763134":e_n, "entry.2011749615":e_t})
            st.success("Registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta")
    id_buscado = st.text_input("Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            # QR
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_s = segno.make(url_p)
            buf = io.BytesIO(); qr_s.save(buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(buf.getvalue()).decode()

            # Vista Pantalla
            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header"><img src="{LOGO_URL}" width="70"><b>TARJETA VIDA QR</b></div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>{p.get('NOMBRE')}</b></p>
                        <p>ID: {p.get('DOCUMENTO')}</p>
                        <p>RH: {p.get('RH')} | EPS: {p.get('EPS')}</p>
                        <div class="label-sos-rojo">SOS: {nom_e}<br>{tel_e}</div>
                    </div>
                    <div class="carnet-qr-white"><img src="data:image/png;base64,{qr_b64}" width="100"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (TAMAÑO REAL TARJETA 85x55) ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.set_margins(0,0,0)
            pdf_c.add_page()
            pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            
            q_tmp = f"q_{id_buscado}.png"
            qr_s.save(q_tmp, border=0)
            pdf_c.image(q_tmp, 58, 12, 22, 22)
            pdf_c.set_font("Arial", 'B', 8); pdf_c.set_xy(5, 18); pdf_c.cell(0, 4, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            st.download_button("🪪 Descargar Carnet (85x55mm)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(q_tmp): os.remove(q_tmp)

            # --- REGISTRO EVOLUCIÓN ---
            st.divider()
            with st.expander("➕ NUEVA EVOLUCIÓN"):
                with st.form("f_ev"):
                    c1, c2 = st.columns(2)
                    with c1: mot=st.text_area("Motivo"); val=st.text_area("Valoración"); tal=st.text_input("Talla")
                    with c2: pes=st.text_input("Peso"); pre=st.text_input("TA"); epi=st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                      data={"entry.2019369477":id_buscado, "entry.611862537":mot, "entry.1088523869":val, "entry.1275746503":tal, "entry.949747647":pes, "entry.2091389798":pre, "entry.616774918":epi})
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL PDF (CONFIGURACIÓN PROFESIONAL) ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.subheader("📋 Evoluciones")
                pdf_h = FPDF()
                pdf_h.add_page(); pdf_h.set_font("Arial", 'B', 14)
                pdf_h.cell(0, 10, f"HISTORIAL MÉDICO: {p.get('NOMBRE')}", 0, 1, 'C')
                for _, f in h_p.iterrows():
                    pdf_h.set_font("Arial", 'B', 10); pdf_h.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, 'L')
                    pdf_h.set_font("Arial", '', 9); pdf_h.multi_cell(0, 6, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nSIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}\nEPICRISIS: {f.get('10. EPICRISIS')}", 1)
                    pdf_h.ln(3)
                st.download_button("📄 Descargar Historial (A4)", pdf_h.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")

                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div class="grid-datos">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
