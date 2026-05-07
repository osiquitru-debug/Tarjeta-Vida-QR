import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import base64

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], select, input, textarea {
        background-color: #ffffff !important; color: #000000 !important;
    }
    h1, h2, h3, p, label { color: #1a202c !important; text-align: center; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; text-align: left;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold; text-align: center;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; border-left: 5px solid #63b3ed;
        margin-bottom: 10px; color: #2d3748; text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RECURSOS Y URLs ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. FUNCIONES AUXILIARES ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        def normalizar_doc(df):
            posibles = ['DOCUMENTO', 'CEDULA', 'ID', 'DOCUMENTO IDENTIDAD']
            for n in posibles:
                if n in df.columns:
                    df['DOC_KEY'] = df[n].astype(str).str.split('.').str[0].str.strip()
                    return df
            return df

        return normalizar_doc(p), normalizar_doc(h)
    except:
        return None, None

def generar_pdf(paciente, historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "HISTORIAL MÉDICO - TARJETA VIDA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Paciente: {paciente.get('NOMBRE')}", ln=True)
    pdf.cell(200, 10, f"Documento: {paciente.get('DOC_KEY')}", ln=True)
    pdf.ln(5)
    for _, fila in historial.iterrows():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, f"Fecha: {fila.get('MARCA TEMPORAL')}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, f"Valoración: {fila.get('VALORACION')}\nMotivo: {fila.get('MOTIVO DE LA CONSULTA')}\n")
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. LÓGICA DE NAVEGACIÓN ---
df_p, df_h = cargar_datos()
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(URL_LOGO, width=200)
    st.title("🩺 TARJETA VIDA")
    st.write("Sistema de gestión médica rural.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            doc = st.text_input("Documento")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        if st.form_submit_button("REGISTRAR"):
            payload = {"entry.346175428": nom, "entry.1302424820": doc, "entry.1172011247": eps, "entry.162368130": rh}
            requests.post(URL_FORM_PACIENTES, data=payload)
            st.success("Registrado correctamente.")

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    busqueda = st.text_input("Documento a consultar").strip()
    if busqueda and df_p is not None:
        p_row = df_p[df_p["DOC_KEY"] == busqueda]
        if not p_row.empty:
            p = p_row.iloc[0]
            st.markdown(f"""<div class="medical-card">
                <h3>👤 {p.get('NOMBRE')}</h3>
                <p>RH: {p.get('RH')} | EPS: {p.get('EPS')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('TELEFONO CONTACTO EMERGENCIA')}</div>
            </div>""", unsafe_allow_html=True)

            with st.expander("✍️ NUEVA EVOLUCIÓN"):
                with st.form("evo_f"):
                    v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo"); v3 = st.text_input("Presión")
                    if st.form_submit_button("GUARDAR"):
                        h_pay = {"entry.2019369477": busqueda, "entry.1088523869": v1, "entry.611862537": v2, "entry.2091389798": v3}
                        requests.post(URL_FORM_HISTORIAL, data=h_pay)
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL")
            if df_h is not None:
                h_p = df_h[df_h["DOC_KEY"] == busqueda].sort_index(ascending=False)
                if not h_p.empty:
                    # BOTÓN PDF
                    pdf_data = generar_pdf(p, h_p)
                    st.download_button("📥 Descargar Historial PDF", data=pdf_data, file_name=f"Historial_{busqueda}.pdf", mime="application/pdf")
                    
                    for _, fila in h_p.iterrows():
                        st.markdown(f"""<div class="evo-card">
                            <small>📅 {fila.get('MARCA TEMPORAL')}</small><br>
                            <b>Valoración:</b> {fila.get('VALORACION')}<br>
                            <b>Motivo:</b> {fila.get('MOTIVO DE LA CONSULTA')}<br>
                            <b>Presión:</b> {fila.get('PRESION ARTERIAL')}
                        </div>""", unsafe_allow_html=True)
                else: st.info("Sin registros.")
        else: st.error("No encontrado.")
