import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

# --- 2. ESTÉTICA PROFESIONAL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar visibilidad de texto */
    label, p, h1, h2, h3, span, div, li, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 600 !important; 
    }
    
    /* Centrado de Logo */
    .logo-container { 
        display: flex; 
        justify-content: center; 
        margin: 20px 0; 
    }

    /* Estilo de Tarjetas Médicas */
    .medical-card {
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 12px solid #4fd1c5; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        margin-bottom: 20px;
    }

    .evolution-card {
        background-color: #ffffff; 
        padding: 18px; 
        border-radius: 12px; 
        border-left: 8px solid #63b3ed; 
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    /* Inputs y Formularios */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #a2d2ff !important;
    }

    /* Botón Principal */
    div.stButton > button:first-child {
        background-color: #4fd1c5 !important; 
        color: #000000 !important; 
        font-weight: 900 !important;
        border-radius: 10px;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE DATOS Y URLS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_BASE_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

# URLs de envío (formResponse)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_BASE_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_BASE_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 4. INTERFAZ ---
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="180"></div>', unsafe_allow_html=True)

if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown("### 🏥 Panel de Control")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"

# --- SECCIÓN REGISTRO ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Pacientes</h1>", unsafe_allow_html=True)
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo de documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería", "Pasaporte"])
            doc = st.text_input("Número de Documento")
        with c2:
            cel = st.text_input("Celular")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        cond = st.text_area("Condiciones Especiales / Alergias")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nom and doc:
                payload_p = {
                    "entry.346175428": nom, "entry.1650757004": tdoc,
                    "entry.1302424820": doc.strip(), "entry.1801154005": "N/A", 
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.162368130": rh, "entry.346363": cond
                }
                requests.post(URL_FORM_PACIENTES, data=payload_p)
                st.success(f"✅ {nom} registrado.")
                st.cache_data.clear()

# --- SECCIÓN CONSULTA ---
elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Historial Clínico</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    
    if id_bus and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == id_bus]
        if not pac.empty:
            p = pac.iloc[0]
            st.markdown(f"""
                <div class="medical-card">
                    <h2>👤 {p.get('NOMBRE', 'N/A')}</h2>
                    <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                    <p><b>Alergias:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)', 'Ninguna')}</p>
                </div>
            """, unsafe_allow_html=True)

            # Formulario Historial Completo
            with st.expander("✍️ AGREGAR NUEVA EVOLUCIÓN (HISTORIAL)"):
                with st.form("f_his", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        mot = st.text_input("Motivo de la Consulta")
                        tall = st.text_input("Talla (cm)")
                        pres = st.text_input("Presión Arterial")
                    with col_b:
                        val = st.text_input("Valoración")
                        pes = st.text_input("Peso (kg)")
                    
                    ant = st.text_area("Antecedentes Médicos")
                    med = st.text_area("Medicamentos")
                    lab = st.text_area("Laboratorios")
                    epi = st.text_area("Epicrisis (Resumen Final)")

                    if st.form_submit_button("GUARDAR EN EL SISTEMA"):
                        payload_h = {
                            "entry.2019369477": id_bus, "entry.611862537": mot,
                            "entry.1275746503": val, "entry.949747647": tall,
                            "entry.2091389798": pes, "entry.889985940": ant,
                            "entry.2016051626": med, "entry.882053172": pres,
                            "entry.1088523869": lab, "entry.616774918": epi
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución guardada exitosamente.")
                        st.cache_data.clear()
                        st.rerun()

            # Mostrar registros anteriores
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus].reset_index(drop=True)
                for i in range(len(h_p)-1, -1, -1):
                    f = h_p.iloc[i]
                    st.markdown(f"""
                        <div class="evolution-card">
                            <p style="color:#2d3748;">📅 <b>Fecha: {f.get('MARCA TEMPORAL', 'S/F')}</b></p>
                            <p><b>Motivo:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/A')}</p>
                            <p><b>Epicrisis:</b> {f.get('EPICRISIS', 'N/A')}</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Paciente no encontrado.")
