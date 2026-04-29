import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tarjeta Vida QR", layout="centered")

# --- CONFIGURACIÓN ---
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_publica = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# Conexión para ESCRITURA
conn = st.connection("gsheets", type=GSheetsConnection)

# Función de lectura estable
def cargar_datos():
    # Intentamos leer por el método que nos funcionó
    p = pd.read_csv(f"{url_publica}&sheet=Pacientes")
    h = pd.read_csv(f"{url_publica}&sheet=Historial")
    return p, h

try:
    df_pacientes, df_historial = cargar_datos()
except:
    st.error("Error de conexión. Verifica los permisos de Google Sheets.")
    st.stop()

st.title("🩺 Gestión Médica Integral")
menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Paciente")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", 0, 120)
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Celular")
        e_nombre = col1.text_input("Contacto Emergencia")
        e_tel = col2.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("Guardar en la Nube"):
            if nombre and documento:
                nuevo_p = pd.DataFrame([{
                    "Nombre": nombre, "Documento": documento, "Edad": edad,
                    "RH": rh, "Celular": celular, "Contacto Emergencia": e_nombre,
                    "Telefono Emergencia": e_tel
                }])
                # INTENTO DE GUARDADO REAL
                try:
                    df_actualizado = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                    conn.update(spreadsheet=url_publica, worksheet="Pacientes", data=df_actualizado)
                    st.success(f"✅ ¡{nombre} guardado exitosamente en Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error("Error al guardar. Verifica que en Secrets esté el enlace de la hoja.")
            else:
                st.warning("Faltan datos obligatorios.")

elif choice == "Ver Base de Datos":
    st.subheader("📊 Registros Actuales")
    st.dataframe(df_pacientes, use_container_width=True)
