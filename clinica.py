import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
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
    .carnet-info {{ flex: 2; color: #000 !important; }}
    .carnet-qr-white {{ flex: 1; background: white; padding: 8px; border-radius: 8px; text-align: center; }}
    .label-sos-rojo {{
        background-color: #f43f5e; color: white !important; padding: 8px;
        border-radius: 6px; font-size: 13px; margin-top: 10px; font-weight: bold; text-align: center;
    }}
    
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 8px solid #b7e4c7; margin-bottom: 10px; color: #000;
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
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta y Carnet", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. SECCIÓN REGISTRAR ---
if st.session_state.menu == "Registrar":
    st.title("📝 Registro de Nuevo Paciente")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            documento = st.text_input("Número de Documento")
            celular = st.text_input("Número de Celular")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("Factor RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        especiales = st.text_area("Condiciones Especiales")
        st.subheader("🚨 Contacto de Emergencia")
        e_nombre = st.text_input("Nombre del Contacto")
        e_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, 
                "entry.1302424820": documento, "entry.1801154005": edad, 
                "entry.1172011247": eps, "entry.162368130": rh, 
                "entry.1892763134": e_nombre, "entry.2011749615": e_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

# --- 5. SECCIÓN CONSULTA ---
elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta")
    id_buscado = st.text_input("Documento del Paciente", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            buff_qr = io.BytesIO()
            qr_gen.save(buff_qr, kind='png', scale=10)
            qr_b64 = base64.b64encode(buff_qr.getvalue()).decode()

            # Carnet en Pantalla
            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header"><img src="{LOGO_URL}" width="70"><b>TARJETA VIDA QR</b></div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>PACIENTE:</b> {p.get('NOMBRE')}</p>
                        <p><b>ID:</b> {p.get('DOCUMENTO')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <div class="label-sos-rojo">🚨 SOS: {nom_e}<br>{tel_e}</div>
                    </div>
                    <div class="carnet-qr-white"><img src="data:image/png;base64,{qr_b64}" width="100"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Botón Descargar Carnet
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page()
            pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            qr_p_path = f"qr_c_{id_buscado}.png"
            qr_gen.save(qr_p_path, border=0)
            pdf_c.image(qr_p_path, 58, 14, 22, 22)
            pdf_c.set_font("Arial", 'B', 8); pdf_c.set_xy(4, 20); pdf_c.cell(0, 4, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            st.download_button("📥 Descargar Carnet (PDF)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(qr_p_path): os.remove(qr_p_path)

            # --- SECCIÓN HISTORIAL Y DESCARGA ---
            st.divider()
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            
            if not h_p.empty:
                st.subheader("📋 Historial Médico")
                
                # --- GENERAR PDF DEL HISTORIAL COMPLETO ---
                pdf_h_doc = FPDF()
                pdf_h_doc.add_page()
                pdf_h_doc.set_font("Arial", 'B', 16)
                pdf_h_doc.cell(0, 10, f"HISTORIA CLÍNICA - {p.get('NOMBRE')}", 0, 1, 'C')
                pdf_h_doc.set_font("Arial", '', 10)
                pdf_h_doc.cell(0, 10, f"Documento: {p.get('DOCUMENTO')} | RH: {p.get('RH')} | EPS: {p.get('EPS')}", 0, 1, 'C')
                pdf_h_doc.ln(5)

                for _, f in h_p.iterrows():
                    pdf_h_doc.set_fill_color(240, 240, 240)
                    pdf_h_doc.set_font("Arial", 'B', 10)
                    pdf_h_doc.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, 'L', True)
                    pdf_h_doc.set_font("Arial", '', 9)
                    pdf_h_doc.multi_cell(0, 6, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACIÓN: {f.get('10. EPICRISIS')}\nSIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}", 1, 'L')
                    pdf_h_doc.ln(4)
                
                st.download_button("📄 Descargar Historial Completo (PDF)", pdf_h_doc.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")

                # Visualización en pantalla
                for _, f in h_p.iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {f.get('MARCA TEMPORAL')}</small><p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p><p><b>Epicrisis:</b> {f.get('10. EPICRISIS')}</p></div>""", unsafe_allow_html=True)
            else:
                st.warning("No hay evoluciones registradas.")
