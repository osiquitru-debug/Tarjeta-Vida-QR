import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA VISUAL (VERDE MENTA, MORADO, TURQUESA, TEXTO NEGRO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjeta del Paciente */
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }
    
    /* Tarjeta de Evolución */
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    
    /* Botones Turquesa */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }
    
    /* Botón Descarga PDF Azul */
    .stDownloadButton > button {
        background-color: #3182ce !important; color: white !important; 
        border-radius: 12px; font-weight: bold; width: 100%; border: none;
    }
    
    input, textarea, [data-baseweb="select"] > div { 
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE CORE (PDF Y CARGA) ---
def generar_pdf_hc(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "HISTORIAL CLINICO PERSONALIZADO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"PACIENTE: {paciente.get('NOMBRE', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"DOCUMENTO: {paciente.get('DOCUMENTO', 'N/A')}", ln=True)
    pdf.ln(5)
    for _, f in historial.iterrows():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, f"FECHA ATENCION: {f.get('MARCA TEMPORAL', 'S/F')}", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        texto = (f"VALORACION: {f.get('VALORACIÓN', 'N/A')}\n"
                 f"MOTIVO: {f.get('MOTIVO DE LA CONSULTA', 'N/A')}\n"
                 f"SIGNOS: Talla: {f.get('TALLA', 'N/A')}cm | Peso: {f.get('PESO', 'N/A')}kg | TA: {f.get('PRESIÓN ARTERIAL', 'N/A')}\n"
                 f"LABORATORIOS: {f.get('LABORATORIOS', 'N/A')}\n"
                 f"EPICRISIS: {f.get('EPICRISIS', 'N/A')}\n")
        pdf.multi_cell(0, 5, texto)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. SIDEBAR Y LOGOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>NAVEGACIÓN</h3>", unsafe_allow_html=True)
    if st.button("🔍 CONSULTA E HISTORIAL"): st.session_state.menu = "Consulta"
    if st.button("📊 BASE DE DATOS"): st.session_state.menu = "Base"
    if st.button("📝 REGISTRAR PACIENTE"): st.session_state.menu = "Registrar"

# Logo en cabecera principal
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. SECCIÓN CONSULTA ---
if st.session_state.menu == "Consulta":
    busq = st.text_input("Ingrese el Documento del Paciente para consultar").strip()
    
    if busq and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == busq]
        if not pac.empty:
            p = pac.iloc[0]
            h_p = df_h[df_h["DOCUMENTO"] == busq] if df_h is not None else pd.DataFrame()
            
            # MOSTRAR TARJETA DE PACIENTE (CON TODOS LOS DATOS)
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'SIN NOMBRE')}</h2>
                <hr style='border: 1px solid #e2e8f0; margin: 10px 0;'>
                <p><b>🆔 ID:</b> {busq} | <b>🩸 RH:</b> {p.get('RH', 'N/A')} | <b>🏥 EPS:</b> {p.get('EPS', 'N/A')}</p>
                <p><b>📱 CELULAR:</b> {p.get('CELULAR', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0;"><b>Nombre:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'Oscar Quintero')}</p>
                    <p style="margin:0;"><b>Teléfono:</b> {p.get('TELEFONO CONTACTO EMERGENCIA', '3225879465')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # BOTÓN PDF (SIEMPRE VISIBLE SI HAY PACIENTE)
            if not h_p.empty:
                pdf_bytes = generar_pdf_hc(p, h_p)
                st.download_button("📥 DESCARGAR HISTORIA CLÍNICA (PDF)", pdf_bytes, f"HC_{busq}.pdf", "application/pdf")

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN MÉDICA"):
                with st.form("h_form", clear_on_submit=True):
                    motivo = st.text_input("Motivo de la Consulta")
                    val = st.text_input("Valoración Profesional")
                    c1, c2, c3 = st.columns(3)
                    talla = c1.text_input("Talla (cm)")
                    peso = c2.text_input("Peso (kg)")
                    ta = c3.text_input("Tensión Arterial (TA)")
                    ant = st.text_area("Antecedentes")
                    meds = st.text_area("Medicamentos Prescritos")
                    labs = st.text_area("Laboratorios / Paraclínicos")
                    epi = st.text_area("Epicrisis / Notas Finales")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        payload = {
                            "entry.2019369477": busq, "entry.611862537": motivo, "entry.1275746503": val,
                            "entry.949747647": talla, "entry.2091389798": peso, "entry.889985940": ant,
                            "entry.2016051626": meds, "entry.882053172": ta, "entry.1088523869": labs, "entry.616774918": epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload)
                        st.success("Evolución guardada correctamente.")
                        st.cache_data.clear()
                        st.rerun()

            # MOSTRAR EVOLUCIONES (ORDEN CRONOLÓGICO INVERSO)
            st.markdown("### 🕒 Línea de Tiempo de Evoluciones")
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""
                <div class="evolution-card">
                    <p style="color:#2b6cb0; border-bottom:1px solid #eee;">📅 <b>FECHA: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                    <p>📋 <b>VALORACIÓN:</b> {f.get('VALORACIÓN', 'N/A')}</p>
                    <p>📏 <b>TALLA:</b> {f.get('TALLA', 'N/A')} | ⚖️ <b>PESO:</b> {f.get('PESO', 'N/A')} | 💓 <b>TA:</b> {f.get('PRESIÓN ARTERIAL', 'N/A')}</p>
                    <p>🧪 <b>LABORATORIOS:</b> {f.get('LABORATORIOS', 'N/A')}</p>
                    <p>📝 <b>EPICRISIS:</b> {f.get('EPICRISIS', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("No se encontró ningún paciente con ese documento.")

# SECCIONES ADICIONALES
elif st.session_state.menu == "Base":
    st.markdown("## Visualización de Base de Datos")
    if df_p is not None: st.subheader("Pacientes Registrados"); st.dataframe(df_p)
    if df_h is not None: st.subheader("Historial de Consultas"); st.dataframe(df_h)

elif st.session_state.menu == "Registrar":
    st.markdown("## Registro de Pacientes")
    st.info("Complete el registro a través del formulario de vinculación oficial.")
