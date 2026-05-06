import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica QR", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS (Tu diseño original) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4; }
    .stMarkdown p, label { color: #000000; font-weight: 600; }
    div[data-baseweb="select"] > div { background-color: #ffffff; border: 2px solid #a2d2ff; }
    input, textarea { background-color: #ffffff; border: 2px solid #a2d2ff; }
    [data-testid="stSidebar"] { background-color: #f3e8ff; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff; border: 2px solid #d8b4fe; font-weight: bold; }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5; color: #000000; border-radius: 12px; font-weight: 900; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .condition-box { background-color: #fff9db; padding: 12px; border-radius: 10px; border: 1px solid #fab005; margin: 10px 0; }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RECURSOS Y URLs ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
# URL de respuesta (cambiamos /viewform por /formResponse)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"

# --- 4. GESTIÓN DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        p.columns = p.columns.str.strip().str.upper()
        if 'DOCUMENTO' in p.columns:
            p['DOCUMENTO'] = p['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p
    except: return None

df_p = cargar_datos()

# --- 5. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"

with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta"): st.session_state.menu = "Consulta"

# --- 6. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Paciente</h1>", unsafe_allow_html=True)
    
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        tipo_doc = c1.selectbox("Tipo de Documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Cédula de Extranjería"])
        cedula = c2.text_input("Número de Documento")
        
        # Nuevo campo basado en tu entry.346363
        condiciones = st.text_area("Condiciones Especiales y Alergias")
        
        c3, c4 = st.columns(2)
        edad = c3.text_input("Edad")
        rh = c4.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c5, c6 = st.columns(2)
        eps = c5.text_input("EPS")
        cel = c6.text_input("Celular")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                # Payload mapeado exactamente a tu enlace de Google Forms
                payload = {
                    "entry.346175428": nombre,
                    "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(),
                    "entry.1801154005": edad,
                    "entry.1043165037": cel,
                    "entry.1172011247": eps,
                    "entry.162368130": rh,
                    "entry.346363": condiciones, # ID verificado de tu enlace
                    "entry.1892763134": e_nom,
                    "entry.2011749615": e_tel
                }
                response = requests.post(URL_FORM_PACIENTES, data=payload)
                if response.status_code == 200:
                    st.success("✅ Datos enviados correctamente a la base de datos.")
                    st.cache_data.clear()
                else:
                    st.error("❌ Error al conectar con el formulario.")
            else:
                st.error("⚠️ Nombre y Documento son obligatorios.")

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta Médica</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            # Buscamos la columna de condiciones (puede variar según tu Excel)
            cond_val = p.get('CONDICIONES ESPECIALES Y ALERGIAS', p.get('CONDICIONES', 'Ninguna'))
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: black !important;">👤 {p.get('NOMBRE COMPLETO', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <div class="condition-box">
                    <p style="color: #856404 !important; margin: 0; font-size: 0.9em; font-weight: 900 !important;"><b>⚠️ CONDICIONES Y ALERGIAS:</b></p>
                    <p style="color: #000000 !important; margin: 0; font-weight: 600 !important;">{cond_val}</p>
                </div>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>CEL:</b> {p.get('CELULAR', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: #c53030 !important; margin:0; font-weight: 900 !important;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0; color: black !important;"><b>Nombre:</b> {p.get('NOMBRE CONTACTO EMERGENCIA', 'N/A')}</p>
                    <p style="margin:0; color: black !important;"><b>Tel:</b> {p.get('TELÉFONO CONTACTO EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Paciente no encontrado.")
