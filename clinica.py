import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA BASE ORIGINAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Estilos CSS exactos del código base
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    .stApp { background-color: #f8fafc; }
    
    /* Banner Superior */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 0 0 30px 30px;
        text-align: center; color: white; margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Tarjetas */
    .medical-card {
        background: white; padding: 25px; border-radius: 20px;
        border-left: 8px solid #3b82f6; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .emergency-box {
        background-color: #fef2f2; padding: 15px; border-radius: 12px;
        border: 1px solid #fee2e2; color: #dc2626; font-weight: bold; margin-top: 10px;
    }
    
    .evo-card {
        background: white; padding: 20px; border-radius: 15px;
        border: 1px solid #e2e8f0; border-left: 5px solid #10b981;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff !important; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RECURSOS Y DATOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

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

def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "HISTORIAL CLINICO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Paciente: {paciente.get('NOMBRE')}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"ID: {paciente.get('DOCUMENTO')} | EPS: {paciente.get('EPS')} | RH: {paciente.get('RH')}", ln=True)
    pdf.ln(5)
    for _, f in historial.iterrows():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"Fecha: {f.get('MARCA TEMPORAL')}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        info = f"Motivo: {f.get('MOTIVO DE LA CONSULTA')}\nValoracion: {f.get('VALORACION')}\nSignos: Talla {f.get('TALLA')} - Peso {f.get('PESO')} - PA {f.get('PRESION ARTERIAL')}\nMedicamentos: {f.get('MEDICAMENTOS')}\nEpicrisis: {f.get('EPICRISIS')}"
        pdf.multi_cell(0, 5, info)
        pdf.ln(4)
    return pdf.output(dest='S').encode('latin-1', 'replace')

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN Y HEADER ---
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Menú Principal</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta y Evolución"): st.session_state.menu = "Consulta"

st.markdown('<div class="main-header"><h1>🩺 TARJETA VIDA</h1><p>Sistema de Gestión Médica Integral</p></div>', unsafe_allow_html=True)

# --- 4. LOGICA DE VISTAS ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

if st.session_state.menu == "Inicio":
    st.markdown("""
        <div class='medical-card' style='text-align: center;'>
            <h2>Bienvenido</h2>
            <p>Acceda a los módulos de registro y consulta desde el menú lateral.</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    with st.form("registro_form", clear_on_submit=True):
        st.markdown("### 📋 Datos Personales")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            cedula = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        cel = st.text_input("Celular")
        cond = st.text_area("Condiciones / Alergias")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        ce1, ce2 = st.columns(2)
        with ce1: e_nom = st.text_input("Nombre Contacto")
        with ce2: e_tel = st.text_input("Teléfono Contacto")
        
        if st.form_submit_button("REGISTRAR PACIENTE"):
            data_p = {"entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": cedula, 
                      "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps, 
                      "entry.162368130": rh, "entry.346363": cond, "entry.1892763134": e_nom, "entry.2011749615": e_tel}
            requests.post(URL_FORM_PACIENTES, data=data_p)
            st.success("Paciente guardado con éxito.")

elif st.session_state.menu == "Consulta":
    id_bus = st.text_input("🔍 Buscar por Documento").strip()
    if id_bus and df_p is not None:
        p_row = df_p[df_p["DOCUMENTO"] == id_bus]
        if not p_row.empty:
            p = p_row.iloc[0]
            st.markdown(f"""
                <div class="medical-card">
                    <h2>👤 {p.get('NOMBRE')}</h2>
                    <p><b>ID:</b> {id_bus} | <b>EPS:</b> {p.get('EPS')} | <b>RH:</b> {p.get('RH')}</p>
                    <div class="emergency-box">📞 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} - {p.get('TELEFONO CONTACTO EMERGENCIA')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📝 Nueva Evolución (10 Campos)"):
                with st.form("evo_form", clear_on_submit=True):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        v1 = st.text_area("Valoración")
                        v2 = st.text_area("Motivo de la Consulta")
                        v3 = st.text_input("Talla")
                        v4 = st.text_input("Peso")
                        v5 = st.text_input("Presión Arterial")
                    with ec2:
                        v6 = st.text_area("Antecedentes Medicos")
                        v7 = st.text_area("Medicamentos")
                        v8 = st.text_area("Laboratorios - Procedimientos")
                        v9 = st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        data_h = {"entry.2019369477": id_bus, "entry.889985940": v1, "entry.611862537": v2, 
                                  "entry.616774918": v3, "entry.2091389798": v4, "entry.949747647": v5, 
                                  "entry.882053172": v6, "entry.2016051626": v7, "entry.1088523869": v8, "entry.1275746503": v9}
                        requests.post(URL_FORM_HISTORIAL, data=data_h)
                        st.success("Evolución guardada.")
                        st.rerun()

            h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
            if not h_p.empty:
                st.download_button("📥 Descargar PDF", data=generar_pdf(p, h_p), file_name=f"Historial_{id_bus}.pdf")
                for _, f in h_p.sort_index(ascending=False).iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                    <b>Valoración:</b> {f.get('VALORACION')}<br><b>Motivo:</b> {f.get('MOTIVO DE LA CONSULTA')}</div>""", unsafe_allow_html=True)
        else: st.error("Paciente no registrado.")
