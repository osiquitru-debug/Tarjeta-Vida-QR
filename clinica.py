import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA INTEGRAL RESTAURADA ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Textos en Negro Total y Negrita */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjeta Principal Paciente */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); margin-bottom: 25px;
    }
    
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 12px;
        border: 2px dashed #feb2b2; margin-top: 15px;
    }

    /* Tarjetas de Evolución del Historial */
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .vital-sign {
        background-color: #ebf8ff; color: #2c5282; padding: 5px 10px;
        border-radius: 8px; font-size: 14px; display: inline-block; margin-right: 10px;
    }

    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 4px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: 900 !important; margin-bottom: 12px; 
        border-radius: 10px;
    }
    
    /* Botones Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.5em; width: 100%; text-transform: uppercase;
    }
    
    /* Botón PDF */
    .stDownloadButton > button {
        background-color: #3182ce !important; color: white !important; 
        border-radius: 12px; font-weight: 900; width: 100%; border: none;
    }

    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; border: 2px solid #a2d2ff !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
def radar_dato(fila, terminos):
    for col in fila.index:
        if any(t in col.upper() for t in terminos):
            return fila[col]
    return "No registrado"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        p.columns = [c.strip().upper() for c in p.columns]
        h.columns = [c.strip().upper() for c in h.columns]
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in c or "ID" in c), None)
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

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. SECCIONES ---

if st.session_state.menu == "Registro":
    st.markdown("<h1 style='text-align: center;'>📝 Registro del Paciente</h1>", unsafe_allow_html=True)
    with st.form("registro_p", clear_on_submit=True):
        st.markdown("### 👤 Datos del Paciente")
        c1, c2 = st.columns(2)
        n_pac = c1.text_input("Nombre Completo")
        d_pac = c2.text_input("Documento Identidad")
        c3, c4, c5 = st.columns([1,1,2])
        r_pac = c3.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        e_pac = c4.text_input("Edad")
        eps_pac = c5.text_input("Entidad (EPS)")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ce_n = st.text_input("Nombre del Familiar/Contacto")
        ce_t = st.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("REGISTRAR PACIENTE EN SISTEMA"):
            st.success(f"Paciente {n_pac} registrado. Datos listos para envío.")

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>🔍 Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = st.text_input("Documento del Paciente").strip()
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in c or "ID" in c), None)
        pac = df_p[df_p[c_doc_p] == busq] if c_doc_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in c or "ID" in c), None)
            h_p = df_h[df_h[c_doc_h] == busq] if c_doc_h else pd.DataFrame()
            
            # Tarjeta Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {radar_dato(p, ["NOM"])}</h2>
                <p style='font-size: 18px;'>ID: {busq} | RH: {radar_dato(p, ["RH"])} | EPS: {radar_dato(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;">🚨 <b>CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0;">{radar_dato(p, ["CONTACTO"])} — <b>Tel:</b> {radar_dato(p, ["TELEFONO"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Evolución Form (1-9)
            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    mot = st.text_input("1. Motivo de la Consulta")
                    col1, col2, col3 = st.columns(3)
                    tll = col1.text_input("2. Talla (cm)")
                    pes = col2.text_input("3. Peso (kg)")
                    ten = col3.text_input("4. Tensión Arterial")
                    ant = st.text_area("5. Antecedentes Médicos")
                    med = st.text_area("6. Medicamentos")
                    lab = st.text_area("7. Laboratorios")
                    val = st.text_input("8. Valoración")
                    epi = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR REGISTRO"):
                        pay = {"entry.2019369477": busq, "entry.611862537": mot, "entry.949747647": tll, "entry.2091389798": pes, "entry.882053172": ten, "entry.889985940": ant, "entry.2016051626": med, "entry.1088523869": lab, "entry.1275746503": val, "entry.616774918": epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL VISUAL RESTAURADO ---
            st.markdown("### 🕒 Línea de Tiempo de Evoluciones")
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; margin-bottom:10px;">📅 FECHA: {radar_dato(f, ["MARCA", "FECHA"])}</p>
                    <p style='font-size: 17px;'><b>📋 VALORACIÓN professional:</b> {radar_dato(f, ["VALORACI"])}</p>
                    <p><b>🩺 MOTIVO:</b> {radar_dato(f, ["MOTIVO"])}</p>
                    <div style='margin: 10px 0;'>
                        <span class="vital-sign">📏 {radar_dato(f, ["TALLA"])} cm</span>
                        <span class="vital-sign">⚖️ {radar_dato(f, ["PESO"])} kg</span>
                        <span class="vital-sign">💓 TA: {radar_dato(f, ["PRESIÓN", "TENSIÓN"])}</span>
                    </div>
                    <p>🧪 <b>LABORATORIOS:</b> {radar_dato(f, ["LABORATORIO"])}</p>
                    <p>📝 <b>EPICRISIS:</b> {radar_dato(f, ["EPICRISIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.warning("No se encontró el paciente.")

elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>📊 Base de Datos</h1>", unsafe_allow_html=True)
    if df_p is not None: st.subheader("Pacientes"); st.dataframe(df_p)
    if df_h is not None: st.subheader("Evoluciones"); st.dataframe(df_h)
