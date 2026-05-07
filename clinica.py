import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA PROFESIONAL (TEXTO NEGRO, VERDE MENTA, MORADO) ---
st.markdown("""
    <style>
    /* Fondo y Textos */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro en toda la app */
    html, body, [class*="st-"], p, div, label, h1, h2, h3, span {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjetas de Paciente e Historial */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 25px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 12px;
        border: 2px dashed #feb2b2; margin-top: 15px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .vital-sign {
        background-color: #e6fffa; border: 1px solid #4fd1c5;
        padding: 5px 12px; border-radius: 8px; margin-right: 8px;
        display: inline-block; font-size: 14px;
    }

    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 4px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: 900 !important; 
        margin-bottom: 12px; border-radius: 10px;
    }
    
    /* Botones Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.5em; width: 100%; text-transform: uppercase;
    }

    /* Inputs Blancos */
    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; border: 2px solid #a2d2ff !important; 
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE LIMPIEZA DE DATOS ---
def normalizar(texto):
    """Elimina tildes y deja en mayúsculas para comparar sin errores."""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').upper().strip()

def buscar_en_tabla(fila, palabras_clave):
    """Busca un dato en la fila ignorando variaciones de nombre de columna."""
    for col in fila.index:
        col_norm = normalizar(col)
        if any(normalizar(p) in col_norm for p in palabras_clave):
            return fila[col]
    return "No registrado"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        # Estandarizar documentos para cruce de tablas
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in normalizar(c) or "ID" in normalizar(c)), None)
            if c_doc: df[c_doc] = df[c_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta e Historial"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 Registro del Paciente"): st.session_state.menu = "Registro"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---

if st.session_state.menu == "Registro":
    st.markdown("<h1 style='text-align: center;'>📝 Registro del Paciente</h1>", unsafe_allow_html=True)
    with st.form("form_reg", clear_on_submit=True):
        st.markdown("### 👤 Datos Personales")
        c1, c2 = st.columns(2)
        n_pac = c1.text_input("Nombre Completo")
        d_pac = c2.text_input("Documento Identidad")
        
        c3, c4, c5 = st.columns(3)
        r_pac = c3.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        e_pac = c4.text_input("Edad")
        s_pac = c5.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
        
        eps_pac = st.text_input("Entidad de Salud (EPS)")
        
        st.markdown("### 🚨 Emergencias")
        ce_n = st.text_input("Nombre Contacto de Emergencia")
        ce_t = st.text_input("Teléfono de Contacto")
        
        st.markdown("### 💊 Antecedentes de Base")
        ant_base = st.text_area("Describa alergias, cirugías o condiciones crónicas")
        
        if st.form_submit_button("REGISTRAR PACIENTE"):
            st.success(f"Paciente {n_pac} preparado para vinculación."); st.balloons()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>🔍 Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente para Consultar").strip()
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in normalizar(c) or "ID" in normalizar(c)), None)
        pac = df_p[df_p[c_doc_p] == busq] if c_doc_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            # Buscar evoluciones
            c_doc_h = next((c for c in df_h.columns if "DOC" in normalizar(c) or "ID" in normalizar(c)), None)
            h_p = df_h[df_h[c_doc_h] == busq] if c_doc_h else pd.DataFrame()
            
            # Tarjeta Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {buscar_en_tabla(p, ["NOMBRE"])}</h2>
                <p style='font-size: 18px;'>ID: {busq} | RH: {buscar_en_tabla(p, ["RH"])} | EPS: {buscar_en_tabla(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;">🚨 <b>CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0;">{buscar_en_tabla(p, ["CONTACTO"])} — <b>Tel:</b> {buscar_en_tabla(p, ["TELEFONO"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ AGREGAR NUEVA EVOLUCIÓN"):
                with st.form("evo_f", clear_on_submit=True):
                    mot = st.text_input("1. Motivo"); c1,c2,c3 = st.columns(3)
                    tll = c1.text_input("2. Talla (cm)"); pes = c2.text_input("3. Peso (kg)"); ten = c3.text_input("4. TA")
                    ant = st.text_area("5. Antecedentes"); med = st.text_area("6. Meds")
                    lab = st.text_area("7. Laboratorios"); val = st.text_input("8. Valoración"); epi = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        pay = {"entry.2019369477": busq, "entry.611862537": mot, "entry.949747647": tll, "entry.2091389798": pes, "entry.882053172": ten, "entry.889985940": ant, "entry.2016051626": med, "entry.1088523869": lab, "entry.1275746503": val, "entry.616774918": epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("Guardado correctamente"); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL VISUAL RESTAURADO ---
            st.markdown("### 🕒 Línea de Tiempo Médica")
            if not h_p.empty:
                for i in range(len(h_p)-1, -1, -1):
                    f = h_p.iloc[i]
                    st.markdown(f"""
                    <div class="evolution-card">
                        <p style="color:#2b6cb0; margin-bottom:8px;">📅 FECHA: {buscar_en_tabla(f, ["MARCA", "FECHA"])}</p>
                        <p style='font-size: 17px;'><b>📋 VALORACIÓN:</b> {buscar_en_tabla(f, ["VALORACI"])}</p>
                        <p><b>🩺 MOTIVO:</b> {buscar_en_tabla(f, ["MOTIVO"])}</p>
                        <div style='margin: 12px 0;'>
                            <span class="vital-sign">📏 {buscar_en_tabla(f, ["TALLA"])} cm</span>
                            <span class="vital-sign">⚖️ {buscar_en_tabla(f, ["PESO"])} kg</span>
                            <span class="vital-sign">💓 TA: {buscar_en_tabla(f, ["PRESIÓN", "TENSIÓN"])}</span>
                        </div>
                        <p>📝 <b>EPICRISIS:</b> {buscar_en_tabla(f, ["EPICRISIS"])}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay evoluciones previas para este paciente.")
        else: st.warning("⚠️ Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>📊 Base de Datos General</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Pacientes", "Historial Completo"])
    with tab1: st.dataframe(df_p, use_container_width=True)
    with tab2: st.dataframe(df_h, use_container_width=True)
