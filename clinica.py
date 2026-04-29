import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. VARIABLES DE CONEXIÓN ---
# Lectura (Google Sheets Publicado)
SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Escritura (Google Forms - URLs de Respuesta)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        # Cargamos las pestañas. Asegúrate que en el Excel se llamen exactamente así.
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        return p, h
    except:
        return None, None

df_pacientes, df_historial = cargar_datos()

# --- 4. INTERFAZ Y NAVEGACIÓN ---
st.title("🩺 Sistema Tarjeta Vida")
st.markdown("---")

menu = ["Registrar Paciente", "Consulta e Historial", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- SECCIÓN 1: REGISTRO DE PACIENTES ---
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
                # Mapeo de IDs para el Formulario de Pacientes
                payload = {
                    "entry.346175428": nombre,
                    "entry.1302424820": documento,
                    "entry.1801154005": edad,
                    "entry.162368130": rh,
                    "entry.1043165037": celular,
                    "entry.1892763134": e_nombre,
                    "entry.2011749615": e_tel
                }
                try:
                    r = requests.post(URL_FORM_PACIENTES, data=payload)
                    if r.ok:
                        st.success(f"✅ ¡{nombre} registrado con éxito!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Error de Google: {r.status_code}. Revisa la privacidad del formulario.")
                except:
                    st.error("Error de conexión al servidor.")
            else:
                st.warning("⚠️ Nombre y Documento son obligatorios.")

# --- SECCIÓN 2: HISTORIAL Y CONSULTA ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Evolución Médica")
    # Limpiamos la entrada del usuario inmediatamente
    id_buscar = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        # LIMPIEZA: Forzamos la columna Documento a texto y quitamos espacios
        df_pacientes["Documento"] = df_pacientes["Documento"].astype(str).str.strip()
        
        # Búsqueda exacta
        pac_filtro = df_pacientes[df_pacientes["Documento"] == id_buscar]
        
        if not pac_filtro.empty:
            p = pac_filtro.iloc[0]
            st.success("✅ Paciente localizado")
            st.info(f"**Paciente:** {p['Nombre']} | **RH:** {p['RH']} | **Emergencia:** {p.get('Telefono Emergencia', 'No registrado')}")
            
            # Ver registros previos
            with st.expander("📅 Ver Historial Anterior"):
                if df_historial is not None:
                    # También limpiamos el historial para que coincida la búsqueda
                    df_historial["Documento"] = df_historial["Documento"].astype(str).str.strip()
                    h_pac = df_historial[df_historial["Documento"] == id_buscar]
                    
                    if not h_pac.empty:
                        st.dataframe(h_pac, use_container_width=True)
                    else:
                        st.write("Sin registros médicos previos.")
            
            # Formulario Nueva Consulta
            st.write("---")
            st.write("📝 **Nueva Entrada de Evolución**")
            with st.form("form_historial", clear_on_submit=True):
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Medicamentos / Observaciones")
                procedimiento = st.text_area("Procedimiento Realizado")
                
                if st.form_submit_button("Guardar Evolución"):
                    payload_h = {
                        "entry.2019369477": id_buscar,
                        "entry.611862537": tratamiento,
                        "entry.2016051626": medicamentos,
                        "entry.1088523869": procedimiento
                    }
                    try:
                        r_h = requests.post(URL_FORM_HISTORIAL, data=payload_h)
                        if r_h.ok:
                            st.success("✅ Evolución guardada correctamente.")
                            st.cache_data.clear()
                        else:
                            st.error(f"Error {r_h.status_code}. Revisa la configuración del formulario.")
                    except:
                        st.error("Error de conexión.")
        else:
            st.error(f"Paciente con documento '{id_buscar}' no encontrado.")
            st.info("💡 Sugerencia: Revisa en 'Ver Base de Datos' si el paciente ya fue registrado.")

# --- SECCIÓN 3: BASE DE DATOS ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Resumen de Registros")
    tab1, tab2 = st.tabs(["Pacientes", "Historial Completo"])
    
    if df_pacientes is not None:
        with tab1:
            st.dataframe(df_pacientes, use_container_width=True)
    else:
        with tab1: st.error("No se pudo cargar la pestaña 'pacientes'.")

    if df_historial is not None:
        with tab2:
            st.dataframe(df_historial, use_container_width=True)
    else:
        with tab2: st.error("No se pudo cargar la pestaña 'historial'.")
