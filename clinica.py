import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Historial Médico Flexible", layout="centered")

st.title("🩺 Gestión Médica Integral")

conn = st.connection("gsheets", type=GSheetsConnection)
url_hoja = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/edit?usp=sharing"

# --- FUNCIÓN PARA BUSCAR HOJAS SIN IMPORTAR MAYÚSCULAS ---
def obtener_nombre_real(nombre_buscado):
    try:
        # Esto obtiene todos los nombres de las pestañas de tu Google Sheets
        todas_las_hojas = conn.read(spreadsheet=url_hoja, list_names=True)
        for hoja in todas_las_hojas:
            if hoja.lower().strip() == nombre_buscado.lower():
                return hoja
        return nombre_buscado # Si no la encuentra, devuelve el original
    except:
        return nombre_buscado

# Detectamos cómo escribiste los nombres en tu Excel
nombre_hoja_pacientes = obtener_nombre_real("pacientes")
nombre_hoja_historial = obtener_nombre_real("historial")

# --- LEER DATOS CON LOS NOMBRES DETECTADOS ---
try:
    df_pacientes = conn.read(spreadsheet=url_hoja, worksheet=nombre_hoja_pacientes)
    df_historial = conn.read(spreadsheet=url_hoja, worksheet=nombre_hoja_historial)
except Exception as e:
    st.error(f"No se pudo encontrar la pestaña. Verifica que en tu Excel exista una hoja llamada Pacientes e Historial.")
    st.stop()

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- 1. REGISTRAR PACIENTE ---
if choice == "Registrar Paciente":
    st.subheader("📝 Ficha de Registro Inicial")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo del Paciente")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", min_value=0, max_value=120)
        rh = col2.selectbox("Tipo de Sangre (RH)", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Número de Celular del Paciente")
        st.markdown("---")
        st.write("**Datos de Emergencia**")
        emergencia_nombre = col1.text_input("Nombre del Contacto de Emergencia")
        emergencia_tel = col2.text_input("Teléfono del Contacto de Emergencia")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and documento:
                nuevo_p = pd.DataFrame([{
                    "Nombre": nombre, "Documento": documento, "Edad": edad,
                    "RH": rh, "Celular": celular, "Contacto Emergencia": emergencia_nombre,
                    "Telefono Emergencia": emergencia_tel
                }])
                df_act_p = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                conn.update(spreadsheet=url_hoja, worksheet=nombre_hoja_pacientes, data=df_act_p)
                st.success(f"✅ Guardado en la hoja: {nombre_hoja_pacientes}")
                st.balloons()

# --- 2. NUEVA CONSULTA ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Registro de Evolución Médica")
    doc_buscar = st.text_input("Cédula para buscar")
    if doc_buscar:
        paciente_info = df_pacientes[df_pacientes["Documento"].astype(str) == str(doc_buscar)]
        if not paciente_info.empty:
            st.warning(f"**Paciente:** {paciente_info.iloc[0]['Nombre']} | **RH:** {paciente_info.iloc[0]['RH']}")
            with st.form("consulta_form"):
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Medicamentos")
                procedimiento = st.text_area("Procedimiento")
                if st.form_submit_button("Guardar Consulta"):
                    nueva_entrada = pd.DataFrame([{
                        "Documento": doc_buscar, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Tratamiento": tratamiento, "Medicamentos": medicamentos, "Procedimiento": procedimiento
                    }])
                    df_act_h = pd.concat([df_historial, nueva_entrada], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, worksheet=nombre_hoja_historial, data=df_act_h)
                    st.success("✅ Historial actualizado")
        else:
            st.error("Paciente no encontrado.")

# --- 3. VER TODO ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Datos en Google Sheets")
    t1, t2 = st.tabs([f"Hoja: {nombre_hoja_pacientes}", f"Hoja: {nombre_hoja_historial}"])
    with t1: st.dataframe(df_pacientes)
    with t2: st.dataframe(df_historial)
