import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA VISUAL (VERDE MENTA, MORADO, TURQUESA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
    
    /* Tarjetas */
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 2px dashed #feb2b2; margin-top: 10px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar Morado */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    
    /* Botones Turquesa Principales */
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
    
    input, textarea { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE CARGA Y BÚSQUEDA ---
def buscar_en_fila(fila, terminos):
    for col in fila.index:
        if any(t in col.upper() for t in terminos):
            return fila[col]
    return "N/A"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        p.columns = [c.strip().upper() for c in p.columns]
        h.columns = [c.strip().upper() for c in h.columns]
        # Estandarizar Documentos
        for df in [p, h]:
            c_doc = next((c for c in df.columns if "DOC" in c or "ID" in c), None)
            if c_doc: df[c_doc] = df[c_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. MENÚ LATERAL (ORDEN: REGISTRO, CONSULTA, BASE DE DATOS) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 REGISTRO"): st.session_state.menu = "Registro"
    if st.button("🔍 CONSULTA"): st.session_state.menu = "Consulta"
    if st.button("📊 BASE DE DATOS"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registro":
    st.markdown("<h2 style='text-align: center;'>Registro de Nuevo Paciente</h2>", unsafe_allow_html=True)
    st.info("Para vincular un nuevo paciente, complete el formulario de registro oficial.")
    # Aquí puedes insertar un link o un iframe del Form de Google de Registro si lo deseas.

elif st.session_state.menu == "Consulta":
    busq = st.text_input("Documento del Paciente").strip()
    if busq and df_p is not None:
        c_doc_p = next((c for c in df_p.columns if "DOC" in c or "ID" in c), None)
        pac = df_p[df_p[c_doc_p] == busq] if c_doc_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            c_doc_h = next((c for c in df_h.columns if "DOC" in c or "ID" in c), None)
            h_p = df_h[df_h[c_doc_h] == busq] if c_doc_h else pd.DataFrame()
            
            # Tarjeta Paciente
            st.markdown(f"""<div class="medical-card">
                <h2>👤 {buscar_en_fila(p, ["NOM"])}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {buscar_en_fila(p, ["RH"])} | <b>EPS:</b> {buscar_en_fila(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 EMERGENCIA:</b> {buscar_en_fila(p, ["CONTACTO"])}</p>
                    <p style="margin:0;"><b>Tel:</b> {buscar_en_fila(p, ["TELEFONO"])}</p>
                </div></div>""", unsafe_allow_html=True)

            # Botón PDF
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "REPORTE MEDICO", ln=True)
            st.download_button("📥 DESCARGAR PDF HISTORIAL", pdf.output(dest='S').encode('latin-1'), f"HC_{busq}.pdf")

            # Formulario Evolución (Orden del Sheet 1-9)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    mot = st.text_input("1. Motivo de la Consulta")
                    c1, c2, c3 = st.columns(3)
                    tll = c1.text_input("2. Talla (cm)")
                    pes = c2.text_input("3. Peso (kg)")
                    ten = c3.text_input("4. Presión Arterial (TA)")
                    ant = st.text_area("5. Antecedentes Médicos")
                    med = st.text_area("6. Medicamentos")
                    lab = st.text_area("7. Laboratorios")
                    val = st.text_input("8. Valoración Professional")
                    epi = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        pay = {"entry.2019369477": busq, "entry.611862537": mot, "entry.949747647": tll, "entry.2091389798": pes, "entry.882053172": ten, "entry.889985940": ant, "entry.2016051626": med, "entry.1088523869": lab, "entry.1275746503": val, "entry.616774918": epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            # Tarjetas de Evolución (Mapeo por Radar de Columnas)
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""<div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {buscar_en_fila(f, ["MARCA", "FECHA"])}</b></p>
                    <p><b>🩺 MOTIVO:</b> {buscar_en_fila(f, ["MOTIVO"])}</p>
                    <p>📏 <b>TALLA:</b> {buscar_en_fila(f, ["TALLA"])} | ⚖️ <b>PESO:</b> {buscar_en_fila(f, ["PESO"])} | 💓 <b>TA:</b> {buscar_en_fila(f, ["PRESIÓN", "TENSIÓN"])}</p>
                    <p>💊 <b>MEDICAMENTOS:</b> {buscar_en_fila(f, ["MEDICAMENTOS"])} | 🧪 <b>LABORATORIOS:</b> {buscar_en_fila(f, ["LABORATORIO"])}</p>
                    <p>📋 <b>VALORACIÓN:</b> {buscar_en_fila(f, ["VALORACIÓN", "VALORACION"])}</p>
                    <p>📝 <b>EPICRISIS:</b> {buscar_en_fila(f, ["EPICRISIS"])}</p>
                </div>""", unsafe_allow_html=True)
        else: st.warning("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.markdown("<h2 style='text-align: center;'>Base de Datos General</h2>", unsafe_allow_html=True)
    if df_p is not None:
        st.subheader("📋 Listado de Pacientes")
        st.dataframe(df_p, use_container_width=True)
    if df_h is not None:
        st.subheader("🕒 Historial de Evoluciones")
        st.dataframe(df_h, use_container_width=True)
