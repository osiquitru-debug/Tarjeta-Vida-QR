import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Tarjeta Vida", page_icon="🩺")

# --- LECTURA (Mantenemos lo que ya funciona) ---
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def cargar_datos():
    try:
        p = pd.read_csv(f"{url_csv}&sheet=pacientes")
        return p
    except: return None

df_pacientes = cargar_datos()

st.title("🩺 Tarjeta Vida")

# --- REGISTRO (Usando Google Forms para escribir) ---
with st.form("registro"):
    nombre = st.text_input("Nombre")
    doc = st.text_input("Documento")
    rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
    
    if st.form_submit_button("Guardar"):
        # URL de envío de tu Google Form (debes obtenerla de 'Enviar' -> 'Obtener enlace rellenado')
        form_url = "AQUÍ_VA_TU_ENLACE_DE_GOOGLE_FORM"
        
        datos = {
            "entry.12345678": nombre, # Estos IDs se sacan del formulario
            "entry.87654321": doc,
            "entry.11223344": rh
        }
        
        try:
            requests.post(form_url, data=datos)
            st.success("✅ ¡Datos enviados con éxito!")
            st.balloons()
        except:
            st.error("Error al conectar")
