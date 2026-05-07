import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Historial Médico", layout="centered", page_icon="🩺")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #000;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; border-left: 5px solid #63b3ed; margin-bottom: 10px;
    }
    .emergency-box { 
        background-color: #fff5f5; padding: 10px; border-radius: 8px; 
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. URLs ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
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
    except:
        return None, None

# --- 4. GENERACIÓN DE PDF ---
def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "HISTORIA CLINICA - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # Datos del Paciente
    pdf.set_fill_color(230, 245, 240)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, f" PACIENTE: {paciente.get('NOMBRE', 'N/R')}", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 7, txt=f"Documento: {paciente.get('DOCUMENTO')}\nRH: {paciente.get('RH')}\nEPS: {paciente.get('EPS')}")
    
    # Evoluciones (Basado solo en los campos del formulario)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, " REGISTROS DE EVOLUCION", ln=True, fill=True)
    
    for _, fila in historial.iterrows():
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 7, f"FECHA: {fila.get('MARCA TEMPORAL', 'S/F')}", ln=True)
        pdf.set_font("Arial", '', 9)
        # Solo campos del Sheet que coinciden con el form
        texto = (f"Diagnóstico: {fila.get('DIAGNOSTICO', 'N/R')}\n"
                 f"Tratamiento: {fila.get('TRATAMIENTO', 'N/R')}\n"
                 f"Medicamentos: {fila.get('MEDICAMENTOS', 'N/R')}\n"
                 f"Evolución: {fila.get('EVOLUCION CLINICA', 'N/R')}")
        pdf.multi_cell(0, 5, texto.encode('latin-1', 'replace').decode('latin-1'))
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
    return pdf.output(dest='S')

# --- 5. LÓGICA DE INTERFAZ ---
df_p, df_h = cargar_datos()

st.title("🩺 Gestión de Evoluciones")

id_bus = st.text_input("Buscar Paciente (Documento)").strip()

if id_bus and df_p is not None:
    paciente_rows = df_p[df_p["DOCUMENTO"] == id_bus]
    
    if not paciente_rows.empty:
        p = paciente_rows.iloc[0]
        # Filtrar historial del paciente
        h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
        
        # Tarjeta resumen paciente
        st.markdown(f"""
        <div class="medical-card">
            <h3 style='margin:0;'>👤 {p.get('NOMBRE', 'N/A')}</h3>
            <p style='margin:0;'>ID: {id_bus} | RH: {p.get('RH', 'N/A')} | EPS: {p.get('EPS', 'N/A')}</p>
            <div class="emergency-box">
                🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA', 'S/D')} - {p.get('TELEFONO CONTACTO EMERGENCIA', 'S/D')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button("📥 Descargar PDF", data=generar_pdf(p, h_p), file_name=f"HC_{id_bus}.pdf")

        # Formulario de Evolución (Campos exactos del link proporcionado)
        with st.expander("📝 REGISTRAR NUEVA ENTRADA"):
            with st.form("form_evo", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    # Basado en tus entries del link
                    tratamiento = st.text_input("Tratamiento (entry.611862537)")
                    procedimientos = st.text_area("Procedimientos (entry.1088523869)")
                    evolucion_clinica = st.text_area("Evolución Clínica (entry.1275746503)")
                    notas_enfermeria = st.text_area("Notas de Enfermería (entry.949747647)")
                    observaciones = st.text_input("Observaciones (entry.2091389798)")
                with col2:
                    diagnostico = st.text_area("Diagnóstico (entry.889985940)")
                    medicamentos = st.text_area("Medicamentos (entry.2016051626)")
                    recomendaciones = st.text_area("Recomendaciones (entry.882053172)")
                    examenes = st.text_input("Exámenes (entry.616774918)")
                    adicional = st.text_input("Dato Adicional (entry.2019369477)", value=id_bus, disabled=True)

                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    payload = {
                        "entry.2019369477": id_bus,
                        "entry.1088523869": procedimientos,
                        "entry.611862537": tratamiento,
                        "entry.1275746503": evolucion_clinica,
                        "entry.949747647": notas_enfermeria,
                        "entry.2091389798": observaciones,
                        "entry.889985940": diagnostico,
                        "entry.2016051626": medicamentos,
                        "entry.882053172": recomendaciones,
                        "entry.616774918": examenes
                    }
                    try:
                        requests.post(URL_FORM_HISTORIAL, data=payload)
                        st.success("✅ Datos enviados. Actualizando...")
                        st.cache_data.clear()
                        st.rerun()
                    except:
                        st.error("Error de conexión.")

        # Visualización de Evoluciones (Tarjetas que coinciden con el Sheet)
        st.subheader("📋 Evoluciones Registradas")
        if not h_p.empty:
            for _, fila in h_p.sort_index(ascending=False).iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small><b>📅 Fecha: {fila.get('MARCA TEMPORAL', 'S/F')}</b></small><br>
                        <b>🩺 Diagnóstico:</b> {fila.get('DIAGNOSTICO', 'N/R')}<br>
                        <b>💊 Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/R')}<br>
                        <b>📋 Evolución:</b> {fila.get('EVOLUCION CLINICA', 'N/R')}<br>
                        <hr style='margin:5px 0; border:0; border-top:1px solid #eee;'>
                        <small>📝 <b>Obs:</b> {fila.get('OBSERVACIONES', 'N/R')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No hay evoluciones previas para este paciente.")
    else:
        st.warning("Paciente no encontrado.")
