import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Enlace directo estable
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        def limpiar(txt): return str(txt).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except Exception as e:
        st.error(f"Error al cargar base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    col_s1, col_s2, col_s3 = st.columns([1, 3, 1])
    with col_s2:
        st.image(LOGO_URL)
    
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL)
    st.markdown("<h1 style='text-align: center;'>TARJETA VIDA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sistema de Historias Clínicas - Guadalupe, Huila</p>", unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r2:
        st.image(LOGO_URL, width=150)
    st.title("📝 REGISTRO DE NUEVO PACIENTE")
    with st.form("form_registro_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
            edad = st.text_input("Edad")
        with col2:
            celular = st.text_input("Celular")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_especiales = st.text_area("Condiciones Especiales (Alergias, Enfermedades)")
        
        # SECCIÓN DE CONTACTO DE EMERGENCIA
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre del Contacto")
        c_tel = st.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            try:
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success(f"✅ Paciente {nombre} registrado correctamente.")
                st.cache_data.clear()
            except:
                st.error("Error al guardar los datos.")

elif st.session_state.menu == "Consulta":
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c2:
        st.image(LOGO_URL, width=150)
    st.title("🔍 CONSULTA MÉDICA")
    busqueda_raw = st.text_input("Ingrese el Documento del Paciente").strip()
    id_buscado = busqueda_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.write(f"## 👤 Paciente: {p.get('NOMBRE')}")
            st.write(f"**Documento:** {p.get('DOCUMENTO')} | **Edad:** {p.get('EDAD')} | **RH:** {p.get('RH')}")
            st.write(f"**EPS:** {p.get('EPS')} | **Celular:** {p.get('CELULAR')}")
            st.warning(f"⚠️ **Condiciones Especiales:** {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}")
            
            # MOSTRAR CONTACTO DE EMERGENCIA EN CONSULTA
            st.error(f"🚨 **EMERGENCIA:** Llamar a {p.get('NOMBRE CONTACTO EMERGENCIA')} al {p.get('TELEFONO CONTACTO EMERGENCIA')}")
        else:
            st.error("Paciente no encontrado en la base de datos.")
