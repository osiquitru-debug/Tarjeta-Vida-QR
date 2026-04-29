import streamlit as st
import pandas as pd
import requests
import io
from PIL import Image

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO EN TONOS PASTEL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1.5px solid #a2d2ff !important;
    }

    label, p, h1, h2, h3, .stSubheader {
        color: #2d3748 !important; 
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f3e8ff !important;
        border-right: 2px solid #e9d5ff;
    }

    div.stButton > button {
        background-color: #99f6e4 !important;
        color: #134e4a !important;
        border-radius: 12px;
        font-weight: bold !important;
        border: 1px solid #5eead4;
    }

    .medical-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 15px;
        border-left: 12px solid #b2f5ea;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    .emergency-box {
        background-color: #fff5f5;
        padding: 12px;
        border-radius: 10px;
        border: 1px dashed #feb2b2;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
ID_LOGO_DRIVE = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO_DIRECTA = f"https://drive.google.com/uc?export=view&id={ID_LOGO_DRIVE}"

SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Normalizamos: Quitamos espacios al inicio/final y pasamos a MAYÚSCULAS
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        return p, h
    except: return None, None

df_pacientes, df_historial = cargar_datos()

# --- 5. CABECERA ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    try:
        resp = requests.get(URL_LOGO_DIRECTA)
        logo_img = Image.open(io.BytesIO(resp.content))
        st.image(logo_img, use_container_width=True)
    except: st.write("## 🩺 Tarjeta Vida")

st.markdown("<h1 style='text-align: center;'>Gestión Médica Integral</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. NAVEGACIÓN ---
choice = st.sidebar.selectbox("MENÚ PRINCIPAL", ["Registrar Paciente", "Consulta e Historial", "Base de Datos"])

# --- SECCIÓN: REGISTRO ---
if choice == "Registrar Paciente":
    st.subheader("📝 Nuevo Registro")
    with st.form("f_reg", clear_on_submit=True):
        st.markdown("### 👤 Datos del Paciente")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        doc = c2.text_input("Documento de Identidad")
        edad = c1.text_input("Edad")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = c1.text_input("EPS")
        cel = c2.text_input("Celular")
        
        st.markdown("---")
        st.markdown("### 🚨 Contacto de Emergencia")
        ce1, ce2 = st.columns(2)
        e_nom = ce1.text_input("Nombre del contacto de emergencia")
        e_tel = ce2.text_input("Teléfono de contacto de emergencia")
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and doc:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": doc,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": cel, "entry.1172011247": eps,
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success(f"✅ Registrado exitosamente.")
                st.cache_data.clear()
            else: st.error("⚠️ Datos obligatorios faltantes.")

# --- SECCIÓN: CONSULTA E HISTORIAL (AJUSTE DE EMERGENCIA) ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Evolución y Antecedentes")
    id_buscar = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        df_pacientes["DOCUMENTO"] = df_pacientes["DOCUMENTO"].astype(str).str.strip()
        p_data = df_pacientes[df_pacientes["DOCUMENTO"] == id_buscar]
        
        if not p_data.empty:
            p = p_data.iloc[0]
            
            # --- LÓGICA DE BÚSQUEDA DE COLUMNAS DE EMERGENCIA ---
            # Buscamos nombres que contengan "EMERGENCIA" para evitar errores de tildes
            col_nom_em = [c for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c]
            col_tel_em = [c for c in p.index if "TEL" in c and "EMERGENCIA" in c]
            
            e_nombre = p[col_nom_em[0]] if col_nom_em else "No registrado"
            e_tel = p[col_tel_em[0]] if col_tel_em else "No registrado"

            st.markdown(f"""
            <div class="medical-card">
                <h3 style='margin:0; color:#2d3748;'>👤 {p.get('NOMBRE', 'N/A')}</h3>
                <p style='margin:5px 0;'><b>ID:</b> {p.get('DOCUMENTO', 'N/A')} | <b>EPS:</b> {p.get('EPS', 'N/A')} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <div class="emergency-box">
                    <p style='margin:0; color:#c53030; font-size: 0.9em;'><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style='margin:0; color:#2d3748; font-size: 1.1em;'>{e_nombre} — <b>Tel:</b> {e_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📅 Historial Clínico")
            if df_historial is not None:
                df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                h_previo = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                if not h_previo.empty:
                    cols = [c for c in ["FECHA", "TRATAMIENTO", "MEDICAMENTOS", "PROCEDIMIENTOS"] if c in h_previo.columns]
                    st.dataframe(h_previo[cols].iloc[::-1], use_container_width=True, hide_index=True)
                else: st.info("Sin registros previos.")
            
            st.markdown("---")
            st.subheader("✍️ Registrar Nueva Evolución")
            with st.form("ev_f", clear_on_submit=True):
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                pr = st.text_area("Procedimientos")
                if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                    payload_h = {
                        "entry.2019369477": id_buscar, "entry.611862537": t, 
                        "entry.2016051626": m, "entry.ID_PROC": pr # Asegúrate de cambiar ID_PROC
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload_h)
                    st.success("✅ Evolución guardada.")
                    st.cache_data.clear()
                    st.rerun()
        else: st.error("Paciente no encontrado.")

else:
    st.subheader("📊 Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_pacientes is not None: t1.dataframe(df_pacientes)
    if df_historial is not None: t2.dataframe(df_historial)
