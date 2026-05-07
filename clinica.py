import streamlit as st
import pandas as pd
import requests
import unicodedata
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Estética de alto contraste: Verde Menta, Morado y Turquesa
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #cbd5e0; border-left: 12px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 4px solid #d8b4fe; }
    
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 15px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.5em; width: 100%; text-transform: uppercase;
    }

    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #a2d2ff !important; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIONES DE LIMPIEZA Y PROCESAMIENTO ---
def limpiar_id(valor):
    if pd.isna(valor): return ""
    v = str(valor).strip()
    if v.endswith('.0'): v = v[:-2]
    return v

def normalizar_col(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def obtener_valor(fila, keywords):
    for col in fila.index:
        if any(k in normalizar_col(col) for k in keywords):
            return str(fila[col])
    return "N/R"

def generar_pdf(paciente, evoluciones, doc_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE CLÍNICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"PACIENTE: {obtener_valor(paciente, ['NOM'])}", ln=True)
    pdf.cell(200, 10, txt=f"DOCUMENTO: {doc_id}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="HISTORIAL DE EVOLUCIONES", ln=True)
    pdf.set_font("Arial", '', 10)
    for _, f in evoluciones.iterrows():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 7, txt=f"FECHA: {obtener_valor(f, ['MARCA', 'FECHA'])}", ln=True)
        pdf.set_font("Arial", '', 10)
        texto = f"MOTIVO: {obtener_valor(f, ['MOTIVO'])}\nVALORACION: {obtener_valor(f, ['VALORAC'])}\nEPICRISIS: {obtener_valor(f, ['EPICRIS'])}"
        pdf.multi_cell(0, 7, txt=texto)
        pdf.cell(0, 0, "", "T")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_todo():
    try:
        base = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{base}&sheet=pacientes")
        h = pd.read_csv(f"{base}&sheet=historial")
        for df in [p, h]:
            col_id = next((c for c in df.columns if "DOC" in normalizar_col(c)), None)
            if col_id: df[col_id] = df[col_id].apply(limpiar_id)
        return p, h
    except: return None, None

df_p, df_h = cargar_todo()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🩺 MENÚ</h2>", unsafe_allow_html=True)
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIÓN: REGISTRAR PACIENTE (AQUÍ ESTÁ LA PARTE QUE FALTABA) ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>📝 Registro de Nuevo Paciente</h1>", unsafe_allow_html=True)
    with st.form("form_registro_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            r_nombre = st.text_input("Nombre Completo")
            r_tipo_doc = st.selectbox("Tipo de Documento", ["Cédula", "T.I.", "C.E.", "Pasaporte"])
            r_documento = st.text_input("Número de Documento")
        with col2:
            r_celular = st.text_input("Celular")
            r_rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            r_eps = st.text_input("EPS")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        r_e_nombre = st.text_input("Nombre del contacto de emergencia")
        r_e_tel = st.text_input("Teléfono del contacto")

        if st.form_submit_button("GUARDAR PACIENTE"):
            if r_documento and r_nombre:
                payload_p = {
                    "entry.346175428": r_nombre,
                    "entry.1650757004": r_tipo_doc,
                    "entry.1302424820": r_documento.strip(),
                    "entry.1043165037": r_celular,
                    "entry.1172011247": r_eps,
                    "entry.162368130": r_rh,
                    "entry.1892763134": r_e_nombre,
                    "entry.2011749615": r_e_tel
                }
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload_p)
                st.success(f"✅ Paciente {r_nombre} registrado con éxito.")
                st.cache_data.clear()
            else:
                st.warning("⚠️ Por favor complete Nombre y Documento.")

# --- 6. SECCIÓN: CONSULTA E HISTORIAL ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>🔍 Consulta Médica</h1>", unsafe_allow_html=True)
    busq = limpiar_id(st.text_input("Ingrese Documento del Paciente"))
    
    if busq and df_p is not None:
        col_doc_p = next((c for c in df_p.columns if "DOC" in normalizar_col(c)), "DOCUMENTO")
        paciente_row = df_p[df_p[col_doc_p] == busq]
        
        if not paciente_row.empty:
            p = paciente_row.iloc[0]
            col_doc_h = next((c for c in df_h.columns if "DOC" in normalizar_col(c)), "DOCUMENTO")
            h_p = df_h[df_h[col_doc_h] == busq] if df_h is not None else pd.DataFrame()

            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {obtener_valor(p, ["NOM"])}</h2>
                <p><b>ID:</b> {busq} | <b>RH:</b> {obtener_valor(p, ["RH"])} | <b>EPS:</b> {obtener_valor(p, ["EPS"])}</p>
            </div>
            """, unsafe_allow_html=True)

            if not h_p.empty:
                pdf_bytes = generar_pdf(p, h_p, busq)
                st.download_button("📥 DESCARGAR HISTORIAL PDF", data=pdf_bytes, file_name=f"Historial_{busq}.pdf", mime="application/pdf")

            with st.expander("✍️ AGREGAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    f1 = st.text_input("1. Motivo de Consulta")
                    f2 = st.text_area("2. Valoración")
                    c1, c2, c3 = st.columns(3)
                    f3, f4, f5 = c1.text_input("3. Talla"), c2.text_input("4. Peso"), c3.text_input("5. TA")
                    f6, f7, f8, f9 = st.text_area("6. Antecedentes"), st.text_area("7. Medicamentos"), st.text_area("8. Laboratorios"), st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR REGISTRO"):
                        payload_h = {
                            "entry.2019369477": busq, "entry.611862537": f1, "entry.1275746503": f2,
                            "entry.949747647": f3, "entry.2091389798": f4, "entry.889985940": f6,
                            "entry.2016051626": f7, "entry.882053172": f5, "entry.1088523869": f8, "entry.616774918": f9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=payload_h)
                        st.success("✅ Evolución guardada."); st.cache_data.clear(); st.rerun()

            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; font-size:12px;">📅 {obtener_valor(f, ["MARCA", "FECHA"])}</p>
                    <p><b>🩺 MOTIVO:</b> {obtener_valor(f, ["MOTIVO"])}</p>
                    <p><b>📋 VALORACIÓN:</b> {obtener_valor(f, ["VALORAC"])}</p>
                    <p><b>📝 EPICRISIS:</b> {obtener_valor(f, ["EPICRIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"❌ El documento '{busq}' no existe en la base de datos.")

# --- 7. SECCIÓN: BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.markdown("### 📊 Datos Registrados")
    st.write("**Pacientes en Sistema:**", df_p)
    st.write("**Historial de Evoluciones:**", df_h)
    
