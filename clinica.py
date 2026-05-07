import streamlit as st
import pandas as pd
import requests
import unicodedata
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA DE ALTO CONTRASTE (VERDE, MORADO, TURQUESA) ---
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

# --- 3. FUNCIONES TÉCNICAS (LIMPIEZA EXTREMA) ---
def limpiar_id(texto):
    """Convierte cualquier ID (123, 123.0, ' 123 ') en una cadena limpia '123'."""
    if pd.isna(texto): return ""
    txt = str(texto).strip()
    if txt.endswith('.0'): txt = txt[:-2]
    return txt

def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def obtener_dato(fila, palabras_clave):
    for col in fila.index:
        if any(p in normalizar(col) for p in palabras_clave):
            return str(fila[col])
    return "N/R"

def generar_pdf(paciente, evoluciones, documento):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="HISTORIAL CLÍNICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"PACIENTE: {obtener_dato(paciente, ['NOM'])}", ln=True)
    pdf.cell(200, 10, txt=f"DOCUMENTO: {documento}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(200, 10, txt="REGISTROS DE EVOLUCIÓN", ln=True)
    pdf.set_font("Arial", '', 10)
    for _, evo in evoluciones.iterrows():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 7, txt=f"FECHA: {obtener_dato(evo, ['MARCA', 'FECHA'])}", ln=True)
        pdf.set_font("Arial", '', 10)
        msg = f"MOTIVO: {obtener_dato(evo, ['MOTIVO'])}\nVALORACION: {obtener_dato(evo, ['VALORAC'])}\nEPICRISIS: {obtener_dato(evo, ['EPICRIS'])}"
        pdf.multi_cell(0, 7, txt=msg)
        pdf.cell(0, 0, "", "T")
    return pdf.output(dest='S').encode('latin-1', 'replace')

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url_base = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url_base}&sheet=pacientes")
        h = pd.read_csv(f"{url_base}&sheet=historial")
        
        # Aplicamos la limpieza extrema a la columna de documento
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in normalizar(c)), None)
            if c_doc:
                df[c_doc] = df[c_doc].apply(limpiar_id)
        return p, h
    except Exception as e:
        st.error(f"Error cargando Sheets: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🩺</h1>", unsafe_allow_html=True)
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIÓN CONSULTA (MOTOR CORREGIDO) ---
if st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)
    busq = limpiar_id(st.text_input("Ingrese Documento del Paciente"))
    
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in normalizar(c)), "DOCUMENTO")
        # Búsqueda sobre columna ya limpia
        pac = df_p[df_p[c_doc_p] == busq]
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in normalizar(c)), "DOCUMENTO")
            h_p = df_h[df_h[c_doc_h] == busq] if df_h is not None else pd.DataFrame()

            # Tarjeta Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {obtener_dato(p, ["NOM"])}</h2>
                <p><b>DOCUMENTO:</b> {busq} | <b>RH:</b> {obtener_dato(p, ["RH"])} | <b>EPS:</b> {obtener_dato(p, ["EPS"])}</p>
            </div>
            """, unsafe_allow_html=True)

            # Botón Descarga PDF
            if not h_p.empty:
                pdf_data = generar_pdf(p, h_p, busq)
                st.download_button("📥 DESCARGAR HISTORIAL (PDF)", data=pdf_data, file_name=f"Historial_{busq}.pdf", mime="application/pdf")

            # Formulario Evolución (Orden del Link)
            with st.expander("✍️ AGREGAR EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    f1 = st.text_input("1. Motivo de la Consulta")
                    f2 = st.text_area("2. Valoración")
                    c1, c2, c3 = st.columns(3)
                    f3 = c1.text_input("3. Talla")
                    f4 = c2.text_input("4. Peso")
                    f5 = c3.text_input("5. TA")
                    f6 = st.text_area("6. Antecedentes")
                    f7 = st.text_area("7. Medicamentos")
                    f8 = st.text_area("8. Laboratorios")
                    f9 = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR REGISTRO"):
                        payload = {
                            "entry.2019369477": busq, "entry.611862537": f1, "entry.1275746503": f2,
                            "entry.949747647": f3, "entry.2091389798": f4, "entry.889985940": f6,
                            "entry.2016051626": f7, "entry.882053172": f5, "entry.1088523869": f8, "entry.616774918": f9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=payload)
                        st.success("✅ Guardado correctamente."); st.cache_data.clear(); st.rerun()

            # Tarjetas de historial
            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; font-size:12px;">📅 {obtener_dato(f, ["MARCA", "FECHA"])}</p>
                    <p><b>🩺 MOTIVO:</b> {obtener_dato(f, ["MOTIVO"])}</p>
                    <p><b>📋 VALORACIÓN:</b> {obtener_dato(f, ["VALORAC"])}</p>
                    <p><b>📝 EPICRISIS:</b> {obtener_dato(f, ["EPICRIS"])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"❌ El documento '{busq}' no existe en la base de datos de pacientes.")

# --- 6. SECCIÓN BASE DE DATOS ---
elif st.session_state.menu == "Base":
    st.markdown("### 📊 Datos en Tiempo Real")
    if df_p is not None: st.write("**Pacientes registrados:**", df_p)
    if df_h is not None: st.write("**Historial de evoluciones:**", df_h)
