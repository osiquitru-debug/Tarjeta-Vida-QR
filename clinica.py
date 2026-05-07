import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    
    [data-testid="stSidebar"] {{
        background-color: #E5B1B1 !important;
        border-right: 2px solid #d4a5a5;
    }}
    
    h1, h2, h3, p, span, label, li, .stMarkdown, [data-testid="stSidebar"] .stMarkdown {{
        color: #000000 !important;
    }}

    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* ESTRUCTURA ORIGINAL: TARJETA DE PACIENTE */
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #000000;
    }}
    
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 1px dashed #f43f5e; color: #b91c1c; font-weight: bold; margin-top: 10px;
    }}

    /* ESTRUCTURA ORIGINAL: TARJETA DE EVOLUCIÓN */
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7;
        margin-bottom: 12px; color: #000000;
    }}

    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        gap: 10px; margin: 12px 0; font-size: 0.95em; 
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; padding: 8px 0;
    }}
    
    div.stButton > button {{
        background-color: #84dcc6 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }}

    /* Estilo para el Copyright */
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 0.8em;
        padding: 10px;
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
    st.markdown("<h2 style='text-align: center;'>OPCIONES</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2024 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.image(LOGO_URL, width=120)
    st.title("📝 REGISTRO MÉDICO")
    with st.form("f_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad"); eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c_esp = st.text_area("Condiciones Especiales / Alergias")
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre Referencia"); c_tel = st.text_input("Teléfono Referencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc, "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh, "entry.1892763134": c_nom, "entry.2011749615": c_tel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120)
    st.title("🔍 CONSULTA Y EVOLUCIÓN")
    id_buscado = st.text_input("Documento del Paciente").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA DE PACIENTE (ORIGINAL)
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EDAD:</b> {p.get('EDAD')} años</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            
            # PDF
            pdf = FPDF()
            pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, f"HC: {p.get('NOMBRE')}", ln=True, align='C')
            st.download_button("📥 Descargar HC (PDF)", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # Formulario Nueva Evolución
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        v_val = st.text_area("Valoración"); v_mot = st.text_area("Motivo"); v_tal = st.text_input("Talla (cm)")
                    with ce2:
                        v_pes = st.text_input("Peso (kg)"); v_pre = st.text_input("Presión"); v_med = st.text_area("Fórmula"); v_epi = st.text_area("Notas")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        e_payload = {"entry.2019369477": id_buscado, "entry.1088523869": v_val, "entry.611862537": v_mot, "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre, "entry.2016051626": v_med, "entry.616774918": v_epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # TARJETA DE EVOLUCIÓN (ORIGINAL SIN NÚMEROS)
            st.subheader("📋 Historial de Evoluciones")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                        <p style='margin: 5px 0;'><b>MOTIVO DE LA CONSULTA:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p style='margin: 5px 0;'><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 Tensión:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style='margin: 5px 0;'><b>💊 TRATAMIENTO:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p style='margin: 5px 0; font-size:0.85em; color: #555;'><b>NOTAS ADICIONALES:</b> {f.get('9. EPICRISIS O NOTAS ADICIONALES')}</p>
                    </div>""", unsafe_allow_html=True)
            else: st.info("Sin registros previos.")
