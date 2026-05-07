import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import unicodedata
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica QR", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span, div, li, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .medical-card {
        background-color: #ffffff; padding: 22px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .evolution-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 3px solid #d8b4fe; }
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.8em; width: 100%;
    }
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DE LIMPIEZA CRÍTICA ---
def limpiar_identificador(valor):
    """Convierte cualquier entrada (123, 123.0, ' 123 ') en una cadena limpia '123'"""
    if pd.isna(valor): return ""
    # Convertir a string, quitar espacios y remover el .0 si es un float de Excel
    s = str(valor).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

def normalizar_nombre_columna(col):
    """Quita tildes y pone en mayúsculas para emparejar columnas"""
    return "".join(c for c in unicodedata.normalize('NFD', str(col)) if unicodedata.category(c) != 'Mn').upper().strip()

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=1) # Actualiza casi en tiempo real
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        
        # PROCESAMIENTO DE COLUMNAS DOCUMENTO
        for df in [p, h]:
            # Buscar la columna que contenga "DOC" (independiente de tildes o mayúsculas)
            col_doc = next((c for c in df.columns if "DOC" in normalizar_nombre_columna(c)), None)
            if col_doc:
                df[col_doc] = df[col_doc].apply(limpiar_identificador)
            else:
                st.error(f"No se encontró la columna 'DOCUMENTO' en una de las hojas.")
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.title("Registro de Pacientes")
    with st.form("reg", clear_on_submit=True):
        nom = st.text_input("Nombre Completo")
        doc = st.text_input("Documento (Solo números)")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        eps = st.text_input("EPS")
        if st.form_submit_button("GUARDAR"):
            if nom and doc:
                res = requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", 
                              data={"entry.346175428": nom, "entry.1302424820": doc.strip(), "entry.1172011247": eps, "entry.162368130": rh})
                st.success("✅ Enviado a Google Sheets. Espere un momento a que se actualice la base.")
                st.cache_data.clear()
            else: st.warning("Faltan datos")

elif st.session_state.menu == "Consulta":
    st.title("Consulta Médica")
    # Limpiamos la entrada del usuario inmediatamente
    busq = limpiar_identificador(st.text_input("Ingrese Documento del Paciente"))
    
    if busq and df_p is not None:
        # Buscamos la columna documento dinámicamente
        col_doc_p = next((c for c in df_p.columns if "DOC" in normalizar_nombre_columna(c)), None)
        
        # FILTRADO ROBUSTO
        pac = df_p[df_p[col_doc_p] == busq]
        
        if not pac.empty:
            p = pac.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE', 'N/R')}</h2>
                <p>ID: {busq} | RH: {p.get('RH', 'N/R')} | EPS: {p.get('EPS', 'N/R')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar evoluciones relacionadas
            col_doc_h = next((c for c in df_h.columns if "DOC" in normalizar_nombre_columna(c)), None)
            h_p = df_h[df_h[col_doc_h] == busq]
            
            for _, f in h_p.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="evolution-card">
                    <p>📅 {f.get('MARCA TEMPORAL', 'S/F')}</p>
                    <p><b>Motivo:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/R')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"El documento '{busq}' no existe en la base. Revisa la pestaña 'Base de Datos'.")

elif st.session_state.menu == "Base":
    st.subheader("Datos actuales en Google Sheets")
    st.write("Pacientes:", df_p)
    st.write("Historial:", df_h)
