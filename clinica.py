import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA EXACTA DEL CÓDIGO BASE ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    /* Estética Base Original */
    .stApp { background-color: #f0f7f4 !important; }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Tarjeta de Paciente */
    .medical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #4fd1c5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #1a202c;
    }
    
    /* Caja de Emergencia */
    .emergency-box {
        background-color: #fff5f5;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #f56565;
        color: #c53030;
        font-weight: bold;
        margin-top: 10px;
    }
    
    /* Tarjetas de Historial */
    .evo-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #63b3ed;
        margin-bottom: 10px;
        color: #2d3748;
    }
    
    h1, h2, h3, label, p { color: #1a202c !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #ffffff;
        color: #2d3748;
        border: 1px solid #e2e8f0;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        border-color: #4fd1c5;
        color: #4fd1c5;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RECURSOS Y URLs ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN (TRES BOTONES ORIGINALES) ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.markdown("---")
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 5. LÓGICA DE VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Sistema Tarjeta Vida")
    st.markdown("""
    <div class="medical-card">
        <h3>Bienvenido al Panel de Gestión Médica</h3>
        <p>Seleccione una opción en el menú de la izquierda para comenzar.</p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Nuevo Paciente")
    with st.form("registro_paciente", clear_on_submit=True):
        st.markdown("### 👤 Datos del Paciente")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería"])
            doc = st.text_input("Número de Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        celular = st.text_input("Celular de contacto")
        condiciones = st.text_area("Condiciones especiales (Alergias, Enfermedades de base)")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            e_nombre = st.text_input("Nombre contacto de emergencia")
        with ecol2:
            e_tel = st.text_input("Teléfono contacto de emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": doc,
                "entry.1801154005": edad, "entry.1043165037": celular, "entry.1172011247": eps,
                "entry.162368130": rh, "entry.346363": condiciones, "entry.1892763134": e_nombre, "entry.2011749615": e_tel
            }
            requests.post(URL_FORM_PACIENTES, data=payload)
            st.success("✅ Paciente registrado con éxito")
            st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    busqueda = st.text_input("Ingrese el Documento del Paciente").strip()
    
    if busqueda and df_p is not None:
        p_data = df_p[df_p["DOCUMENTO"] == busqueda]
        if not p_data.empty:
            p = p_data.iloc[0]
            # TARJETA VISUAL ORIGINAL
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {busqueda} | <b>EPS:</b> {p.get('EPS')} | <b>RH:</b> {p.get('RH')}</p>
                <div class="emergency-box">
                    🚨 CONTACTO DE EMERGENCIA:<br>
                    {p.get('NOMBRE CONTACTO EMERGENCIA', 'S/D')} — {p.get('TELEFONO CONTACTO EMERGENCIA', 'S/D')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FORMULARIO CON LOS 10 CAMPOS SOLICITADOS
            with st.expander("✍️ REGISTRAR EVOLUCIÓN MÉDICA"):
                with st.form("nueva_evolucion", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v_valoracion = st.text_area("Valoración")
                        v_motivo = st.text_area("Motivo de la Consulta")
                        v_talla = st.text_input("Talla")
                        v_peso = st.text_input("Peso")
                        v_presion = st.text_input("Presión Arterial")
                    with c2:
                        v_ante = st.text_area("Antecedentes Medicos")
                        v_med = st.text_area("Medicamentos")
                        v_lab = st.text_area("Laboratorios - Procedimientos")
                        v_epi = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR REGISTRO"):
                        payload_h = {
                            "entry.2019369477": busqueda, "entry.889985940": v_valoracion,
                            "entry.611862537": v_motivo, "entry.616774918": v_talla,
                            "entry.2091389798": v_peso, "entry.949747647": v_presion,
                            "entry.882053172": v_ante, "entry.2016051626": v_med,
                            "entry.1088523869": v_lab, "entry.1275746503": v_epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("Registro guardado")
                        st.cache_data.clear()
                        st.rerun()

            # HISTORIAL EN TARJETAS EVO-CARD
            st.subheader("📋 Historial Clínico")
            h_p = df_h[df_h["DOCUMENTO"] == busqueda] if df_h is not None else pd.DataFrame()
            if not h_p.empty:
                for _, f in h_p.sort_index(ascending=False).iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                        <b>Motivo:</b> {f.get('MOTIVO DE LA CONSULTA')}<br>
                        <b>Valoración:</b> {f.get('VALORACION')}<br>
                        <b>Signos:</b> Talla: {f.get('TALLA')} | Peso: {f.get('PESO')} | PA: {f.get('PRESION ARTERIAL')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay registros previos.")
        else:
            st.error("Paciente no encontrado.")
