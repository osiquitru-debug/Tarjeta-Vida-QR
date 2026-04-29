import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema Médico", layout="centered")

# --- CONEXIÓN DIRECTA POR CSV (A prueba de errores) ---
# Este método es el más estable de todos para leer datos públicos
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_pacientes = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Pacientes"
url_historial = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Historial"

try:
    df_pacientes = pd.read_csv(url_pacientes)
    df_historial = pd.read_csv(url_historial)
    st.success("✅ Conexión establecida")
except Exception as e:
    st.error("⚠️ No se pudo leer la hoja.")
    st.info("Asegúrate de que en Google Sheets: 1. El archivo sea PÚBLICO (Cualquier persona con el enlace). 2. Las pestañas se llamen exactamente Pacientes e Historial.")
    st.stop()

st.title("🩺 Gestión Médica")
menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Registro")
    with st.form("reg"):
        n = st.text_input("Nombre")
        d = st.text_input("Cédula")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c = st.text_input("Celular")
        if st.form_submit_button("Guardar"):
            st.info("Para guardar datos en esta versión gratuita, copia los datos al Excel manualmente o solicita la configuración de API Key.")
            st.write(f"Datos: {n}, {d}, {rh}, {c}")

elif choice == "Ver Base de Datos":
    st.write("### Pacientes")
    st.dataframe(df_pacientes)
