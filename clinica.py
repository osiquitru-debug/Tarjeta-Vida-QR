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
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS SEGURA ---
@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        
        # Normalizar nombres de columnas
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        def identificar_doc(df):
            # Intentar por nombres comunes
            for col in ['DOCUMENTO', 'DOCUMENTO_KEY', 'CEDULA', 'ID']:
                if col in df.columns:
                    df['DOC_KEY'] = df[col].astype(str).str.split('.').str[0].str.strip()
                    return df
            # Si falla, tomar la segunda columna (usualmente Documento tras Marca Temporal)
            df['DOC_KEY'] = df.iloc[:, 1].astype(str).str.split('.').str[0].str.strip()
            return df

        return identificar_doc(p), identificar_doc(h)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# Logo centrado arriba
c1, c2, c3 = st.columns([1,1,1])
with c2: st.image(URL_LOGO, width=120)

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 TARJETA VIDA")
    st.subheader("Gestión de Historiales Médicos")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            doc_id = st.text_input("Número de Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, 
                "entry.1302424820": doc_id, "entry.1172011247": eps, "entry.162368130": rh
            }
            requests.post(URL_FORM_PACIENTES, data=payload)
            st.success("Registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA Y EVOLUCIÓN")
    busqueda = st.text_input("Documento del Paciente").strip()
    
    if busqueda and df_p is not None:
        p_data = df_p[df_p["DOC_KEY"] == busqueda]
        if not p_data.empty:
            p = p_data.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'Sin Nombre')}</h2>
                <p><b>ID:</b> {busqueda} | <b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
            </div>""", unsafe_allow_html=True)
            
            with st.expander("✍️ REGISTRAR EVOLUCIÓN (10 CAMPOS)"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo"); v3 = st.text_input("3. Talla")
                        v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión")
                    with c2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        h_pay = {
                            "entry.2019369477": busqueda, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post(URL_FORM_HISTORIAL, data=h_pay)
                        st.success("Guardado"); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL MÉDICO")
            if df_h is not None:
                h_p = df_h[df_h["DOC_KEY"] == busqueda]
                if not h_p.empty:
                    # Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, f"Historial: {p.get('NOMBRE')}", ln=True)
                    pdf.set_font("Arial", size=10)
                    for _, r in h_p.iterrows():
                        pdf.multi_cell(0, 5, f"FECHA: {r.get('MARCA TEMPORAL')}\nMOTIVO: {r.get('MOTIVO DE LA CONSULTA')}\nVALORACION: {r.get('VALORACION')}\n{'-'*30}")
                    
                    st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"Historial_{busqueda}.pdf", "application/pdf")

                    for _, f in h_p.sort_index(ascending=False).iterrows():
                        st.markdown(f"""
                        <div class="evo-card">
                            <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                            <b>1. Valoración:</b> {f.get('VALORACION')}<br>
                            <b>2. Motivo:</b> {f.get('MOTIVO DE LA CONSULTA')}<br>
                            <b>Medicamentos:</b> {f.get('MEDICAMENTOS')}
                        </div>""", unsafe_allow_html=True)
                else: st.info("Sin registros.")
        else: st.error("Paciente no encontrado.")
