import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (FIDELIDAD TOTAL) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

st.markdown(f"""
    <style>
    /* FONDO GENERAL VERDE MEDICINAL */
    .stApp {{ background-color: #D8F3DC !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    
    /* BOTONES CLAROS Y TEXTO NEGRO */
    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 8px;
    }}
    
    h1, h2, h3, p, span, label, div {{ color: #000000 !important; font-family: 'Arial', sans-serif; }}

    /* CARNET AZUL CIELO (DISEÑO SOLICITADO) */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 15px;
        padding: 20px;
        max-width: 450px;
        margin: auto;
        border: 2px solid #ffffff;
    }}
    .label-sos-rojo {{
        background-color: #f43f5e; color: white !important; padding: 10px;
        border-radius: 8px; font-size: 13px; font-weight: bold; text-align: center; margin-top: 10px;
    }}
    
    /* CELDAS DE EVOLUCIÓN (BLANCAS CON TEXTO NEGRO) */
    .evo-card {{
        background-color: #ffffff !important; 
        padding: 25px; 
        border-radius: 12px;
        border: 1px solid #dddddd;
        border-left: 10px solid #2d6a4f; 
        margin-bottom: 20px;
    }}
    .evo-card b, .evo-card p, .evo-card span {{
        color: #000000 !important;
    }}
    .grid-datos {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; 
        background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin: 15px 0;
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

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("---")
    if st.button("🏠 INICIO", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 REGISTRAR PACIENTE", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 CONSULTA Y CARNET", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()
    st.markdown("---")
    st.caption("© 2026 Vida QR - Abri_Garcia_Sierra")

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Vida QR")
    st.image(LOGO_URL, width=300)
    st.markdown("## *'Tu información médica vital, siempre contigo.'*")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("form_registro"):
        st.subheader("📋 Datos Básicos")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE"])
            documento = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        st.markdown("---")
        st.subheader("🚨 Contacto de Emergencia")
        e_nombre = st.text_input("Nombre de quien llamar")
        e_tel = st.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            payload = {"entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": documento, "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh, "entry.1892763134": e_nombre, "entry.2011749615": e_tel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta de Historial")
    # Captura el ID de la URL si existe (para el escaneo del QR)
    query_params = st.query_params
    id_por_url = query_params.get("id", "")
    id_buscado = st.text_input("Ingrese Documento", value=id_por_url).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            # URL DEL QR (Apunta a la aplicación para abrir el historial)
            url_qr = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_code = segno.make(url_qr)
            qr_buffer = io.BytesIO()
            qr_code.save(qr_buffer, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buffer.getvalue()).decode()

            # --- CARNET EN PANTALLA ---
            st.markdown(f"""
            <div class="carnet-container">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <img src="{LOGO_URL}" width="70"><b>TARJETA VIDA QR</b>
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

            # --- PDF CARNET (AJUSTADO A 85x55mm REAL) ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page(); pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(0, 0, 85, 55, 'F')
            
            # Guardar QR temporal para el PDF
            tmp_qr = f"temp_qr_{id_buscado}.png"
            qr_code.save(tmp_qr, border=0)
            
            pdf_c.image(tmp_qr, 58, 12, 22, 22)
            pdf_c.set_font("Arial", 'B', 8); pdf_c.set_xy(5, 18)
            pdf_c.cell(0, 4, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            pdf_c.set_xy(5, 23); pdf_c.cell(0, 4, f"ID: {p.get('DOCUMENTO')} | RH: {p.get('RH')}")
            
            pdf_c.set_fill_color(244, 63, 94); pdf_c.rect(5, 36, 50, 12, 'F'); pdf_c.set_text_color(255,255,255)
            pdf_c.set_xy(5, 37); pdf_c.cell(50, 4, f"SOS: {nom_e[:20]}", 0, 1, 'C')
            pdf_c.set_xy(5, 41); pdf_c.cell(50, 4, f"TEL: {tel_e}", 0, 1, 'C')
            
            st.download_button("🪪 Descargar Carnet (Para Impresión)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_qr): os.remove(tmp_qr)

            # --- NUEVA EVOLUCIÓN ---
            st.divider()
            with st.expander("➕ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1: mot=st.text_area("Motivo"); val=st.text_area("Valoración (Epicrisis)"); tal=st.text_input("Talla")
                    with c2: pes=st.text_input("Peso"); pre=st.text_input("T.A."); obs=st.text_area("Observaciones")
                    if st.form_submit_button("GUARDAR CONSULTA"):
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                      data={"entry.2019369477":id_buscado, "entry.611862537":mot, "entry.1088523869":obs, "entry.1275746503":tal, "entry.949747647":pes, "entry.2091389798":pre, "entry.616774918":val})
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL (CELDAS BLANCAS Y DATOS REALES) ---
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.subheader("📋 Historial de Evoluciones")
                
                # PDF HISTORIAL COMPLETO
                pdf_h = FPDF(); pdf_h.add_page(); pdf_h.set_font("Arial", 'B', 16)
                pdf_h.cell(0, 10, "HISTORIA CLÍNICA - VIDA QR", 0, 1, 'C')
                pdf_h.set_font("Arial", 'B', 11); pdf_h.set_fill_color(230, 230, 230)
                pdf_h.cell(0, 8, f"PACIENTE: {p.get('NOMBRE')} | ID: {p.get('DOCUMENTO')}", 1, 1, 'L', True)
                pdf_h.ln(5)

                for _, f in h_p.iterrows():
                    # Mostrar evoluciones en pantalla
                    st.markdown(f"""
                    <div class="evo-card">
                        <p><small>📅 FECHA: {f.get('MARCA TEMPORAL')}</small></p>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div class="grid-datos">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 T.A:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>🩺 VALORACIÓN (EPICRISIS):</b> {f.get('10. EPICRISIS')}</p>
                        <p><b>📝 OBSERVACIONES:</b> {f.get('9. OBSERVACIONES')}</p>
                    </div>""", unsafe_allow_html=True)

                    # Añadir al PDF del historial
                    pdf_h.set_font("Arial", 'B', 10); pdf_h.cell(0, 8, f"FECHA: {f.get('MARCA TEMPORAL')}", 'B', 1, 'L')
                    pdf_h.set_font("Arial", '', 9)
                    pdf_h.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACIÓN: {f.get('10. EPICRISIS')}\nSIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}")
                    pdf_h.ln(4)
                
                st.download_button("📄 Descargar Historial Completo (PDF)", pdf_h.output(dest='S').encode('latin-1'), f"Historial_{id_buscado}.pdf")
