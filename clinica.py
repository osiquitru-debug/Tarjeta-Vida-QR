import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Historial Médico Pro", layout="centered")

st.title("🩺 Gestión Médica Integral")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
df_pacientes = conn.read(worksheet="Pacientes")
df_historial = conn.read(worksheet="Historial")

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- 1. REGISTRAR PACIENTE (CAMPOS AMPLIADOS) ---
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
        
        submit = st.form_submit_button("Guardar Paciente")
        
        if submit:
            if nombre and documento:
                nuevo_p = pd.DataFrame([{
                    "Nombre": nombre, 
                    "Documento": documento, 
                    "Edad": edad,
                    "RH": rh,
                    "Celular": celular,
                    "Contacto Emergencia": emergencia_nombre,
                    "Telefono Emergencia": emergencia_tel
                }])
                df_actualizado = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                conn.update(worksheet="Pacientes", data=df_actualizado)
                st.success(f"✅ Paciente {nombre} guardado con éxito")
            else:
                st.error("Por favor, llena al menos el nombre y el documento.")

# --- 2. NUEVA CONSULTA ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Registro de Evolución Médica")
    doc_buscar = st.text_input("Ingrese Cédula para buscar")
    
    if doc_buscar:
        paciente_info = df_pacientes[df_pacientes["Documento"].astype(str) == str(doc_buscar)]
        
        if not paciente_info.empty:
            # Mostramos un resumen de emergencia destacado
            st.warning(f"""
            **DATOS VITALES:**
            * **Paciente:** {paciente_info.iloc[0]['Nombre']}
            * **RH:** {paciente_info.iloc[0]['RH']}
            * **En caso de emergencia llamar a:** {paciente_info.iloc[0]['Contacto Emergencia']} ({paciente_info.iloc[0]['Telefono Emergencia']})
            """)
            
            with st.form("consulta_form"):
                tratamiento = st.text_input("Tratamiento Actual")
                medicamentos = st.text_area("Medicamentos Recetados")
                procedimiento = st.text_area("Procedimientos Realizados")
                
                if st.form_submit_button("Guardar Consulta"):
                    nueva_entrada = pd.DataFrame([{
                        "Documento": doc_buscar,
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Tratamiento": tratamiento,
                        "Medicamentos": medicamentos,
                        "Procedimiento": procedimiento
                    }])
                    df_h_act = pd.concat([df_historial, nueva_entrada], ignore_index=True)
                    conn.update(worksheet="Historial", data=df_h_act)
                    st.success("✅ Historial médico actualizado")
        else:
            st.error("El paciente no existe.")

# --- 3. VER TODO ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Base de Datos Completa")
    tab1, tab2 = st.tabs(["Lista de Pacientes", "Historial de Consultas"])
    
    with tab1:
        st.dataframe(df_pacientes)
    with tab2:
        st.dataframe(df_historial)