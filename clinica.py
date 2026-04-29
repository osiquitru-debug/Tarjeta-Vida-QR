import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# 2. Configuración de la conexión
# Usamos el enlace que proporcionaste
url_sheet = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/edit?usp=sharing"
sheet_id = "18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0"
# URL para lectura rápida vía CSV
url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

# Conexión oficial para escritura (Configurada mediante Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función de carga de datos (Lectura estable)
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        # Intentamos leer las pestañas específicas
        p = pd.read_csv(f"{url_csv}&sheet=pacientes")
        h = pd.read_csv(f"{url_csv}&sheet=historial")
        return p, h
    except Exception:
        return None, None

df_pacientes, df_historial = cargar_datos()

if df_pacientes is None:
    st.error("⚠️ No se pudo conectar con la base de datos.")
    st.info("Verifica que en Google Sheets hayas ido a: Archivo > Compartir > Publicar en la web.")
    st.stop()

# 4. Interfaz de Usuario
st.title("🩺 Tarjeta Vida")
st.markdown("---")

menu = ["Registrar Paciente", "Nueva Consulta", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- OPCIÓN 1: REGISTRAR PACIENTE ---
if choice == "Registrar Paciente":
    st.subheader("📝 Nuevo Registro Tarjeta Vida")
    
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo")
        documento = col2.text_input("Cédula/ID")
        edad = col1.number_input("Edad", 0, 120, value=18)
        rh = col2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        celular = col1.text_input("Teléfono Celular")
        
        st.write("**Contacto en Caso de Emergencia**")
        e_nombre = col1.text_input("Nombre del Contacto")
        e_tel = col2.text_input("Teléfono del Contacto")
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and documento:
                # Crear DataFrame con el nuevo paciente
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
                    # Combinar con datos existentes y actualizar la hoja
                    df_actualizado = pd.concat([df_pacientes, nuevo_p], ignore_index=True)
                    conn.update(spreadsheet=url_sheet, worksheet="pacientes", data=df_actualizado)
                    
                    st.success(f"✅ ¡{nombre} registrado con éxito!")
                    st.balloons()
                    st.cache_data.clear() # Forzar recarga de datos
                except Exception as e:
                    st.error("❌ Error al guardar. Verifica que el permiso en Google sea 'Editor'.")
                    st.info(f"Detalle: {e}")
            else:
                st.warning("El Nombre y la Cédula son campos obligatorios.")

# --- OPCIÓN 2: NUEVA CONSULTA ---
elif choice == "Nueva Consulta":
    st.subheader("🔍 Evolución Médica")
    id_buscar = st.text_input("Ingrese Cédula del paciente")
    
    if id_buscar:
        res = df_pacientes[df_pacientes["Documento"].astype(str) == str(id_buscar)]
        
        if not res.empty:
            p = res.iloc[0]
            st.info(f"**Paciente:** {p['Nombre']} | **RH:** {p['RH']}")
            
            with st.form("consulta_form", clear_on_submit=True):
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Observaciones / Medicamentos")
                procedimiento = st.text_area("Procedimientos Realizados")
                
                if st.form_submit_button("Actualizar Historial"):
                    nueva_entrada = pd.DataFrame([{
                        "Documento": id_buscar,
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tratamiento": tratamiento,
                        "Medicamentos": medicamentos,
                        "Procedimiento": procedimiento
                    }])
                    
                    try:
                        df_h_act = pd.concat([df_historial, nueva_entrada], ignore_index=True)
                        conn.update(spreadsheet=url_sheet, worksheet="historial", data=df_h_act)
                        st.success("✅ Historial de Tarjeta Vida actualizado.")
                        st.cache_data.clear()
                    except:
                        st.error("Error al actualizar la base de datos.")
        else:
            st.error("Documento no encontrado.")

# --- OPCIÓN 3: VER BASE DE DATOS ---
elif choice == "Ver Base de Datos":
    st.subheader("📊 Registros")
    tab1, tab2 = st.tabs(["Pacientes", "Historiales"])
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True)
    with tab2:
        st.dataframe(df_historial, use_container_width=True)
