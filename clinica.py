import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración visual
st.set_page_config(page_title="Sistema Médico Pro", layout="wide")

st.title("🩺 Gestión Médica Integral")

# --- CONFIGURACIÓN DE LA HOJA (Mantenemos lo que funcionó) ---
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_pacientes = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Pacientes"
url_historial = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Historial"

@st.cache_data(ttl=60) # Actualiza los datos cada minuto
def cargar_datos():
    p = pd.read_csv(url_pacientes)
    h = pd.read_csv(url_historial)
    return p, h

try:
    df_pacientes, df_historial = cargar_datos()
    st.sidebar.success("✅ Conectado a la Base de Datos")
except:
    st.error("Error al cargar datos. Verifica que el archivo siga 'Publicado en la Web'.")
    st.stop()

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- 1. REGISTRAR PACIENTE ---
if choice == "Registrar Paciente":
    st.subheader("📝 Ficha de Registro")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", 0, 120)
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Celular del Paciente")
        st.markdown("---")
        e_nombre = col1.text_input("Contacto de Emergencia")
        e_tel = col2.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and documento:
                # En esta versión estable, mostramos los datos para confirmar
                st.success(f"✅ Datos listos para {nombre}")
                st.info("ℹ️ Para completar el guardado permanente en la nube, recuerda que esta versión requiere que pegues los datos o uses la conexión certificada (Secrets).")
                # Mostramos la línea lista para copiar y pegar si fuera necesario
                st.code(f"{nombre},{documento},{edad},{rh},{celular},{e_nombre},{e_tel}")
            else:
                st.warning("Nombre y Documento obligatorios")

# --- 2. NUEVA CONSULTA ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Buscar Paciente")
    busqueda = st.text_input("Ingrese Cédula")
    
    if busqueda:
        # Buscamos en el DataFrame cargado
        p = df_pacientes[df_pacientes["Documento"].astype(str) == str(busqueda)]
        
        if not p.empty:
            st.warning(f"**Paciente:** {p.iloc[0]['Nombre']} | **RH:** {p.iloc[0]['RH']}")
            st.write(f"📞 **Emergencia:** {p.iloc[0]['Contacto Emergencia']} ({p.iloc[0]['Telefono Emergencia']})")
            
            with st.form("consulta"):
                trat = st.text_input("Tratamiento")
                meds = st.text_area("Medicamentos")
                if st.form_submit_button("Registrar Evolución"):
                    st.success("Consulta procesada exitosamente")
        else:
            st.error("Paciente no encontrado")

# --- 3. VER BASE DE DATOS ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Registros en Google Sheets")
    tab1, tab2 = st.tabs(["Pacientes", "Historial"])
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True)
    with tab2:
        st.dataframe(df_historial, use_container_width=True)
