import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. CSS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { color: #ffffff !important; }
    .stButton > button { background-color: #4fd1c5 !important; color: #000000 !important; border: 2px solid #285e61; font-weight: bold; width: 100%; }
    .medical-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 15px solid #4fd1c5; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Normalizar encabezados (Mayúsculas y sin espacios)
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        
        # Limpiar columna DOCUMENTO en ambas hojas
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown("### 🏥 MENÚ")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consultar / Evolucionar"): st.session_state.menu = "Consulta"

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registrar":
    st.subheader("📝 Registro de Paciente")
    with st.form("f_reg", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        tipo_doc = c1.selectbox("Tipo Documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Registro Civil", "Cédula de Extranjería"])
        cedula = c2.text_input("Número de Documento")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, 
                    "entry.1650757004": tipo_doc,
                    "entry.1302424820": cedula.strip(), 
                    "entry.162368130": rh
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Paciente registrado. Los datos aparecerán en breve.")
                st.cache_data.clear()
            else: st.warning("Nombre y documento son obligatorios.")

elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Consulta e Historial Médico")
    id_bus = st.text_input("Ingrese Cédula del Paciente").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            # Mostrar Tarjeta del Paciente
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: black !important; margin:0;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p style="color: #444 !important; margin:0;"><b>{p.get('TIPO DE DOCUMENTO', 'ID')}:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- SECCIÓN DE HISTORIAL ---
            st.write("### 📅 Evoluciones Registradas")
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus]
                
                # Definir columnas a mostrar (sin FECHA, usando MARCA DE TIEMPO de Google si existe)
                columnas_posibles = ["MARCA DE TIEMPO", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"]
                columnas_visibles = [c for c in columnas_posibles if c in h_p.columns]
                
                if not h_p.empty:
                    # Mostrar tabla invertida (más reciente arriba)
                    st.dataframe(h_p[columnas_visibles].iloc[::-1], use_container_width=True, hide_index=True)
                else:
                    st.info("Este paciente aún no tiene historial registrado.")
            
            # --- FORMULARIO NUEVA EVOLUCIÓN ---
            with st.form("f_evo", clear_on_submit=True):
                st.write("### ✍️ Registrar Nueva Evolución")
                trat = st.text_input("Tratamiento")
                meds = st.text_area("Medicamentos")
                proc = st.text_area("Procedimientos")
                
                if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                    if trat or meds or proc:
                        payload_h = {
                            "entry.2019369477": id_bus, 
                            "entry.611862537": trat, 
                            "entry.2016051626": meds,
                            "entry.1088523869": proc
                        }
                        requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        st.success("✅ Evolución guardada correctamente.")
                        st.cache_data.clear()
                        st.rerun()
                    else: st.warning("Debes llenar al menos un campo para guardar.")
        else:
            st.error("❌ Paciente no encontrado en la base de datos.")
