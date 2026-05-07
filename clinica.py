import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA BLINDADA ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .logo-container { display: flex; justify-content: center; margin: 10px 0; }
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
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    .stSidebar button { 
        width: 100%; background-color: #ffffff !important; color: #000000 !important; 
        border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; 
    }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; 
        height: 3.8em; width: 100%; text-transform: uppercase;
    }
    .stDownloadButton > button {
        background-color: #3182ce !important; color: white !important; 
        border-radius: 12px; font-weight: bold; width: 100%; border: none;
    }
    input, textarea { background-color: #ffffff !important; border: 2px solid #a2d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RADAR DE COLUMNAS (Para que coincida con el Sheet 100%) ---
def buscar_dato(fila, palabras):
    """Busca en una fila el valor de la columna que contenga ciertas palabras clave."""
    for col in fila.index:
        if any(p in col.upper() for p in palabras):
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
        # Limpiar documentos para que la búsqueda no falle
        for df in [p, h]:
            col_doc = next((c for c in df.columns if "DOC" in c or "ID" in c), None)
            if col_doc:
                df[col_doc] = df[col_doc].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 4. MENÚ LATERAL (ORDEN: REGISTRO, CONSULTA, BASE) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="100"></div>', unsafe_allow_html=True)
    if st.button("📝 REGISTRO"): st.session_state.menu = "Registrar"
    if st.button("🔍 CONSULTA"): st.session_state.menu = "Consulta"
    if st.button("📊 BASE DE DATOS"): st.session_state.menu = "Base"

st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="150"></div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registrar":
    st.markdown("<h2 style='text-align: center;'>Registro de Pacientes</h2>", unsafe_allow_html=True)
    st.info("Formulario de ingreso para nuevos pacientes.")

elif st.session_state.menu == "Consulta":
    busq = st.text_input("Ingrese Documento del Paciente").strip()
    
    if busq and df_p is not None:
        col_doc_p = next((c for c in df_p.columns if "DOC" in c or "ID" in c), None)
        pac = df_p[df_p[col_doc_p] == busq] if col_doc_p else pd.DataFrame()
        
        if not pac.empty:
            p = pac.iloc[0]
            col_doc_h = next((c for c in df_h.columns if "DOC" in c or "ID" in c), None)
            h_p = df_h[df_h[col_doc_h] == busq] if col_doc_h else pd.DataFrame()
            
            # Tarjeta Paciente
            st.markdown(f"""<div class="medical-card">
                <h2>👤 {buscar_dato(p, ["NOM"])}</h2>
                <p><b>Doc:</b> {busq} | <b>RH:</b> {buscar_dato(p, ["RH"])} | <b>EPS:</b> {buscar_dato(p, ["EPS"])}</p>
                <div class="emergency-box">
                    <p style="color:#c53030; margin:0;"><b>🚨 EMERGENCIA:</b> {buscar_dato(p, ["CONTACTO"])}</p>
                    <p style="margin:0;"><b>Tel:</b> {buscar_dato(p, ["TELEFONO"])}</p>
                </div></div>""", unsafe_allow_html=True)

            if not h_p.empty:
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "HISTORIAL", ln=True)
                st.download_button("📥 DESCARGAR PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{busq}.pdf")

            with st.expander("✍️ AGREGAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    mot = st.text_input("1. Motivo"); c1, c2, c3 = st.columns(3)
                    tll = c1.text_input("2. Talla"); pes = c2.text_input("3. Peso"); ten = c3.text_input("4. TA")
                    ant = st.text_area("5. Antecedentes"); med = st.text_area("6. Medicamentos")
                    lab = st.text_area("7. Laboratorios"); val = st.text_input("8. Valoración"); epi = st.text_area("9. Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        pay = {"entry.2019369477": busq, "entry.611862537": mot, "entry.949747647": tll, "entry.2091389798": pes, "entry.882053172": ten, "entry.889985940": ant, "entry.2016051626": med, "entry.1088523869": lab, "entry.1275746503": val, "entry.616774918": epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay)
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            # --- RENDERIZADO POR RADAR DE PALABRAS CLAVE ---
            for i in range(len(h_p)-1, -1, -1):
                f = h_p.iloc[i]
                st.markdown(f"""<div class="evolution-card">
                    <p style="color:#2b6cb0;">📅 <b>FECHA: {buscar_dato(f, ["MARCA", "FECHA"])}</b></p>
                    <p>📋 <b>VALORACIÓN:</b> {buscar_dato(f, ["VALORACI"])}</p>
                    <p><b>🩺 MOTIVO:</b> {buscar_dato(f, ["MOTIVO"])}</p>
                    <p>📏 <b>TALLA:</b> {buscar_dato(f, ["TALLA"])} | ⚖️ <b>PESO:</b> {buscar_dato(f, ["PESO"])} | 💓 <b>TA:</b> {buscar_dato(f, ["PRESIÓN", "TENSIÓN"])}</p>
                    <p>🧪 <b>LABORATORIOS:</b> {buscar_dato(f, ["LABORATORIO"])}</p>
                    <p>📝 <b>EPICRISIS:</b> {buscar_dato(f, ["EPICRISIS"])}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.dataframe(df_h)
