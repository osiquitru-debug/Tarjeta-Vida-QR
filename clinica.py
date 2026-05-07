import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN BÁSICA (SIN ADORNOS) ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# --- 2. CARGA DE DATOS Y NORMALIZACIÓN DE BÚSQUEDA ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def limpiar_documento(valor):
    """Elimina decimales, espacios y convierte a texto puro para búsqueda exacta."""
    if pd.isna(valor) or valor == "": return ""
    return str(valor).split('.')[0].replace(" ", "").strip()

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        # Se cargan las hojas 'pacientes' e 'historial'
        df_pacientes = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        df_historial = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Se crea una columna 'LLAVE' en ambas para que el buscador no falle
        # Se asume que el documento está en la segunda columna (índice 1)
        df_pacientes['LLAVE'] = df_pacientes.iloc[:, 1].apply(limpiar_documento)
        df_historial['LLAVE'] = df_historial.iloc[:, 1].apply(limpiar_documento)
        
        return df_pacientes, df_historial
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_tablas()

# --- 3. NAVEGACIÓN ---
if 'seccion' not in st.session_state: 
    st.session_state.seccion = "Inicio"

with st.sidebar:
    st.title("MENÚ")
    if st.button("🏠 Inicio"): st.session_state.seccion = "Inicio"
    if st.button("📝 Registro de Paciente"): st.session_state.seccion = "Registro"
    if st.button("🔍 Consulta y Evolución"): st.session_state.seccion = "Consulta"

# --- 4. SECCIONES ---

if st.session_state.seccion == "Inicio":
    st.title("SISTEMA MÉDICO TARJETA VIDA")
    st.write("Bienvenido. Use el menú lateral para operar.")

elif st.session_state.seccion == "Registro":
    st.title("REGISTRO DE PACIENTE")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            num_doc = st.text_input("Número de Documento")
            edad = st.text_input("Edad")
        with col2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            c_emergencia = st.text_input("Contacto Emergencia")
            t_emergencia = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, 
                "entry.1302424820": num_doc, "entry.1801154005": edad, 
                "entry.1172011247": eps, "entry.162368130": rh, 
                "entry.1892763134": c_emergencia, "entry.2011749615": t_emergencia
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente registrado exitosamente.")
            st.cache_data.clear()

elif st.session_state.seccion == "Consulta":
    st.title("CONSULTA Y EVOLUCIÓN")
    id_ingresado = st.text_input("Documento del Paciente:").strip()
    id_limpio = limpiar_documento(id_ingresado)
    
    if id_limpio and df_p is not None:
        paciente = df_p[df_p['LLAVE'] == id_limpio]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            # MOSTRAR DATOS DEL PACIENTE (Usando posiciones fijas para evitar errores de nombres)
            st.subheader(f"Paciente: {p.iloc[2]}")
            st.write(f"**Documento:** {p.iloc[1]} | **Edad:** {p.iloc[4]} | **RH:** {p.iloc[6]} | **EPS:** {p.iloc[5]}")
            st.warning(f"CONTACTO EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}")

            # FORMULARIO DE EVOLUCIÓN (10 CAMPOS)
            with st.expander("REGISTRAR EVOLUCIÓN"):
                with st.form("form_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo de consulta")
                        v3 = st.text_input("Talla"); v4 = st.text_input("Peso"); v5 = st.text_input("Presión")
                    with c2:
                        v6 = st.text_area("Antecedentes"); v7 = st.text_area("Medicamentos")
                        v8 = st.text_area("Laboratorios"); v9 = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        evo_payload = {
                            "entry.2019369477": id_limpio, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=evo_payload)
                        st.success("Evolución guardada.")
                        st.cache_data.clear()
                        st.rerun()

            # HISTORIAL Y PDF
            st.subheader("HISTORIAL MÉDICO")
            h_paciente = df_h[df_h['LLAVE'] == id_limpio].sort_index(ascending=False)
            
            if not h_paciente.empty:
                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"HISTORIA CLINICA: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_paciente.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\n{'-'*50}")
                
                st.download_button("Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_limpio}.pdf", "application/pdf")

                for _, r in h_paciente.iterrows():
                    st.write(f"**Fecha:** {r.iloc[0]}")
                    st.write(f"**Valoración:** {r.iloc[2]}")
                    st.write(f"**Motivo:** {r.iloc[3]}")
                    st.write("---")
            else:
                st.info("No hay evoluciones registradas.")
        else:
            st.error("Paciente no encontrado. Verifique el número de documento en su base de datos.")
