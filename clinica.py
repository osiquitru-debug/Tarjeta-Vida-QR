import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA INTEGRAL (VERDE MENTA, MORADO, TURQUESA) ---
st.markdown("""
    <style>
    /* Fondo General Verde Menta */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Tipografía y Textos en Negro Negrita */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjetas de Información */
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    
    /* Botones Turquesa Principales */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }
    
    /* Botón de Descarga PDF */
    .stDownloadButton > button {
        background-color: #3182ce !important; color: white !important; 
        border-radius: 12px; font-weight: bold; width: 100%; border: none;
    }
    
    input, textarea, [data-baseweb="select"] > div { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
def buscar_valor(fila, terminos):
    for col in fila.index:
        if any(t in col.upper() for t in terminos):
            return fila[col]
    return "N/A"

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

# --- 4. MENÚ LATERAL (ORDEN Y NOMBRES EXACTOS) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta e Historial"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 Registro del Paciente"): st.session_state.menu = "Registro"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registro":
    st.markdown("<h2 style='text-align: center;'>Registro del Paciente</h2>", unsafe_allow_html=True)
    with st.form("form_registro", clear_on_submit=True):
        st.markdown("### Datos Personales")
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nombre Completo")
        doc = c2.text_input("Documento de Identidad")
        c3, c4 = st.columns(2)
        rh = c3.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = c4.text_input("EPS")
        
        st.markdown("### Contacto de Emergencia")
        cem = st.text_input("Nombre del Contacto")
        tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("REGISTRAR PACIENTE"):
            # Aquí iría el POST a tu formulario de Google para Pacientes
            st.success(f"Paciente {nom} registrado con éxito.")

elif st.session_state.menu == "Consulta":
    busq = st.text_input("Ingrese Documento del Paciente").strip()
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in c or "ID" in c), None)
        pac = df_p[df_p[c_doc_p] == busq] if c_doc_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in c or "ID" in c), None)
            h_p = df_h[df_h[c_doc_h] == busq] if c_doc_h else pd.DataFrame()
            
            # Tarjeta de Identificación
            st.markdown(f"""<div class="medical-card">
                <h2>👤 {buscar_valor(p, ["NOM"])}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {buscar_valor(p, ["RH"])} | <b>EPS:</b> {buscar_valor(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 EMERGENCIA:</b> {buscar_valor(p, ["CONTACTO"])}</p>
                    <p style="margin:0;"><b>Tel:</b> {buscar_valor(p, ["TELEFONO"])}</p>
                </div></div>""", unsafe_allow_html=True)

            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "HISTORIA CLINICA", ln=True)
            st.download_button("📥 DESCARGAR PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{busq}.pdf")

            # Formulario de Evoluciones (Orden 1-9)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    mot = st.text_input("1. Motivo de la Consulta")
                    col1, col2, col3 = st.columns(3)
                    talla = col1.text_input("2. Talla (cm)")
                    peso = col2.text_input("3. Peso (kg)")
                    ta = col3.text_input("4. Tensión Arterial")
                    ant = st.text_area("5. Antecedentes Médicos")
                    med = st.text_area("6. Medicamentos")
                    lab = st.text_area("7. Laboratorios")
                    val = st.text_input("8. Valoración")
                    epi = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        # POST al formulario de Historial
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            # Tarjetas de Evolución
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""<div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {buscar_valor(f, ["MARCA", "FECHA"])}</b></p>
                    <p><b>🩺 MOTIVO:</b> {buscar_valor(f, ["MOTIVO"])}</p>
                    <p>📏 <b>TALLA:</b> {buscar_valor(f, ["TALLA"])} | ⚖️ <b>PESO:</b> {buscar_valor(f, ["PESO"])} | 💓 <b>TA:</b> {buscar_valor(f, ["PRESIÓN", "TENSIÓN"])}</p>
                    <p>🧪 <b>LABORATORIOS:</b> {buscar_valor(f, ["LABORATORIO"])}</p>
                    <p>📋 <b>VALORACIÓN:</b> {buscar_valor(f, ["VALORACI"])}</p>
                </div>""", unsafe_allow_html=True)
        else: st.warning("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("<h2 style='text-align: center;'>Base de Datos</h2>", unsafe_allow_html=True)
    if df_p is not None:
        st.subheader("Pacientes Registrados")
        st.dataframe(df_p, use_container_width=True)
    if df_h is not None:
        st.subheader("Historial de Evoluciones")
        st.dataframe(df_h, use_container_width=True)
