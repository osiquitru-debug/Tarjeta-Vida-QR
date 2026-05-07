import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL (TEXTO NEGRO Y CAJAS BLANCAS) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

st.markdown(f"""
    <style>
    /* Fondo general pastel suave */
    .stApp {{ 
        background-color: #f0f7f4 !important; 
        color: #000000 !important;
    }}
    
    /* Forzar que todos los textos de Streamlit sean negros */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: #000000 !important;
    }}

    /* CAJAS DE DATOS BLANCAS (Inputs, Selectbox, Textarea) */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Tarjeta de Paciente */
    .medical-card {{
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 20px;
        border-left: 12px solid #a2d2ff; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px; 
        color: #000000 !important;
    }}
    
    /* Caja de Emergencia */
    .emergency-box {{
        background-color: #ffe5d9; 
        padding: 15px; 
        border-radius: 12px;
        border: 2px dashed #ffcad4; 
        color: #d64545 !important; 
        font-weight: bold; 
        margin-top: 10px;
    }}

    /* Tarjetas de Evolución */
    .evo-card {{
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 15px;
        border: 1px solid #d8e2dc; 
        border-left: 8px solid #b7e4c7; 
        margin-bottom: 12px; 
        color: #000000 !important;
    }}

    .grid-medidas {{ 
        display: grid; 
        grid-template-columns: 1fr 1fr 1fr; 
        gap: 10px; 
        margin: 10px 0; 
        background-color: #f9fbf9;
        padding: 8px;
        border-radius: 8px;
        color: #000000 !important;
    }}

    /* Botón Cian del logo */
    div.stButton > button {{
        background-color: #84dcc6 !important;
        color: #000000 !important; /* Texto del botón también negro para consistencia */
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
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
    st.markdown("<h2 style='text-align: center;'>GESTIÓN</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 TARJETA VIDA")
    st.markdown("### *Cuidado Integral con Tecnología QR*")
    st.write("Plataforma médica optimizada para la comunidad de Guadalupe, Huila.")

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
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_esp = st.text_area("Condiciones Especiales (Alergias, etc.)")
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre de Referencia")
        c_tel = st.text_input("Teléfono de Referencia")
        
        if st.form_submit_button("FINALIZAR REGISTRO"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            try:
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success("✅ Paciente registrado."); st.cache_data.clear()
            except: st.error("Error de conexión.")

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120)
    st.title("🔍 PERFIL DEL PACIENTE")
    id_buscado_raw = st.text_input("Documento del Paciente").strip()
    id_buscado = id_buscado_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p style='margin:5px 0;'><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EDAD:</b> {p.get('EDAD')} años</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EN EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            
            # Botón PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, f"HISTORIA CLINICA - {p.get('NOMBRE')}", ln=True, align='C')
            st.download_button(label="📥 Exportar HC a PDF", data=pdf.output(dest='S').encode('latin-1'), file_name=f"HC_{id_buscado}.pdf")

            # REGISTRO DE NUEVA EVOLUCIÓN
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN MÉDICA"):
                with st.form("f_evo", clear_on_submit=True):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        v_val = st.text_area("Valoración Física")
                        v_mot = st.text_area("Motivo")
                        v_tal = st.text_input("Talla (cm)")
                    with col_e2:
                        v_pes = st.text_input("Peso (kg)")
                        v_pre = st.text_input("Tensión Arterial")
                        v_med = st.text_area("Tratamiento")
                        v_epi = st.text_area("Notas / Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        e_payload = {
                            "entry.2019369477": id_buscado, "entry.1088523869": v_val, "entry.611862537": v_mot,
                            "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre,
                            "entry.2016051626": v_med, "entry.616774918": v_epi
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Sincronizado."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 Evoluciones Recientes")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                        <b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}<br>
                        <div class="grid-medidas">
                            <span>📏 Talla: {f.get('4. TALLA')}</span>
                            <span>⚖️ Peso: {f.get('5. PESO')}</span>
                            <span>🩸 P.A.: {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p>💊 <b>Plan:</b> {f.get('8. MEDICAMENTOS')}</p>
                    </div>""", unsafe_allow_html=True)
