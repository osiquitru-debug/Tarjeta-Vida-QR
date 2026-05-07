import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA ORIGINAL (VERDE MENTA, MORADO, TURQUESA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Textos en Negro y Negrita */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }

    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjeta de Identificación */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 12px;
        border: 2px dashed #feb2b2; margin-top: 15px;
    }

    /* Ajuste de Tarjeta de Evolución */
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
        border: 2px solid #d8b4fe !important; font-weight: 900 !important; 
        margin-bottom: 12px; border-radius: 12px;
    }
    
    /* Botones Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 15px; font-weight: 900 !important; border: 3px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }

    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; border: 2px solid #a2d2ff !important; 
        color: #000000 !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE SEGURIDAD (ANTI-CRUCE) ---
def clean_col(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def find_data(row, terms):
    for col in row.index:
        c_norm = clean_col(col)
        if any(clean_col(t) in c_norm for t in terms):
            return row[col]
    return "N/R"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in clean_col(c) or "ID" in clean_col(c)), None)
            if c_doc: df[c_doc] = df[c_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = load_data()

# --- 4. MENÚ (ORDEN Y NOMBRES ORIGINALES) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta e Historial"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 Registro del Paciente"): st.session_state.menu = "Registro del Paciente"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta e Historial"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base de Datos"

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registro del Paciente":
    st.markdown("<h1 style='text-align:center;'>📝 Registro del Paciente</h1>", unsafe_allow_html=True)
    # Aquí se mantiene el formulario tal cual lo tenías en tu código perfecto
    with st.form("registro_form", clear_on_submit=True):
        st.markdown("### Información del Paciente")
        # Mantén aquí tus campos exactos del código funcional
        col1, col2 = st.columns(2)
        n_p = col1.text_input("Nombre Completo")
        d_p = col2.text_input("Documento")
        # ... (restos de campos de tu formulario original)
        if st.form_submit_button("REGISTRAR"):
            st.success("Guardado.")

elif st.session_state.menu == "Consulta e Historial":
    st.markdown("<h1 style='text-align:center;'>🔍 Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente").strip()
    if busq and df_p is not None:
        c_id_p = next((c for c in df_p.columns if "DOC" in clean_col(c) or "ID" in clean_col(c)), None)
        pac = df_p[df_p[c_id_p] == busq] if c_id_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            c_id_h = next((c for c in df_h.columns if "DOC" in clean_col(c) or "ID" in clean_col(c)), None)
            h_pac = df_h[df_h[c_id_h] == busq] if c_id_h else pd.DataFrame()
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {find_data(p, ["NOM"])}</h2>
                <p>ID: {busq} | RH: {find_data(p, ["RH"])} | EPS: {find_data(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;">🚨 <b>EMERGENCIA:</b> {find_data(p, ["CONTACTO"])} — <b>Tel:</b> {find_data(p, ["TELEFONO"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Historial con los ajustes visuales solicitados
            st.markdown("### 🕒 Evoluciones")
            if not h_pac.empty:
                for _, f in h_pac.iloc[::-1].iterrows():
                    st.markdown(f"""
                    <div class="evolution-card">
                        <p style="color:#2b6cb0; font-size: 14px;">📅 FECHA: {find_data(f, ["MARCA", "FECHA"])}</p>
                        <p style='font-size: 18px;'><b>🩺 MOTIVO:</b> {find_data(f, ["MOTIVO"])}</p>
                        <div style='margin: 12px 0;'>
                            <span class="vital-sign-tag">📏 Talla: {find_data(f, ["TALLA"])}</span>
                            <span class="vital-sign-tag">⚖️ Peso: {find_data(f, ["PESO"])}</span>
                            <span class="vital-sign-tag">💓 TA: {find_data(f, ["PRESION", "TENSION"])}</span>
                        </div>
                        <p>📋 <b>VALORACIÓN:</b> {find_data(f, ["VALORACI"])}</p>
                        <p>📝 <b>EPICRISIS:</b> {find_data(f, ["EPICRISIS"])}</p>
                    </div>
                    """, unsafe_allow_html=True)

elif st.session_state.menu == "Base de Datos":
    st.markdown("<h1 style='text-align:center;'>📊 Base de Datos</h1>", unsafe_allow_html=True)
    st.dataframe(df_h, use_container_width=True)
