import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (ESTÉTICA ORIGINAL RESTAURADA) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar color negro en textos para máxima claridad */
    label, p, h1, h2, h3, span, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 600 !important; 
    }
    
    /* Contenedor para centrar el logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
    }
    
    /* Tarjeta de Paciente NORMAL (Borde Turquesa) */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 25px;
    }
    
    /* Tarjeta de Paciente CRÍTICA (Roja Pulsante) */
    .alert-card {
        background-color: #fff5f5; padding: 25px; border-radius: 15px; 
        border: 2px solid #feb2b2; border-left: 15px solid #f56565; 
        margin-bottom: 25px;
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(245, 101, 101, 0); }
        100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); }
    }

    /* Tarjetas de Historial (Borde Azul) */
    .evolution-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
    }
    
    /* Caja de Emergencia (Dentro de la tarjeta de paciente) */
    .emergency-box { 
        background-color: #fff5f5; padding: 15px; border-radius: 10px; 
        border: 2px dashed #f56565; margin-top: 15px; 
    }
    
    /* Estilo de los Botones */
    div.stButton > button {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; 
        border: 2px solid #285e61; width: 100%; height: 3.5em; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #38b2ac !important; transform: scale(1.01); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES TÉCNICAS (PDF Y DATOS) ---
def crear_pdf(nombre, documento, rh, df_historial):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "HISTORIAL MEDICO - TARJETA VIDA", ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f" PACIENTE: {nombre}", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" DOCUMENTO: {documento}    |    RH: {rh}", ln=True)
    pdf.ln(10)
    
    for i, fila in df_historial.iterrows():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"FECHA: {fila.get('MARCA DE TIEMPO', 'N/A')}", ln=True)
        pdf.set_font("Arial", "", 10)
        contenido = f"TRATAMIENTO: {fila.get('TRATAMIENTO', 'N/A')}\nMEDICAMENTOS: {fila.get('MEDICAMENTOS', 'N/A')}\nPROCEDIMIENTOS: {fila.get('PROCEDIMIENTOS', 'N/A')}"
        pdf.multi_cell(0, 6, contenido)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

@st.cache_data(ttl=1)
def cargar_datos():
    URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        # Limpiar números de documento
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

# --- 4. CARGA INICIAL Y LOGO ---
df_p, df_h = cargar_datos()
URL_LOGO = "https://lh3.googleusercontent.com/d/1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"

# Logo centrado en la parte superior
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="200"></div>', unsafe_allow_html=True)

# Menú lateral
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown("## Menú")
    if st.button("🔍 Consultar Paciente"): st.session_state.menu = "Consulta"
    if st.button("📝 Registrar Nuevo"): st.session_state.menu = "Registrar"

# --- SECCIÓN REGISTRO ---
if st.session_state.menu == "Registrar":
    st.markdown("<h2 style='text-align: center;'>Registro de Paciente</h2>", unsafe_allow_html=True)
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        documento = c1.text_input("Número de Documento")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alertas = st.text_area("⚠️ Alertas / Condiciones Especiales")
        
        st.markdown("### Contacto de Emergencia")
        e_nom = st.text_input("Nombre de contacto")
        e_tel = st.text_input("Teléfono de contacto")
        
        if st.form_submit_button("GUARDAR EN BASE DE DATOS"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": documento.strip(),
                    "entry.162368130": rh, "entry.346363": alertas,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success("✅ Paciente registrado correctamente.")
                st.cache_data.clear()
            else: st.error("⚠️ Nombre y documento son obligatorios.")

# --- SECCIÓN CONSULTA ---
elif st.session_state.menu == "Consulta":
    id_buscar = st.text_input("🔍 Ingrese Documento para consultar...").strip()
    
    if id_buscar and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_buscar]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Lógica para mostrar Alerta Roja
            alerta_texto = str(p.get('CONDICIONES ESPECIALES', '')).strip()
            es_alerta = alerta_texto.lower() not in ['nan', '', 'ninguna', 'no', 'n/a']
            clase_css = "alert-card" if es_alerta else "medical-card"
            
            st.markdown(f"""
            <div class="{clase_css}">
                <h2 style="margin:0;">{'⚠️' if es_alerta else '👤'} {p.get('NOMBRE', 'N/A')}</h2>
                {f'<p style="color:#c53030; font-size:1.2em; margin-top:10px;"><b>ALERTA MÉDICA: {alerta_texto}</b></p>' if es_alerta else ''}
                <hr style="border: 0.5px solid #eee; margin: 15px 0;">
                <p><b>DOCUMENTO:</b> {id_buscar}  |  <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0; font-size:1.1em;">{p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'N/A')} — {p.get('TELÉFONO CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Historial y PDF
            if df_h is not None:
                historial_p = df_h[df_h["DOCUMENTO"] == id_buscar]
                
                if not historial_p.empty:
                    pdf_bytes = crear_pdf(p.get('NOMBRE'), id_buscar, p.get('RH'), historial_p)
                    st.download_button("📥 DESCARGAR HISTORIAL COMPLETO (PDF)", data=pdf_bytes, file_name=f"Historial_{id_buscar}.pdf", mime="application/pdf")
                
                # Nueva Evolución
                with st.form("nueva_evolucion", clear_on_submit=True):
                    st.markdown("### ✍️ Registrar Evolución")
                    trat = st.text_input("Tratamiento Actual")
                    meds = st.text_area("Medicamentos")
                    proc = st.text_area("Procedimientos")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        pay_h = {"entry.2019369477": id_buscar, "entry.611862537": trat, "entry.2016051626": meds, "entry.1088523869": proc}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay_h)
                        st.cache_data.clear()
                        st.rerun()

                # Mostrar historial en tarjetas azules
                st.markdown("### 📅 Evoluciones Previas")
                if not historial_p.empty:
                    for i in range(len(historial_p)-1, -1, -1): # De más reciente a más antiguo
                        f = historial_p.iloc[i]
                        st.markdown(f"""
                        <div class="evolution-card">
                            <p style="color: #2b6cb0; font-size:1.1em;"><b>REGISTRO: {f.get('MARCA DE TIEMPO', 'N/A')}</b></p>
                            <p><b>🩺 TRATAMIENTO:</b> {f.get('TRATAMIENTO', 'N/A')}</p>
                            <p><b>💊 MEDICAMENTOS:</b> {f.get('MEDICAMENTOS', 'N/A')}</p>
                            <p><b>🔬 PROCEDIMIENTOS:</b> {f.get('PROCEDIMIENTOS', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay evoluciones registradas para este paciente.")
        else:
            st.error("❌ El paciente no se encuentra en el sistema.")
