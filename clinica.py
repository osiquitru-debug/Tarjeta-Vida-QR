import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (RESTAURADO Y MEJORADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li { color: #000000 !important; font-weight: 600 !important; }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; 
        border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; 
        border-left: 8px solid #63b3ed; margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLS Y RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. FUNCIONES DE AYUDA ---
def normalizar_texto(texto):
    if pd.isna(texto): return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def buscar_dato(fila, palabras_clave):
    for col in fila.index:
        if any(p in normalizar_texto(col) for p in palabras_clave):
            return str(fila[col])
    return "N/R"

def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="REPORTE MEDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DATOS DEL PACIENTE", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"Nombre: {buscar_dato(paciente, ['NOM'])}", ln=True)
    pdf.cell(0, 8, txt=f"Documento: {buscar_dato(paciente, ['DOC'])} | RH: {buscar_dato(paciente, ['RH'])}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, fila in historial.iterrows():
        fecha = buscar_dato(fila, ['MARCA', 'FECHA'])
        pdf.cell(0, 8, txt=f"FECHA: {fecha}", ln=True)
        pdf.multi_cell(0, 6, txt=f"Tratamiento: {buscar_dato(fila, ['TRATAMIENTO'])}")
        pdf.cell(0, 2, txt="", ln=True, border='B')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Limpieza crucial de documentos
        for df in [p, h]:
            doc_col = next((c for c in df.columns if "DOC" in normalizar_texto(c)), None)
            if doc_col:
                df[doc_col] = df[doc_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 6. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 7. SECCIONES ---
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
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": cedula.strip(),
                    "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": condiciones, 
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        doc_col_p = next((c for c in df_p.columns if "DOC" in normalizar_texto(c)), "DOCUMENTO")
        paciente = df_p[df_p[doc_col_p] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            doc_col_h = next((c for c in df_h.columns if "DOC" in normalizar_texto(c)), "DOCUMENTO")
            h_p = df_h[df_h[doc_col_h] == id_bus].reset_index(drop=True)
            
            st.download_button("🖨️ Descargar PDF", data=generar_pdf(p, h_p), file_name=f"Reporte_{id_bus}.pdf")

            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {buscar_dato(p, ['NOM'])}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {buscar_dato(p, ['RH'])} | <b>Edad:</b> {buscar_dato(p, ['EDAD'])}</p>
                <div class="emergency-box">
                    <b>🚨 EMERGENCIA:</b> {buscar_dato(p, ['CONTACTO'])} - {buscar_dato(p, ['TEL'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <b>Evolución #{i+1} - Fecha: {buscar_dato(f, ['MARCA', 'FECHA'])}</b><br>
                    🩺 <b>Tratamiento:</b> {buscar_dato(f, ['TRATAMIENTO'])}<br>
                    💊 <b>Medicamentos:</b> {buscar_dato(f, ['MEDICAMENTOS'])}
                </div>
                """, unsafe_allow_html=True)

            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución")
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                pr = st.text_area("Procedimientos")
                if st.form_submit_button("GUARDAR"):
                    requests.post(URL_FORM_HISTORIAL, data={
                        "entry.2019369477": id_bus, "entry.611862537": t, 
                        "entry.2016051626": m, "entry.1088523869": pr
                    })
                    st.success("✅ Evolución guardada.")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.error("❌ Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    if df_p is not None: st.dataframe(df_p)
