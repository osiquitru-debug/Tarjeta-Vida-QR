import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# 2. Configuración de la conexión
# Usamos el ID de tu hoja que ya comprobamos que funciona
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_lectura_publica = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# Conexión oficial para escritura (Usa los Secrets de Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para cargar datos (Lectura ultra-estable)
@st.cache_data(ttl=10) # Se refresca cada 10 segundos
def cargar_datos():
    try:
        # Leemos mediante el método de publicación web que nos dio éxito
        p = pd.read_csv(f"{url_lectura_publica}&sheet=Pacientes")
        h = pd.read_csv(f"{url_lectura_publica}&sheet=Historial")
        return p, h
    except Exception as e:
        return None, None

df_pacientes, df_historial = cargar_datos()

# Verificación de conexión
if df_pacientes is None:
    st.error("⚠️ Error de conexión con la base de datos.")
    st.info("Asegúrate de que el archivo de Google Sheets esté 'Publicado en la Web'.")
    st.stop()

# 4. Interfaz de Usuario
st.title("🩺 Tarjeta Vida")
menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- OPCIÓN 1: REGISTRAR PACIENTE ---
if choice == "Registrar Paciente":
    st.subheader("📝 Registro de Nueva Tarjeta Vida")
    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", 0, 120)
        rh = col2.selectbox("RH (Grupo Sanguíneo)", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Número de Celular")
        st.markdown("---")
        st.write("**Contacto de Emergencia**")
        e_nombre = col1.text_input("Nombre del Contacto")
        e_tel = col2.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and documento:
                # Crear el nuevo registro en un DataFrame
                nuevo_p = pd.DataFrame([{
                    "Nombre": nombre, 
                    "Documento": documento, 
                    "Edad": edad,
                    "RH": rh, 
                    "Celular": celular, 
                    "Contacto Emergencia": e_nombre,
                    "Telefono Emergencia": e_tel
                }])
                
                try:
                    # Combinamos datos viejos con el nuevo y subimos a Google Sheets
                    df_actualizado = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                    conn.update(worksheet="Pacientes", data=df_actualizado)
                    
                    st.success(f"✅ ¡Tarjeta Vida de {nombre} creada con éxito!")
                    st.balloons()
                    st.cache_data.clear() # Limpiamos memoria para ver el cambio
                except Exception as e:
                    st.error("❌ Error al guardar. Verifica que el permiso en Google Sheets sea 'EDITOR'.")
            else:
                st.warning("Por favor, llena el Nombre y la Cédula.")

# --- OPCIÓN 2: NUEVA CONSULTA (EVOLUCIÓN) ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Evolución Médica")
    busqueda = st.text_input("Ingrese Cédula del paciente")
    
    if busqueda:
        # Buscamos al paciente por documento
        paciente = df_pacientes[df_pacientes["Documento"].astype(str) == str(busqueda)]
        
        if not paciente.empty:
            st.warning(f"**Paciente:** {paciente.iloc[0]['Nombre']} | **RH:** {paciente.iloc[0]['RH']}")
            st.write(f"📞 **Emergencia:** {paciente.iloc[0]['Contacto Emergencia']} ({paciente.iloc[0]['Telefono Emergencia']})")
            
            with st.form("consulta_form"):
                tratamiento = st.text_input("Tratamiento Actual")
                medicamentos = st.text_area("Medicamentos / Observaciones")
                procedimiento = st.text_area("Procedimientos Realizados")
                
                if st.form_submit_button("Actualizar Historial"):
                    nueva_consulta = pd.DataFrame([{
                        "Documento": busqueda,
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tratamiento": tratamiento,
                        "Medicamentos": medicamentos,
                        "Procedimiento": procedimiento
                    }])
                    
                    try:
                        # Actualizamos la pestaña 'Historial'
                        df_h_act = pd.concat([df_historial, nueva_consulta], ignore_index=True)
                        conn.update(worksheet="Historial", data=df_h_act)
                        st.success("✅ Historial de Tarjeta Vida actualizado")
                        st.cache_data.clear()
                    except:
                        st.error("No se pudo guardar la evolución.")
        else:
            st.error("Documento no encontrado en el sistema Tarjeta Vida.")

# --- OPCIÓN 3: VER BASE DE DATOS ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Base de Datos Tarjeta Vida")
    tab1, tab2 = st.tabs(["Pacientes", "Historiales"])
    
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True)
    with tab2:
        st.dataframe(df_historial, use_container_width=True)
