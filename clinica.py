import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema Médico", layout="centered")

# --- CONEXIÓN DIRECTA ---
url_hoja = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Forzamos la lectura de las hojas
    df_pacientes = conn.read(spreadsheet=url_hoja, worksheet="Pacientes")
    df_historial = conn.read(spreadsheet=url_hoja, worksheet="Historial")
except Exception as e:
    st.error("🔄 Conectando con Google Sheets...")
    st.info("Si este mensaje no desaparece, verifica que el archivo de Google esté COMPARTIDO como EDITOR para cualquier persona con el enlace.")
    st.stop()

st.title("🩺 Gestión Médica")

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Paciente")
    with st.form("reg"):
        col1, col2 = st.columns(2)
        n = col1.text_input("Nombre")
        d = col2.text_input("Cédula")
        rh = col1.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c = col2.text_input("Celular")
        en = col1.text_input("Contacto Emergencia")
        et = col2.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("Guardar"):
            if n and d:
                nuevo = pd.DataFrame([{"Nombre":n, "Documento":d, "RH":rh, "Celular":c, "Contacto Emergencia":en, "Telefono Emergencia":et}])
                df_act = pd.concat([df_pacientes, nuevo], ignore_index=True)
                conn.update(spreadsheet=url_hoja, worksheet="Pacientes", data=df_act)
                st.success("✅ Guardado correctamente")
            else: st.warning("Nombre y Cédula son obligatorios")

elif choice == "Nueva Consulta":
    st.subheader("🔍 Nueva Consulta")
    doc = st.text_input("Cédula del paciente")
    if doc:
        p = df_pacientes[df_pacientes["Documento"].astype(str) == str(doc)]
        if not p.empty:
            st.warning(f"Paciente: {p.iloc[0]['Nombre']} | RH: {p.iloc[0]['RH']}")
            with st.form("con"):
                t = st.text_input("Tratamiento")
                m = st.text_area("Medicamentos")
                if st.form_submit_button("Actualizar Historial"):
                    nuevo_h = pd.DataFrame([{"Documento":doc, "Fecha":datetime.now().strftime("%d/%m/%Y"), "Tratamiento":t, "Medicamentos":m}])
                    df_h_act = pd.concat([df_historial, nuevo_h], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, worksheet="Historial", data=df_h_act)
                    st.success("✅ Historial Actualizado")
        else: st.error("Paciente no encontrado")

elif choice == "Ver Base de Datos":
    st.write("### Lista de Pacientes")
    st.dataframe(df_pacientes, use_container_width=True)
