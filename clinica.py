import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# 2. Configuración de IDs y Conexión
# Tu ID de hoja verificado
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
url_lectura_publica = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# Conexión para ESCRITURA (usa los Secrets configurados en Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Carga de datos estable
@st.cache_data(ttl=10)
def cargar_datos():
    try:
        # Intentamos leer de la publicación web para asegurar que siempre haya datos
        p = pd.read_csv(f"{url_lectura_publica}&sheet=Pacientes")
        h = pd.read_csv(f"{url_lectura_publica}&sheet=Historial")
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_pacientes, df_historial = cargar_datos()

# 4. Título e Interfaz
st.title("🩺 Tarjeta Vida")
st.markdown("---")

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- OPCIÓN 1: REGISTRAR PACIENTE ---
if choice == "Registrar Paciente":
    st.subheader("📝 Crear Nueva Tarjeta Vida")
    
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", 0, 120, value=25)
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Teléfono Celular")
        
        st.write("**En caso de emergencia avisar a:**")
        e_nombre = col1.text_input("Nombre del Contacto")
        e_tel = col2.text_input("Teléfono del Contacto")
        
        btn_guardar = st.form_submit_button("Guardar Registro Permanente")
        
        if btn_guardar:
            if nombre and documento:
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
                    # Unimos los datos actuales con el nuevo
                    df_actualizado = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                    
                    # EJECUCIÓN DEL GUARDADO
                    conn.update(worksheet="Pacientes", data=df_actualizado)
                    
                    st.success(f"✅ ¡Tarjeta de {nombre} guardada exitosamente!")
                    st.balloons()
                    st.cache_data.clear() # Limpia cache para mostrar el nuevo dato
                except Exception as error:
                    st.error("❌ No se pudo guardar en Google Sheets.")
                    st.info(f"Detalle técnico: {error}")
                    st.warning("Asegúrate de que el permiso en el botón COMPARTIR sea 'EDITOR' para cualquier persona con el enlace.")
            else:
                st.warning("⚠️ El Nombre y el Documento son obligatorios.")

# --- OPCIÓN 2: NUEVA CONSULTA ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Evolución Médica")
    id_buscar = st.text_input("Buscar por Cédula")
    
    if id_buscar:
        # Búsqueda flexible (convirtiendo a string)
        resultado = df_pacientes[df_pacientes["Documento"].astype(str) == str(id_buscar)]
        
        if not resultado.empty:
            p_data = resultado.iloc[0]
            st.info(f"**Paciente:** {p_data['Nombre']} | **RH:** {p_data['RH']}")
            st.write(f"🚑 **Contacto:** {p_data['Contacto Emergencia']} ({p_data['Telefono Emergencia']})")
            
            with st.form("consulta_form", clear_on_submit=True):
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Observaciones / Medicamentos")
                procedimiento = st.text_area("Procedimiento realizado")
                
                if st.form_submit_button("Actualizar Historial"):
                    nueva_fila = pd.DataFrame([{
                        "Documento": id_buscar,
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tratamiento": tratamiento,
                        "Medicamentos": medicamentos,
                        "Procedimiento": procedimiento
                    }])
                    
                    try:
                        df_h_act = pd.concat([df_historial, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Historial", data=
