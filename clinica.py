import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN DE ALTO NIVEL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA "PERFECTA" (CONTRASTE MÁXIMO Y COLORES SOLICITADOS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro ultra-legible */
    html, body, [class*="st-"], p, div, label, h1, h2, h3, span, li {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjeta Principal */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 12px;
        border: 2px dashed #feb2b2; margin-top: 15px;
    }

    /* Tarjeta de Evolución (Ajuste Solicitado) */
    .evolution-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .vital-sign-tag {
        background-color: #e6fffa; border: 2px solid #4fd1c5;
        padding: 6px 14px; border-radius: 10px; margin-right: 10px;
        display: inline-block; font-size: 15px; color: #234e52 !important;
    }

    /* Navegación Sidebar Morado */
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

    /* Estilo de Inputs */
    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; border: 2px solid #a2d2ff !important; 
        color: #000000 !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE DATOS PRO (CERO CRUCES) ---
def clean_txt(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_field(row, keys):
    """Busca el valor exacto evitando cruces de columnas similares."""
    for col in row.index:
        norm_col = clean_txt(col)
        if any(clean_txt(k) == norm_col or clean_txt(k) in norm_col for k in keys):
            return row[col]
    return "No registrado"

@st.cache_data(ttl=1)
def load_all_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        # Sanitización de IDs para el cruce
        for df in [p, h]:
            c_id = next((c for c in df.columns if "DOC" in clean_txt(c) or "ID" in clean_txt(c)), None)
            if c_id: df[c_id] = df[c_id].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = load_all_data()

# --- 4. NAVEGACIÓN Y LOGOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta e Historial"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="110"></div>', unsafe_allow_html=True)
    if st.button("📝 Registro del Paciente"): st.session_state.menu = "Registro del Paciente"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta e Historial"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base de Datos"

# --- 5. LÓGICA DE INTERFAZ ---

if st.session_state.menu == "Registro del Paciente":
    st.markdown("<h1 style='text-align: center;'>📝 Registro del Paciente</h1>", unsafe_allow_html=True)
    with st.form("reg_form_master"):
        st.markdown("### 👤 Información Vital")
        c1, c2 = st.columns(2)
        n_comp = c1.text_input("Nombre Completo")
        d_iden = c2.text_input("Documento de Identidad")
        
        c3, c4, c5 = st.columns(3)
        r_rh = c3.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        e_edad = c4.text_input("Edad")
        s_sexo = c5.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
        
        st.markdown("### 🚨 Contactos y Salud")
        eps_n = st.text_input("Entidad de Salud (EPS)")
        c_emerg = st.text_input("Nombre Contacto de Emergencia")
        t_emerg = st.text_input("Teléfono de Emergencia")
        ant_p = st.text_area("Antecedentes Médicos (Alergias, Cirugías, Crónicos)")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            st.success("✅ Paciente listo para base de datos."); st.balloons()

elif st.session_state.menu == "Consulta e Historial":
    st.markdown("<h1 style='text-align: center;'>🔍 Consulta e Historial</h1>", unsafe_allow_html=True)
    target = st.text_input("Buscar por Documento").strip()
    
    if target and df_p is not None:
        c_id_p = next((c for c in df_p.columns if "DOC" in clean_txt(c) or "ID" in clean_txt(c)), None)
        p_row = df_p[df_p[c_id_p] == target] if c_id_p else pd.DataFrame()
        
        if not p_row.empty:
            p = p_row.iloc[0]
            c_id_h = next((c for c in df_h.columns if "DOC" in clean_txt(c) or "ID" in clean_txt(c)), None)
            h_data = df_h[df_h[c_id_h] == target] if c_id_h else pd.DataFrame()
            
            # Tarjeta Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {get_field(p, ["NOMBRE", "PACIENTE"])}</h2>
                <p style='font-size: 19px;'><b>DOCUMENTO:</b> {target} | <b>RH:</b> {get_field(p, ["RH"])} | <b>EPS:</b> {get_field(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0; font-size: 16px;">🚨 <b>EMERGENCIA:</b></p>
                    <p style="margin:0;">{get_field(p, ["CONTACTO"])} — <b>Tel:</b> {get_field(p, ["TELEFONO"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Evoluciones (Orden 1-9)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN MÉDICA"):
                with st.form("evo_form_final"):
                    m_c = st.text_input("1. Motivo de Consulta"); col1, col2, col3 = st.columns(3)
                    t_c = col1.text_input("2. Talla (cm)"); p_c = col2.text_input("3. Peso (kg)"); ta_c = col3.text_input("4. Tensión (TA)")
                    a_c = st.text_area("5. Antecedentes"); m_med = st.text_area("6. Medicamentos")
                    l_c = st.text_area("7. Laboratorios"); v_c = st.text_input("8. Valoración Médica"); e_c = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        # Endpoint de Google Forms
                        pay = {"entry.2019369477": target, "entry.611862537": m_c, "entry.949747647": t_c, "entry.2091389798": p_c, "entry.882053172": ta_c, "entry.889985940": a_c, "entry.2016051626": m_med, "entry.1088523869": l_c, "entry.1275746503": v_c, "entry.616774918": e_c}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("✅ Guardado"); st.cache_data.clear(); st.rerun()

            # --- RENDERIZADO DE HISTORIAL (ANTISEÑAL CRUZADA) ---
            st.markdown("### 🕒 Línea de Tiempo de Evoluciones")
            if not h_data.empty:
                for _, f in h_data.iloc[::-1].iterrows():
                    st.markdown(f"""
                    <div class="evolution-card">
                        <p style="color:#2b6cb0; font-size: 14px;">📅 FECHA: {get_field(f, ["MARCA", "FECHA"])}</p>
                        <p style='font-size: 18px;'><b>🩺 MOTIVO:</b> {get_field(f, ["MOTIVO"])}</p>
                        <div style='margin: 15px 0;'>
                            <span class="vital-sign-tag">📏 Talla: {get_field(f, ["TALLA"])}</span>
                            <span class="vital-sign-tag">⚖️ Peso: {get_field(f, ["PESO"])}</span>
                            <span class="vital-sign-tag">💓 TA: {get_field(f, ["PRESION", "TENSION"])}</span>
                        </div>
                        <p>📋 <b>VALORACIÓN:</b> {get_field(f, ["VALORACI"])}</p>
                        <p>📝 <b>EPICRISIS:</b> {get_field(f, ["EPICRISIS"])}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Sin registros previos.")

elif st.session_state.menu == "Base de Datos":
    st.markdown("<h1 style='text-align: center;'>📊 Base de Datos Central</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Listado de Pacientes", "Historial Global"])
    with t1: st.dataframe(df_p, use_container_width=True)
    with t2: st.dataframe(df_h, use_container_width=True)
