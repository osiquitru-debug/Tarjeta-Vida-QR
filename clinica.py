import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA DE ALTO CONTRASTE (VERDE MENTA, MORADO, TURQUESA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro y negrita para legibilidad absoluta */
    html, body, [class*="st-"], p, div, label, h1, h2, h3, span, li {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjeta Principal del Paciente */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 12px;
        border: 2px dashed #feb2b2; margin-top: 15px;
    }

    /* Tarjeta de Evolución Optimizada */
    .evolution-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .vital-sign-tag {
        background-color: #e6fffa; border: 2px solid #4fd1c5;
        padding: 6px 14px; border-radius: 10px; margin-right: 10px;
        display: inline-block; font-size: 15px;
    }

    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 4px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 3px solid #d8b4fe !important; font-weight: 900 !important; 
        margin-bottom: 12px; border-radius: 12px;
    }
    
    /* Botones de Acción Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 15px; font-weight: 900 !important; border: 3px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }

    /* Inputs y Textareas */
    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; border: 2px solid #a2d2ff !important; 
        color: #000000 !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE BÚSQUEDA DE DATOS (EVITA CRUCES) ---
def norm_c(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_data(fila, claves):
    for col in fila.index:
        if any(norm_c(k) in norm_c(col) for k in claves):
            return fila[col]
    return "N/R"

@st.cache_data(ttl=1)
def fetch_sheets():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in norm_c(c) or "ID" in norm_c(c)), None)
            if c_doc: df[c_doc] = df[c_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = fetch_sheets()

# --- 4. NAVEGACIÓN ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta e Historial"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 Registro del Paciente"): st.session_state.menu = "Registro del Paciente"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta e Historial"
    if st.button("📊 Base de datos"): st.session_state.menu = "Base de datos"

# --- 5. SECCIONES ---

if st.session_state.menu == "Registro del Paciente":
    st.markdown("<h1 style='text-align:center;'>📝 Registro del Paciente</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        st.markdown("### 👤 Datos Personales")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        cedula = c2.text_input("Documento de Identidad")
        
        c3, c4, c5 = st.columns(3)
        rh = c3.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        edad = c4.text_input("Edad")
        sexo = c5.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
        
        eps = st.text_input("EPS")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre del Contacto")
        c_tel = st.text_input("Teléfono del Contacto")
        
        st.markdown("### 💊 Antecedentes Médicos")
        ant_med = st.text_area("Alergias, Cirugías, Enfermedades Crónicas")
        
        if st.form_submit_button("REGISTRAR PACIENTE"):
            st.success("✅ Datos registrados correctamente."); st.balloons()

elif st.session_state.menu == "Consulta e Historial":
    st.markdown("<h1 style='text-align:center;'>🔍 Consulta e Historial</h1>", unsafe_allow_html=True)
    target = st.text_input("Documento del Paciente").strip()
    
    if target and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in norm_c(c) or "ID" in norm_c(c)), None)
        p_row = df_p[df_p[c_doc_p] == target] if c_doc_p else pd.DataFrame()
        
        if not p_row.empty:
            p = p_row.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in norm_c(c) or "ID" in norm_c(c)), None)
            h_rows = df_h[df_h[c_doc_h] == target] if c_doc_h else pd.DataFrame()
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {get_data(p, ["NOM"])}</h2>
                <p>ID: {target} | RH: {get_data(p, ["RH"])} | EPS: {get_data(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;">🚨 <b>EMERGENCIA:</b> {get_data(p, ["CONTAC"])} — <b>Tel:</b> {get_data(p, ["TEL"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    m_c = st.text_input("1. Motivo"); c1, c2, c3 = st.columns(3)
                    t_c = c1.text_input("2. Talla (cm)"); p_c = c2.text_input("3. Peso (kg)"); ta_c = c3.text_input("4. TA")
                    a_c = st.text_area("5. Antecedentes"); med_c = st.text_area("6. Medicamentos")
                    l_c = st.text_area("7. Laboratorios"); v_c = st.text_input("8. Valoración"); e_c = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        pay = {"entry.2019369477": target, "entry.611862537": m_c, "entry.949747647": t_c, "entry.2091389798": p_c, "entry.882053172": ta_c, "entry.889985940": a_c, "entry.2016051626": med_c, "entry.1088523869": l_c, "entry.1275746503": v_c, "entry.616774918": e_c}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("✅ Guardado."); st.cache_data.clear(); st.rerun()

            st.markdown("### 🕒 Línea de Tiempo de Evoluciones")
            for _, f in h_rows.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; font-size: 14px;">📅 FECHA: {get_data(f, ["MARCA", "FECHA"])}</p>
                    <p style='font-size: 18px;'><b>🩺 MOTIVO:</b> {get_data(f, ["MOTIVO"])}</p>
                    <div style='margin: 12px 0;'>
                        <span class="vital-sign-tag">📏 Talla: {get_data(f, ["TALLA"])}</span>
                        <span class="vital-sign-tag">⚖️ Peso: {get_data(f, ["PESO"])}</span>
                        <span class="vital-sign-tag">💓 TA: {get_data(f, ["PRESION", "TENSION"])}</span>
                    </div>
                    <p>📋 <b>VALORACIÓN:</b> {get_data(f, ["VALORACI"])}</p>
                    <p>🧪 <b>LABORATORIOS:</b> {get_data(f, ["LABORAT"])}</p>
                    <p>📝 <b>EPICRISIS:</b> {get_data(f, ["EPICRISIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.warning("⚠️ Paciente no encontrado.")

elif st.session_state.menu == "Base de datos":
    st.markdown("<h1 style='text-align:center;'>📊 Base de Datos</h1>", unsafe_allow_html=True)
    if df_h is not None: st.dataframe(df_h, use_container_width=True)
