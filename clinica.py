import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# 2. Configuración de LECTURA (Desde el Sheet que ya funciona)
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# 3. Configuración de ESCRITURA (Hacia el Formulario)
# Hemos cambiado 'viewform' por 'formResponse' para que Google acepte el envío automático
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        # Intentamos leer la pestaña de pacientes para mostrar en la tabla
        p = pd.read_csv(f"{url_csv}&sheet=pacientes")
        return p
    except:
        return None

df_pacientes = cargar_datos()

# 4. Interfaz de Usuario
st.title("🩺 Tarjeta Vida")
st.markdown("---")

menu = ["Registrar Paciente", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registrar Paciente":
    st.subheader("📝 Crear Nuevo Registro")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.text_input("Edad") # Usamos text para mayor compatibilidad con el form
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Número de Celular")
        
        st.write("**En caso de emergencia avisar a:**")
        e_nombre = col1.text_input("Nombre del Contacto")
        e_tel = col2.text_input("Teléfono del Contacto")
        
        enviar = st.form_submit_button("Guardar en Tarjeta Vida")
        
        if enviar:
            if nombre and documento:
                # Mapeo exacto de tus IDs de Google Form
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
                    # Enviamos los datos por debajo a Google Forms
                    response = requests.post(form_url, data=payload)
                    if response.status_code == 200:
                        st.success(f"✅ ¡Registro de {nombre} guardado exitosamente!")
                        st.balloons()
                        st.cache_data.clear() # Limpiamos cache para ver al nuevo paciente
                    else:
                        st.error("Error al enviar. Revisa la URL del formulario.")
                except:
                    st.error("Hubo un problema de conexión al intentar guardar.")
            else:
                st.warning("El Nombre y el Documento son campos obligatorios.")

elif choice == "Ver Base de Datos":
    st.subheader("📊 Registros en la Nube")
    if df_pacientes is not None:
        st.dataframe(df_pacientes, use_container_width=True)
    else:
        st.info("Conectando con la base de datos... Si no carga, verifica que el Sheet esté 'Publicado en la web'.")
