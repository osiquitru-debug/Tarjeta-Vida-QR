import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA "PERFECTA" (TEXTO NEGRO, VERDE MENTA, MORADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar texto negro y negrita absoluta */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    /* Inputs Blancos */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }

    /* Sidebar Morado Original */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: 900 !important; margin-bottom: 10px; 
    }

    /* Botón Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }

    /* Tarjetas de Diseño */
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; 
        border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #cbd5e0; 
        border-left: 12px solid #63b3ed; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE DATOS (RADAR ANTI-CRUCE) ---
def norm(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def buscar_dato(fila, palabras):
    for col in fila.index:
        if any(norm(p) in norm(col) for p in palabras):
            return fila[col]
    return "No registrado"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in norm(c)), None)
            if c_doc: df[c_doc] = df[c_doc].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Número de Documento")
        condiciones = st.text_area("Condiciones Especiales / Alergias")
        edad = st.text_input("Edad")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = st.text_input("EPS")
        cel = st.text_input("Celular")
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1302424820": cedula,
                "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps,
                "entry.162368130": rh, "entry.346363": condiciones, 
                "entry.1892763134": e_nom, "entry.2011749615": e_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        p_row = df_p[df_p["DOCUMENTO"] == id_bus]
        if not p_row.empty:
            p = p_row.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == id_bus]
            
            # Tarjeta de Datos
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {buscar_en_tabla(p, ["NOM"])}</h2>
                <p>ID: {id_bus} | RH: {buscar_en_tabla(p, ["RH"])} | Edad: {buscar_en_tabla(p, ["EDAD"])}</p>
                <p>EPS: {buscar_en_tabla(p, ["EPS"])} | Condiciones: {buscar_en_tabla(p, ["CONDICIONES", "ALERGIAS"])}</p>
                <div class="emergency-box">
                    🚨 <b>EMERGENCIA:</b> {buscar_en_tabla(p, ["NOMBRE CONTACTO"])} - {buscar_en_tabla(p, ["TELEFONO CONTACTO"])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Historial (Evoluciones)
            st.markdown("### 🕒 Historial de Evoluciones")
            for _, fila in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <b>📅 Registro: {buscar_dato(fila, ["MARCA", "TIME"])}</b><br><br>
                    🩺 <b>TRATAMIENTO:</b> {buscar_dato(fila, ["TRATAMIENTO"])}<br>
                    💊 <b>MEDICAMENTOS:</b> {buscar_dato(fila, ["MEDICAMENTO"])}<br>
                    📋 <b>PROCEDIMIENTOS:</b> {buscar_dato(fila, ["PROCEDIMIENTO"])}
                </div>
                """, unsafe_allow_html=True)

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("h_form"):
                    t = st.text_input("Tratamiento")
                    m = st.text_area("Medicamentos")
                    pr = st.text_area("Procedimientos")
                    if st.form_submit_button("GUARDAR"):
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                      data={"entry.2019369477": id_bus, "entry.611862537": t, "entry.2016051626": m, "entry.1088523869": pr})
                        st.cache_data.clear(); st.rerun()

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    st.dataframe(df_p)
