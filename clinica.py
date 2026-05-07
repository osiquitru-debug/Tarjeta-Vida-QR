import streamlit as st
import pandas as pd
import requests
import unicodedata

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA DE ALTO CONTRASTE (DISEÑO SOLICITADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Texto Negro Intenso y Negrita */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    /* Tarjetas de Datos del Paciente */
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }

    /* Tarjetas de Evolución */
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Sidebar Morado */
    [data-testid="stSidebar"] { 
        background-color: #f3e8ff !important; 
        border-right: 4px solid #d8b4fe; 
    }
    
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 3px solid #d8b4fe !important; font-weight: 900 !important; margin-bottom: 12px; 
    }

    /* Botones de Acción Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 15px; font-weight: 900 !important; border: 3px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }

    /* Inputs Blancos con Borde Azul */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #a2d2ff !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS E INTELIGENCIA DE COLUMNAS ---
def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def obtener_dato(fila, palabras_clave):
    """Busca un dato en la fila comparando con palabras clave para evitar errores de nombres en el Sheet."""
    for col in fila.index:
        if any(p in normalizar(col) for p in palabras_clave):
            return fila[col]
    return "N/A"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url_base = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url_base}&sheet=pacientes")
        h = pd.read_csv(f"{url_base}&sheet=historial")
        # Limpieza de documentos para asegurar cruce perfecto
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if c_doc: 
                df[c_doc] = df[c_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. CONFIGURACIÓN DE LINKS Y LOGO ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

# --- 5. SIDEBAR (NAVEGACIÓN) ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="{URL_LOGO}" width="120"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 6. SECCIÓN: REGISTRAR PACIENTE ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>📝 Registro Inicial</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["Cédula", "T.I.", "C.E.", "Pasaporte"])
            doc = st.text_input("Documento")
        with c2:
            cel = st.text_input("Celular")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            eps = st.text_input("EPS")
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre de contacto")
        e_tel = st.text_input("Teléfono de contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload_p = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": doc.strip(), 
                "entry.1043165037": cel, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": e_nom, "entry.2011749615": e_tel
            }
            requests.post(URL_FORM_PACIENTES, data=payload_p)
            st.success("✅ Paciente registrado correctamente."); st.cache_data.clear()

# --- 7. SECCIÓN: CONSULTA E HISTORIAL ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>🔍 Gestión de Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente").strip()
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in normalizar(c)), "DOCUMENTO")
        pac = df_p[df_p[c_doc_p] == busq]
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in normalizar(c)), "DOCUMENTO")
            h_p = df_h[df_h[c_doc_h] == busq] if df_h is not None else pd.DataFrame()

            # Tarjeta de Identificación
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {obtener_dato(p, ["NOM"])}</h2>
                <p>DOC: {busq} | RH: {obtener_dato(p, ["RH"])} | EPS: {obtener_dato(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 EMERGENCIA:</b> {obtener_dato(p, ["CONTAC"])} — {obtener_dato(p, ["TEL"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Formulario de Evolución (Orden del Formulario)
            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    f_motivo = st.text_input("1. Motivo de la Consulta")
                    f_val = st.text_area("2. Valoración Clínica")
                    col1, col2, col3 = st.columns(3)
                    f_talla = col1.text_input("3. Talla (cm)")
                    f_peso = col2.text_input("4. Peso (kg)")
                    f_pa = col3.text_input("5. Presión Arterial (TA)")
                    f_ant = st.text_area("6. Antecedentes Médicos")
                    f_meds = st.text_area("7. Medicamentos")
                    f_lab = st.text_area("8. Laboratorios")
                    f_epi = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        payload_h = {
                            "entry.2019369477": busq, "entry.611862537": f_motivo,
                            "entry.1275746503": f_val, "entry.949747647": f_talla,
                            "entry.2091389798": f_peso, "entry.889985940": f_ant,
                            "entry.2016051626": f_meds, "entry.882053172": f_pa,
                            "entry.1088523869": f_lab, "entry.616774918": f_epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Datos enviados."); st.cache_data.clear(); st.rerun()

            # Mapeo y Visualización de Evoluciones Pasadas
            st.markdown("### 🕒 Línea de Tiempo Clínica")
            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; font-size:13px; margin:0;">📅 FECHA: {obtener_dato(f, ["MARCA", "FECHA", "TIME"])}</p>
                    <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
                    <p style="font-size:18px;"><b>🩺 MOTIVO:</b> {obtener_dato(f, ["MOTIVO"])}</p>
                    <p><b>📋 VALORACIÓN:</b> {obtener_dato(f, ["VALORAC"])}</p>
                    <div style='margin:12px 0; display: flex; gap: 8px;'>
                        <span style='background:#e6fffa; border:1px solid #4fd1c5; padding:5px 10px; border-radius:8px;'>📏 {obtener_dato(f, ["TALLA"])} cm</span>
                        <span style='background:#e6fffa; border:1px solid #4fd1c5; padding:5px 10px; border-radius:8px;'>⚖️ {obtener_dato(f, ["PESO"])} kg</span>
                        <span style='background:#e6fffa; border:1px solid #4fd1c5; padding:5px 10px; border-radius:8px;'>💓 TA: {obtener_dato(f, ["PRESION", "TA"])}</span>
                    </div>
                    <p><b>🏥 ANTECEDENTES:</b> {obtener_dato(f, ["ANTECEDEN"])}</p>
                    <p><b>💊 MEDICAMENTOS:</b> {obtener_dato(f, ["MEDICAM"])}</p>
                    <p><b>🧪 LABORATORIOS:</b> {obtener_dato(f, ["LABORA"])}</p>
                    <p><b>📝 EPICRISIS:</b> {obtener_dato(f, ["EPICRIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.error("❌ Paciente no encontrado.")

# --- 8. SECCIÓN: BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>📊 Bases de Datos</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["👥 Lista de Pacientes", "🕒 Historial Completo"])
    with t1: 
        if df_p is not None: st.dataframe(df_p, use_container_width=True)
    with t2: 
        if df_h is not None: st.dataframe(df_h, use_container_width=True)
