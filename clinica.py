import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica QR", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS ORIGINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }

    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; }

    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }

    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .evo-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #edf2f7; margin-bottom: 10px; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIÓN PDF ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MÉDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_fill_color(240, 255, 244)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DATOS GENERALES", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"Nombre: {paciente.get('NOMBRE', 'N/A')}", ln=True)
    pdf.cell(0, 8, txt=f"ID: {paciente.get('DOCUMENTO', 'N/A')} | RH: {paciente.get('RH', 'N/A')}", ln=True)
    pdf.multi_cell(0, 8, txt=f"Condiciones: {paciente.get('CONDICIONES', 'Ninguna registrada')}")
    pdf.ln(5)
    pdf.set_fill_color(243, 232, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True, fill=True)
    if not historial.empty:
        for i, fila in historial.iterrows():
            pdf.set_font("Arial", 'B', 10)
            pdf.ln(2)
            pdf.multi_cell(0, 5, txt=f"Fecha Registro: {fila.get('MARCA DE TIEMPO', 'N/A')}")
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=f"Tratamiento: {fila.get('TRATAMIENTO', 'N/A')}")
            pdf.multi_cell(0, 5, txt=f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/A')}")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

def obtener_valor(df_row, keywords):
    for col in df_row.index:
        if all(word in col for word in keywords):
            return df_row[col]
    return "No registrado"

# --- 6. NAVEGACIÓN (RESTAURADA) ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 7. SECCIONES ---
if st.session_state.menu == "Registrar":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image(URL_LOGO, use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        tipo_doc = c1.selectbox("Tipo de Documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Registro Civil", "Cédula de Extranjería"])
        cedula = c2.text_input("Número de Documento")
        condiciones = st.text_area("Condiciones Especiales / Alergias")
        c3, c4 = st.columns(2)
        edad = c3.text_input("Edad")
        rh = c4.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = st.text_input("EPS")
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(), "entry.1801154005": edad,
                    "entry.1172011247": eps, "entry.162368130": rh, "entry.346363": condiciones
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == id_bus].reset_index(drop=True)
            
            # Botón de PDF
            st.download_button(label="🖨️ Descargar PDF", data=generar_pdf(p, h_p), file_name=f"Historial_{id_bus}.pdf")

            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: black !important;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>Condiciones:</b> {obtener_valor(p, ["CONDICIONES"])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📅 Historial")
            for i in range(len(h_p)-1, -1, -1):
                fila = h_p.iloc[i]
                st.markdown(f'<div class="evolution-card"><b>Evolución #{i+1}</b> - {fila.get("MARCA DE TIEMPO")}<br>🩺 {fila.get("TRATAMIENTO")}</div>', unsafe_allow_html=True)

            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución")
                fecha_hoy = datetime.now().strftime('%d/%m/%Y')
                fecha_input = st.text_input("Fecha (DD/MM/AAAA)", value=fecha_hoy)
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    tratamiento_con_fecha = f"[{fecha_input}] {t}"
                    requests.post(URL_FORM_HISTORIAL, data={"entry.2019369477": id_bus, "entry.611862537": tratamiento_con_fecha, "entry.2016051626": m})
                    st.success("✅ Guardado.")
                    st.cache_data.clear()
                    st.rerun()

# --- SECCIÓN DE BASE DE DATOS REPARADA ---
elif st.session_state.menu == "Base":
    st.markdown("<h1 style='text-align: center;'>📊 Bases de Datos</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📋 Pacientes registrados", "📔 Historial de evoluciones"])
    
    if df_p is not None:
        with t1:
            st.dataframe(df_p, use_container_width=True)
    else:
        t1.error("No se pudo cargar la base de pacientes.")
        
    if df_h is not None:
        with t2:
            st.dataframe(df_h, use_container_width=True)
    else:
        t2.error("No se pudo cargar el historial.")
