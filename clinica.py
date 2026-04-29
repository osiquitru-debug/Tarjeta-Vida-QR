import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. VARIABLES DE CONEXIÓN ---
SHEET_ID = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# URLs de Google Forms (Escritura)
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        
        # Normalizamos encabezados: eliminamos espacios y pasamos a MAYÚSCULAS
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        
        return p, h
    except Exception as e:
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
        st.markdown("### 👤 Datos Personales")
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.text_input("Edad")
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        eps = col1.text_input("EPS")
        celular = col2.text_input("Teléfono Celular")
        
        st.markdown("---")
        st.markdown("### 🚨 En caso de emergencia")
        col_em1, col_em2 = st.columns(2)
        e_nombre = col_em1.text_input("Nombre contacto emergencia")
        e_tel = col_em2.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("Guardar Registro Permanente"):
            if nombre and documento:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": documento,
                    "entry.1801154005": edad, "entry.162368130": rh,
                    "entry.1043165037": celular, "entry.1172011247": eps,
                    "entry.1892763134": e_nombre, "entry.2011749615": e_tel
                }
                try:
                    r = requests.post(URL_FORM_PACIENTES, data=payload)
                    if r.ok:
                        st.success(f"✅ ¡{nombre} registrado con éxito!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Error de Google: {r.status_code}")
                except:
                    st.error("Error de conexión al servidor.")
            else:
                st.warning("⚠️ Nombre y Documento son obligatorios.")

# --- SECCIÓN 2: HISTORIAL Y CONSULTA ---
elif choice == "Consulta e Historial":
    st.subheader("🔍 Evolución Médica")
    id_buscar = st.text_input("Ingrese Cédula para buscar").strip()
    
    if id_buscar and df_pacientes is not None:
        # Buscamos usando el nombre de columna normalizado
        col_doc = "DOCUMENTO"
        
        if col_doc in df_pacientes.columns:
            # Aseguramos que los datos de la columna sean texto y sin espacios
            df_pacientes[col_doc] = df_pacientes[col_doc].astype(str).str.strip()
            pac_filtro = df_pacientes[df_pacientes[col_doc] == id_buscar]
            
            if not pac_filtro.empty:
                p = pac_filtro.iloc[0]
                st.success("✅ Paciente localizado")
                
                # Usamos .get() con nombres en MAYÚSCULAS para evitar errores
                st.info(f"**Paciente:** {p.get('NOMBRE', 'N/A')} | **EPS:** {p.get('EPS', 'N/A')} | **RH:** {p.get('RH', 'N/A')}")
                
                with st.expander("🚨 Ver Contacto de Emergencia"):
                    st.write(f"**Nombre:** {p.get('NOMBRE CONTACTO EMERGENCIA', 'No registrado')}")
                    st.write(f"**Teléfono:** {p.get('TELEFONO CONTACTO EMERGENCIA', 'No registrado')}")
                
                with st.expander("📅 Ver Historial Anterior"):
                    if df_historial is not None and "DOCUMENTO" in df_historial.columns:
                        df_historial["DOCUMENTO"] = df_historial["DOCUMENTO"].astype(str).str.strip()
                        h_pac = df_historial[df_historial["DOCUMENTO"] == id_buscar]
                        st.dataframe(h_pac, use_container_width=True) if not h_pac.empty else st.write("Sin registros.")
                
                st.write("---")
                st.write("📝 **Nueva Entrada de Evolución**")
                with st.form("form_historial", clear_on_submit=True):
                    tratamiento = st.text_input("Tratamiento")
                    medicamentos = st.text_area("Medicamentos / Observaciones")
                    procedimiento = st.text_area("Procedimiento Realizado")
                    
                    if st.form_submit_button("Guardar Evolución"):
                        payload_h = {
                            "entry.2019369477": id_buscar, "entry.611862537": tratamiento,
                            "entry.2016051626": medicamentos, "entry.1088523869": procedimiento
                        }
                        if requests.post(URL_FORM_HISTORIAL, data=payload_h).ok:
                            st.success("✅ Evolución guardada correctamente.")
                            st.cache_data.clear()
            else:
                st.error("Paciente no encontrado.")
        else:
            st.error("⚠️ La columna 'DOCUMENTO' no existe en el Excel.")
            st.write("Columnas detectadas:", list(df_pacientes.columns))

# --- SECCIÓN 3: BASE DE DATOS ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Resumen de Registros")
    tab1, tab2 = st.tabs(["Pacientes", "Historial Completo"])
    
    if df_pacientes is not None:
        with tab1: st.dataframe(df_pacientes, use_container_width=True)
    if df_historial is not None:
        with tab2: st.dataframe(df_historial, use_container_width=True)
