import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL (ESTILO CONSULTORÍA PREMIUM) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Enlace del logo
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Lato:wght@300;400&display=swap" rel="stylesheet">
    <style>
    /* Reset y Tipografía */
    .stApp {{
        background-color: #f4fafa !important; /* Mint Pastel Cálido */
        font-family: 'Lato', sans-serif;
    }}
    
    h1, h2, h3 {{
        font-family: 'Poppins', sans-serif;
        color: #1e293b !important; /* Azul Medianoche Profesional */
    }}

    /* Barra Lateral */
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }}
    
    /* Tarjeta de Paciente (Estilo McKinsey Insight) */
    .medical-card {{
        background-color: #ffffff;
        padding: 30px;
        border-radius: 4px;
        border-top: 6px solid #22d3ee; /* Acento Turquesa */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        color: #334155;
    }}
    
    /* Caja de Emergencia */
    .emergency-box {{
        background-color: #fff1f2;
        padding: 15px;
        border-radius: 4px;
        border-left: 4px solid #f43f5e;
        color: #9f1239;
        font-weight: 600;
        margin-top: 15px;
        font-size: 0.9em;
    }}

    /* Tarjetas de Evoluciones (Estilo BCG Slide) */
    .evo-card {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 0px; /* Estilo cuadrado más formal */
        border: 1px solid #e2e8f0;
        border-left: 8px solid #0891b2;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }}
    .evo-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}

    .grid-medidas {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 15px;
        margin: 15px 0;
        background: #f8fafc;
        padding: 10px;
        border-radius: 4px;
    }}

    /* Botones Premium */
    div.stButton > button {{
        background-color: #0891b2 !important;
        color: white !important;
        border-radius: 2px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }}
    
    div.stButton > button:hover {{
        background-color: #0e7490 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }}

    /* Inputs y Forms */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        border-radius: 2px !important;
        border: 1px solid #cbd5e1 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (Mantenida) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        def limpiar(txt): return str(txt).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except Exception as e:
        st.error(f"Error de sistema: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 REGISTRO", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 HISTORIAL", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("TARJETA VIDA")
    st.markdown("### *Intelligence Healthcare Management*")
    st.write("Bienvenido a la plataforma centralizada de gestión clínica de Guadalupe, Huila. Utilice el menú lateral para gestionar registros o consultar historiales.")

elif st.session_state.menu == "Registrar":
    st.title("REGISTRO CLÍNICO")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Identificación", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_especiales = st.text_area("Notas / Alergias / Preexistencias")
        st.subheader("Contacto de Emergencia")
        c_nom = st.text_input("Nombre de Referencia")
        c_tel = st.text_input("Teléfono de Referencia")
        
        if st.form_submit_button("COMPLETAR REGISTRO"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel,
            }
            try:
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success("✅ Registro almacenado en la nube."); st.cache_data.clear()
            except: st.error("Error de sincronización.")

elif st.session_state.menu == "Consulta":
    st.title("CONSULTA PERFIL PACIENTE")
    busqueda_raw = st.text_input("Identificación del paciente").strip()
    id_buscado = busqueda_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0; font-weight:600;'>👤 {p.get('NOMBRE')}</h2>
                <hr style='border: 0.5px solid #e2e8f0; margin: 15px 0;'>
                <p><b>{p.get('TIPO DE DOCUMENTO')}:</b> {p.get('DOCUMENTO')} | <b>EDAD:</b> {p.get('EDAD')} años</p>
                <p><b>EPS:</b> {p.get('EPS')} | <b>RH:</b> {p.get('RH')}</p>
                <p style='color:#0891b2;'><b>RESUMEN CLÍNICO:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 PROTOCOLO EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            if not h_p.empty:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "REPORTE CLINICO ESTRUCTURADO", ln=True, align='C')
                st.download_button(label="📥 EXPORTAR HC (PDF)", data=pdf.output(dest='S').encode('latin-1'), file_name=f"HC_{id_buscado}.pdf", mime="application/pdf")

            with st.expander("📝 NUEVA ENTRADA MÉDICA"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v2 = st.text_area("Valoración Física")
                        v3 = st.text_area("Motivo Consulta")
                        v4 = st.text_input("Talla (cm)")
                        v5 = st.text_input("Peso (kg)")
                    with c2:
                        v6 = st.text_input("Tensión Arterial")
                        v7 = st.text_area("Antecedentes")
                        v8 = st.text_area("Prescripción")
                        v10 = st.text_area("Epicrisis / Plan")
                    if st.form_submit_button("REGISTRAR EVOLUCIÓN"):
                        e_payload = {
                            "entry.2019369477": id_buscado, "entry.1088523869": v2, "entry.611862537": v3,
                            "entry.1275746503": v4, "entry.949747647": v5, "entry.2091389798": v6,
                            "entry.889985940": v7, "entry.2016051626": v8, "entry.616774918": v10
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Sincronizado."); st.cache_data.clear(); st.rerun()

            st.subheader("REGISTROS CRONOLÓGICOS")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <span style="font-size:0.8em; color:#64748b; font-weight:600;">📅 {f.get('MARCA TEMPORAL')}</span>
                            <span style="background:#0891b2; color:white; padding:2px 10px; font-size:0.7em; font-weight:600;">VISITA MÉDICA</span>
                        </div>
                        <p style="font-weight:600; color:#1e293b; margin-bottom:5px;">MOTIVO: <span style="font-weight:400;">{f.get('3. MOTIVO DE LA CONSULTA')}</span></p>
                        <p style="font-weight:600; color:#1e293b; margin-bottom:5px;">VALORACIÓN: <span style="font-weight:400;">{f.get('2. VALORACIÓN')}</span></p>
                        <div class="grid-medidas">
                            <span><b>Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>T.A.:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style="background:#e0f2fe; padding:10px; border-radius:2px; font-size:0.9em;">💊 <b>PLAN FARMACOLÓGICO:</b> {f.get('8. MEDICAMENTOS')}</p>
                    </div>""", unsafe_allow_html=True)
            else: st.info("No existen registros históricos para este perfil.")
        else: st.error(f"Identificación no válida o inexistente.")
