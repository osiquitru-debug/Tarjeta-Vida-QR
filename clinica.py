import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], select, input, textarea {
        background-color: #ffffff !important; color: #000000 !important;
    }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold; margin-top: 10px;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; border-left: 5px solid #63b3ed;
        margin-bottom: 10px; color: #2d3748;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        # Cargar hojas y limpiar nombres de columnas
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        # Crear llave de búsqueda DOC_KEY (primera columna que parezca documento)
        def fix_doc(df):
            for col in df.columns:
                if 'DOC' in col or 'CEDULA' in col or 'IDENTIFICACION' in col:
                    df['DOC_KEY'] = df[col].astype(str).str.split('.').str[0].str.strip()
                    return df
            df['DOC_KEY'] = df.iloc[:, 1].astype(str).str.split('.').str[0].str.strip()
            return df
            
        return fix_doc(p), fix_doc(h)
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 3. FUNCIÓN PDF MEJORADA ---
def generar_pdf_completo(p, h_p):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Paciente
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 128, 128)
    pdf.cell(0, 10, "HISTORIA CLÍNICA - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"PACIENTE: {p.get('NOMBRE', 'N/A')}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Documento: {p.get('DOC_KEY')} | Edad: {p.get('EDAD')} | RH: {p.get('RH')}", ln=True)
    pdf.cell(0, 6, f"EPS: {p.get('EPS')} | Tel: {p.get('CELULAR')}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Evoluciones
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "REGISTROS DE EVOLUCIÓN", ln=True)
    
    for _, fila in h_p.iterrows():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, f"FECHA: {fila.get('MARCA TEMPORAL')}", ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        
        campos = [
            ("Valoración", "VALORACION"), ("Motivo", "MOTIVO DE LA CONSULTA"),
            ("Talla", "TALLA"), ("Peso", "PESO"), ("Presión", "PRESION ARTERIAL"),
            ("Antecedentes", "ANTECEDENTES MEDICOS"), ("Medicamentos", "MEDICAMENTOS"),
            ("Laboratorios", "LABORATORIOS - PROCEDIMIENTOS"), ("Epicrisis", "EPICRISIS")
        ]
        
        for label, col in campos:
            val = str(fila.get(col, 'N/R'))
            if val != 'nan' and val != 'N/R':
                pdf.set_font("Arial", 'B', 8)
                pdf.write(5, f"{label}: ")
                pdf.set_font("Arial", '', 8)
                pdf.write(5, f"{val}\n")
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INTERFAZ ---
st.sidebar.title("🩺 Menú")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Registro", "Consulta"])

if opcion == "Consulta":
    st.title("🔍 Consulta de Paciente")
    busqueda = st.text_input("Ingrese Documento").strip()
    
    if busqueda and df_p is not None:
        p_row = df_p[df_p["DOC_KEY"] == busqueda]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            # TARJETA DE PACIENTE COMPLETA
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <hr>
                <table style='width:100%; border:none;'>
                    <tr><td><b>Documento:</b> {busqueda}</td><td><b>Edad:</b> {p.get('EDAD')}</td></tr>
                    <tr><td><b>EPS:</b> {p.get('EPS')}</td><td><b>RH:</b> {p.get('RH')}</td></tr>
                    <tr><td><b>Celular:</b> {p.get('CELULAR')}</td><td><b>Tipo:</b> {p.get('TIPO DE DOCUMENTO')}</td></tr>
                </table>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA', 'No asignado')}<br>
                    📞 Tel: {p.get('TELEFONO CONTACTO EMERGENCIA', 'No asignado')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FORMULARIO EVOLUCIÓN (10 CAMPOS)
            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_full"):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo"); v3 = st.text_input("3. Talla")
                        v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión Arterial")
                    with c2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR HISTORIAL"):
                        # (Aquí iría el requests.post a tu Google Form)
                        st.success("Registro enviado.")

            # HISTORIAL Y PDF
            st.subheader("📋 Evoluciones Previas")
            if df_h is not None:
                h_p = df_h[df_h["DOC_KEY"] == busqueda].sort_index(ascending=False)
                if not h_p.empty:
                    # Botón PDF
                    pdf_bytes = generar_pdf_completo(p, h_p)
                    st.download_button("📥 Descargar Historia Clínica PDF", pdf_bytes, f"HC_{busqueda}.pdf", "application/pdf")
                    
                    for _, fila in h_p.iterrows():
                        with st.container():
                            st.markdown(f"""
                            <div class="evo-card">
                                <small>📅 {fila.get('MARCA TEMPORAL')}</small><br>
                                <b>Valoración:</b> {fila.get('VALORACION')}<br>
                                <b>Motivo:</b> {fila.get('MOTIVO DE LA CONSULTA')}<br>
                                <b>Medicamentos:</b> {fila.get('MEDICAMENTOS')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No hay evoluciones registradas.")
        else:
            st.error("Paciente no encontrado.")
