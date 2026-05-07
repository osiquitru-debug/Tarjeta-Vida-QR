import streamlit as st
import pandas as pd
import requests
import unicodedata
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 20px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 15px; border-radius: 10px; border: 2px dashed #feb2b2; margin-top: 10px; }
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

# --- 3. FUNCIONES DE DATOS Y PDF ---
def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def obtener_dato(fila, palabras_clave):
    for col in fila.index:
        if any(p in normalizar(col) for p in palabras_clave):
            return str(fila[col])
    return "N/A"

def generar_pdf(paciente, evoluciones, documento):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="HISTORIAL CLÍNICO - TARJETA VIDA", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"PACIENTE: {obtener_dato(paciente, ['NOM'])}", ln=True)
    pdf.cell(200, 10, txt=f"DOCUMENTO: {documento}", ln=True)
    pdf.cell(200, 10, txt=f"EPS: {obtener_dato(paciente, ['EPS'])} | RH: {obtener_dato(paciente, ['RH'])}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="EVOLUCIONES", ln=True)
    
    pdf.set_font("Arial", '', 10)
    for _, evo in evoluciones.iterrows():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 7, txt=f"FECHA: {obtener_dato(evo, ['MARCA', 'FECHA'])}", ln=True, fill=False)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 7, txt=f"MOTIVO: {obtener_dato(evo, ['MOTIVO'])}\nVALORACIÓN: {obtener_dato(evo, ['VALORAC'])}\nSIGNOS: Talla {obtener_dato(evo, ['TALLA'])}cm - Peso {obtener_dato(evo, ['PESO'])}kg - TA {obtener_dato(evo, ['PRESION'])}\nEPICRISIS: {obtener_dato(evo, ['EPICRIS'])}")
        pdf.cell(0, 0, "", "T") # Línea divisoria
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url_base = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url_base}&sheet=pacientes")
        h = pd.read_csv(f"{url_base}&sheet=historial")
        # LIMPIEZA CRÍTICA DE DOCUMENTOS (Evita el error de "Paciente no encontrado")
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if c_doc:
                df[c_doc] = df[c_doc].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🩺 MENÚ</h2>", unsafe_allow_html=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. LÓGICA DE CONSULTA E HISTORIAL ---
if st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>🔍 Historial Clínico</h1>", unsafe_allow_html=True)
    busq = st.text_input("Ingrese Documento para buscar").strip()
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in normalizar(c)), "DOCUMENTO")
        # Búsqueda exacta
        pac = df_p[df_p[c_doc_p] == busq]
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in normalizar(c)), "DOCUMENTO")
            h_p = df_h[df_h[c_doc_h] == busq] if df_h is not None else pd.DataFrame()

            # Tarjeta Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {obtener_dato(p, ["NOM"])}</h2>
                <p>DOC: {busq} | RH: {obtener_dato(p, ["RH"])} | EPS: {obtener_dato(p, ["EPS"])}</p>
            </div>
            """, unsafe_allow_html=True)

            # Botón de Descarga PDF
            if not h_p.empty:
                pdf_bytes = generar_pdf(p, h_p, busq)
                st.download_button(label="📥 DESCARGAR HISTORIAL PDF", data=pdf_bytes, file_name=f"Historial_{busq}.pdf", mime="application/pdf")

            # Formulario Nueva Evolución
            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    f_motivo = st.text_input("1. Motivo de la Consulta")
                    f_val = st.text_area("2. Valoración")
                    c1, c2, c3 = st.columns(3)
                    f_talla = c1.text_input("3. Talla")
                    f_peso = c2.text_input("4. Peso")
                    f_pa = c3.text_input("5. Presión Arterial")
                    f_ant = st.text_area("6. Antecedentes")
                    f_meds = st.text_area("7. Medicamentos")
                    f_lab = st.text_area("8. Laboratorios")
                    f_epi = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR DATOS"):
                        payload = {
                            "entry.2019369477": busq, "entry.611862537": f_motivo, "entry.1275746503": f_val,
                            "entry.949747647": f_talla, "entry.2091389798": f_peso, "entry.889985940": f_ant,
                            "entry.2016051626": f_meds, "entry.882053172": f_pa, "entry.1088523869": f_lab, "entry.616774918": f_epi
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=payload)
                        st.success("✅ Evolución Guardada"); st.cache_data.clear(); st.rerun()

            # Tarjetas de Evolución
            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; font-size:12px;">📅 {obtener_dato(f, ["MARCA", "FECHA"])}</p>
                    <p><b>🩺 MOTIVO:</b> {obtener_dato(f, ["MOTIVO"])}</p>
                    <p><b>📋 VALORACIÓN:</b> {obtener_dato(f, ["VALORAC"])}</p>
                    <p><b>📏 SIGNOS:</b> Talla: {obtener_dato(f, ["TALLA"])} | Peso: {obtener_dato(f, ["PESO"])} | TA: {obtener_dato(f, ["PRESION"])}</p>
                    <p><b>📝 EPICRISIS:</b> {obtener_dato(f, ["EPICRIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"❌ Paciente con documento {busq} no encontrado. Verifique espacios o el número en el Sheet.")

elif st.session_state.menu == "Base":
    st.markdown("### 📊 Base de Datos")
    if df_p is not None: st.write("Pacientes", df_p)
    if df_h is not None: st.write("Historial", df_h)
