import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. VARIABLES DE CONEXIÓN (Google Sheets y Forms) ---
# Lectura desde Google Sheets (Publicado en la web)
SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Escritura vía Google Forms (IMPORTANTE: terminan en /formResponse)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. FUNCIÓN PARA CARGAR DATOS ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        # Asegúrate de que las pestañas en tu Excel se llamen exactamente así
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        return p, h
    except:
        return None, None

df_pacientes, df_historial = cargar_datos()

# --- 4. INTERFAZ DE USUARIO ---
st.title("🩺 Sistema Tarjeta Vida")
st.markdown("---")

menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# OPCIÓN 1: REGISTRAR NUEVO PACIENTE
if choice == "Registrar Paciente":
    st.subheader("📝 Nuevo Registro de Usuario")
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.text_input("Edad")
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Teléfono Celular")
        e_nombre = col1.text_input("Contacto de Emergencia")
        e_tel = col2.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("Guardar Registro Permanente"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre,
                    "entry.1302424820": documento,
                    "entry.1801154005": edad,
                    "entry.162368130": rh,
                    "entry.1043165037": celular,
                    "entry.1892763134": e_nombre,
                    "entry.2011749615": e_tel
                }
                if requests.post(URL_FORM_PACIENTES, data=payload).ok:
                    st.success(f"✅ ¡{nombre} registrado con éxito!")
                    st.cache_data.clear()
                else:
                    st.error("Error al guardar en la nube.")
            else:
                st.warning("⚠️ El Nombre y el Documento son obligatorios.")

# OPCIÓN 2: CONSULTA DE HISTORIAL Y NUEVA EVOLUCIÓN
elif choice == "Consulta e Historial":
    st.subheader("🔍 Gestión de Evolución Médica")
    id_buscar = st.text_input("Ingrese Cédula del paciente")
    
    if id_buscar and df_pacientes is not None:
        pac_info = df_pacientes[df_pacientes["Documento"].astype(str) == str(id_buscar)]
        
        if not pac_info.empty:
            p = pac_info.iloc[0]
            st.info(f"**Paciente:** {p['Nombre']} | **RH:** {p['RH']} | **Emergencia:** {p['Telefono Emergencia']}")
            
            # Ver Historial Previo
            with st.expander("📅 Ver Evoluciones Anteriores"):
                if df_historial is not None:
                    h_pac = df_historial[df_historial["Documento"].astype(str) == str(id_buscar)]
                    if not h_pac.empty:
                        st.dataframe(h_pac, use_container_width=True)
                    else:
                        st.write("No hay registros previos para este paciente.")
            
            # Formulario para Nueva Evolución
            st.write("---")
            st.write("📝 **Registrar Nueva Consulta**")
            with st.form("form_historial", clear_on_submit=True):
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Observaciones / Medicamentos")
                procedimiento = st.text_area("Procedimientos Realizados")
                
                if st.form_submit_button("Guardar Evolución"):
                    # Mapeo de IDs para el Formulario de Historial
                    payload_h = {
                        "entry.2019369477": id_buscar,
                        "entry.611862537": tratamiento,
                        "entry.2016051626": medicamentos,
                        "entry.1088523869": procedimiento
                    }
                    if requests.post(URL_FORM_HISTORIAL, data=payload_h).ok:
                        st.success("✅ Evolución guardada correctamente.")
                        st.cache_data.clear()
                    else:
                        st.error("Error al guardar la evolución.")
        else:
            st.error("Paciente no encontrado en la base de datos.")

# OPCIÓN 3: VISUALIZACIÓN DE BASE DE DATOS
elif choice == "Ver Base de Datos":
    st.subheader("📊 Registros Globales")
    tab1, tab2 = st.tabs(["Pacientes", "Historial Completo"])
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True) if df_pacientes is not None else st.write("Error de conexión.")
    with tab2:
        st.dataframe(df_historial, use_container_width=True) if df_historial is not None else st.write("Error de conexión.")
