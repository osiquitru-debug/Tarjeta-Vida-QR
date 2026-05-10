import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segnoimport streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    /* Fondo y texto general */
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{ color: #000000 !important; }}

    /* FLECHAS BLANCAS (CHEVRON) - FORZADO */
    button[data-testid="stSidebarCollapseIcon"] svg,
    button[aria-label="Collapse sidebar"] svg,
    button[aria-label="Expand sidebar"] svg,
    .st-emotion-cache-6qob1r svg {{
        fill: #ffffff !important;
        color: #ffffff !important;
        stroke: #ffffff !important;
    }}
    
    /* Asegurar que el botón contenedor no opaque el color */
    button[data-testid="stSidebarCollapseIcon"], 
    button[aria-label="Collapse sidebar"], 
    button[aria-label="Expand sidebar"] {{
        color: #ffffff !important;
    }}

    /* Inputs: Fondo blanco y letra negra */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Botones Verde Menta */
    div.stButton > button {{
        background-color: #98FF98 !important; 
        color: #000000 !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        border: 1px solid #7ed37e !important;
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
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    }}
    .footer {{ 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        text-align: center; color: #555555 !important; font-size: 0.8em; padding: 10px;
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
st.image(LOGO_URL, width=220)

if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
            cel = st.text_input("Celular")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alert = st.text_area("Condiciones Especiales (Alergias, Enfermedades de base)")
        st.subheader("🚨 Emergencia")
        enom = st.text_input("Nombre Contacto"); etel = st.text_input("Teléfono Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel, "entry.celular_id": cel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            def obtener_dato(df_row, palabras_clave):
                for col in df_row.index:
                    if all(palabra in col for palabra in palabras_clave):
                        return df_row[col]
                return "No registra"

            nom_emer = obtener_dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_emer = obtener_dato(p, ["TEL", "CONTACTO", "EMERGENCIA"])
            alertas = obtener_dato(p, ["CONDICIONES", "ESPECIALES"])

            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'No registra')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO', 'No registra')} | <b>EDAD:</b> {p.get('EDAD', 'No registra')} | <b>RH:</b> {p.get('RH', 'No registra')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'No registra')} | <b>CEL:</b> {p.get('CELULAR', 'No registra')}</p>
                <p><b>⚠️ ALERTAS:</b> {alertas}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {nom_emer} (Tel: {tel_emer})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            pdf = FPDF()
            pdf.add_page()
            try: pdf.image(LOGO_URL, 10, 8, 30)
            except: pass
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "Historia Clinica Completa - Tarjeta Vida QR", ln=True, align='C')
            pdf.ln(5)
            
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, "DATOS DEL PACIENTE", 1, 1, 'L', 1)
            pdf.set_font("Arial", '', 9)
            info_p = (f"Nombre: {p.get('NOMBRE')}\n"
                      f"Documento: {p.get('DOCUMENTO')} | Edad: {p.get('EDAD')} | RH: {p.get('RH')}\n"
                      f"EPS: {p.get('EPS')} | Celular: {p.get('CELULAR')}\n"
                      f"Alertas: {alertas}\n"
                      f"CONTACTO EMERGENCIA: {nom_emer} - Tel: {tel_emer}")
            pdf.multi_cell(0, 5, info_p); pdf.ln(5)

            if not h_p.empty:
                pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, "HISTORIAL DE EVOLUCIONES", 1, 1, 'L', 1)
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 6, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, 'L')
                    pdf.set_font("Arial", '', 8)
                    txt_evo = (f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\n"
                               f"VALORACION: {f.get('2. VALORACIÓN')}\n"
                               f"MEDIDAS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}\n"
                               f"ANTECEDENTES: {f.get('7. ANTECEDENTES MEDICOS')}\n"
                               f"TRATAMIENTO/MEDICAMENTOS: {f.get('8. MEDICAMENTOS')}\n"
                               f"LABORATORIOS: {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}\n"
                               f"EPICRISIS: {f.get('10. EPICRISIS')}")
                    pdf.multi_cell(0, 4, txt_evo); pdf.ln(2)

            st.download_button("📥 Descargar Reporte PDF Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1: 
                        v_mot = st.text_area("3. Motivo"); v_val = st.text_area("2. Valoración"); v_ant = st.text_area("7. Antecedentes"); v_tal = st.text_input("4. Talla")
                    with c2:
                        v_pes = st.text_input("5. Peso"); v_pre = st.text_input("6. Presión"); v_med = st.text_area("8. Medicamentos"); v_lab = st.text_area("9. Laboratorios"); v_epi = st.text_area("10. Epicrisis")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        data_e = {"entry.2019369477": id_buscado, "entry.611862537": v_mot, "entry.1088523869": v_val, "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre, "entry.2016051626": v_med, "entry.616774918": v_epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_e)
                        st.success("✅ Guardado."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 Evoluciones")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>💊 MEDICAMENTOS:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p><b>🔬 LABS:</b> {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}</p>
                        <p style='font-size:0.9em; color:#444; border-top:1px solid #eee; padding-top:5px;'>
                            <b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}
                        </p>
                    </div>""", unsafe_allow_html=True)
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (PARÁMETROS FIJOS NO NEGOCIABLES) ---
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
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
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
    if st.button("🏠 Inicio", key="nav1"): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", key="nav2"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", key="nav3"): st.session_state.menu = "Consulta"; st.rerun()

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
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            ndoc = st.text_input("Documento")
            fnac = st.text_input("Fecha de Nacimiento (DD/MM/AAAA)")
        with c2:
            ed = st.text_input("Edad")
            ep = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            enfer = st.text_input("Enfermedades/Condiciones")
        aler = st.text_area("Alergias/Observaciones")
        enom = st.text_input("Contacto Emergencia")
        etel = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, 
                "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, 
                "entry.1892763134": enom, "entry.2011749615": etel, "entry.123": fnac, "entry.456": aler, "entry.789": enfer
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Datos enviados."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- QR INDIVIDUAL (FIDELIDAD AL PACIENTE) ---
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_p)
            qr_buf = io.BytesIO(); qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # --- VISTA EN PANTALLA ---
            st.markdown(f"""
            <div class="medical-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:2;">
                        <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                        <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')}</p>
                        <p><b>EPS:</b> {p.get('EPS')}</p>
                        <div class="emergency-box">🚨 SOS: {p.get('NOMBRE CONTACTO', 'No registra')} - {p.get('TELÉFONO CONTACTO', 'No registra')}</div>
                    </div>
                    <div style="flex:1; text-align:right;">
                        <img src="data:image/png;base64,{qr_b64}" width="120" style="border-radius:10px;">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- PDF CARNET (REPLICA EXACTA DE LA IMAGEN SUMINISTRADA) ---
            pdf = FPDF(orientation='L', unit='mm', format=(85.6, 54))
            pdf.add_page(); pdf.set_auto_page_break(False); pdf.set_margins(0,0,0)
            
            # Fondo y Contenedor QR
            pdf.set_fill_color(162, 210, 255); pdf.rect(0, 0, 85.6, 54, 'F') 
            pdf.set_fill_color(255, 255, 255); pdf.rect(58, 6, 22, 22, 'F')
            
            tmp_qr = f"q_{id_buscado}.png"; qr_gen.save(tmp_qr, border=1)
            pdf.image(tmp_qr, 59, 7, 20)

            # Tabla de Datos (Campos exactos de tu imagen)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(5, 5); pdf.cell(0, 4, "NOMBRE:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 8); pdf.cell(0, 4, p.get('NOMBRE')[:35])
            
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 13); pdf.cell(0, 4, "FECHA DE NACIMIENTO:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 16); pdf.cell(0, 4, p.get('EDAD', '---'))
            
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 21); pdf.cell(0, 4, "TIPO DE SANGRE:"); pdf.set_font("Arial", '', 8); pdf.set_xy(5, 24); pdf.cell(0, 4, p.get('RH'))
            
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 29); pdf.cell(0, 4, "ALERGIAS:"); pdf.set_font("Arial", '', 7); pdf.set_xy(5, 32); pdf.multi_cell(50, 3, p.get('ALERGIAS', 'Ninguna')[:60])

            # Banda SOS (Rojo)
            pdf.set_fill_color(200, 0, 0); pdf.rect(0, 40, 85.6, 14, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
            pdf.set_xy(0, 42); pdf.cell(85.6, 5, "CONTACTO DE EMERGENCIA", 0, 1, 'C')
            pdf.set_xy(0, 47); pdf.cell(85.6, 5, f"{p.get('NOMBRE CONTACTO', '---')} - {p.get('TELÉFONO CONTACTO', '---')}", 0, 1, 'C')

            # --- EVOLUCIONES MÉDICAS (TU ESTRUCTURA FIJA) ---
            st.divider()
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style='border-top:1px solid #eee; padding-top:5px;'><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)

            st.download_button("🪪 Descargar Carnet", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            if os.path.exists(tmp_qr): os.remove(tmp_qr)
