import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS PASTEL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { color: #ffffff !important; }
    
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; }

    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em;
    }

    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 10px; border-radius: 8px; border: 1px dashed red; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO (CORREGIDO) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}" # Nuevo método de enlace directo
st.sidebar.image(URL_LOGO, use_container_width=True)

# --- 4. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 5. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.markdown("### 🏥 **MENÚ**")
    if st.button("📝 Registrar"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta"): st.session_state.menu = "Consulta"
    if st.button("📊 Base Datos"): st.session_state.menu = "Base"

# --- 6. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.subheader("📝 Nuevo Paciente")
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        tipo_doc = c1.selectbox("Tipo Documento", ["Cédula de Ciudadanía", "Tarjeta de Identidad", "Registro Civil", "Cédula de Extranjería"])
        cedula = c2.text_input("Documento")
        c3, c4 = st.columns(2)
        edad = st.text_input("Edad")
        rh = c4.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = st.text_input("EPS")
        cel = st.text_input("Celular")
        st.markdown("### 🚨 Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("GUARDAR"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": cedula.strip(),
                "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps,
                "entry.162368130": rh, "entry.1892763134": e_nom, "entry.2011749615": e_tel
            }
            requests.post(URL_FORM_PACIENTES, data=payload)
            st.success("Registrado.")
            st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Buscar Paciente")
    id_bus = st.text_input("Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            # Buscador flexible de columnas de emergencia
            emer_nom = p.get('NOMBRE DEL CONTACTO DE EMERGENCIA') or p.get('NOMBRE CONTACTO EMERGENCIA') or "No registrado"
            emer_tel = p.get('TELEFONO DE CONTACTO DE EMERGENCIA') or p.get('TELEFONO CONTACTO EMERGENCIA') or "N/A"
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: black !important;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>CEL:</b> {p.get('CELULAR', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 EMERGENCIA:</b> {emer_nom}</p>
                    <p style="margin:0; color: black !important;"><b>TEL:</b> {emer_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### 📅 Evoluciones")
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus]
                cols = [c for c in ["MARCA DE TIEMPO", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"] if c in h_p.columns]
                st.dataframe(h_p[cols].iloc[::-1], use_container_width=True, hide_index=True)

            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar")
                t, m, pr = st.text_input("Tratamiento"), st.text_area("Medicamentos"), st.text_area("Procedimientos")
                if st.form_submit_button("GUARDAR"):
                    requests.post(URL_FORM_HISTORIAL, data={"entry.2019369477": id_bus, "entry.611862537": t, "entry.2016051626": m, "entry.1088523869": pr})
                    st.success("Guardado.")
                    st.cache_data.clear()
                    st.rerun()
        else: st.error("No encontrado.")

else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_p is not None: t1.dataframe(df_p)
    if df_h is not None: t2.dataframe(df_h)
