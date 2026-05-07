import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# --- 2. CARGA DE DATOS (FLEXIBLE) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Limpiar espacios y estandarizar a mayúsculas para el código
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        # Identificar la columna de Documento en ambas hojas
        def encontrar_doc_col(df):
            for col in df.columns:
                if any(x in col for x in ['DOC', 'CEDULA', 'ID', 'IDENTIFICACION']):
                    df['DOC_KEY'] = df[col].astype(str).str.split('.').str[0].str.strip()
                    return df
            df['DOC_KEY'] = df.iloc[:, 1].astype(str).str.split('.').str[0].str.strip()
            return df

        return encontrar_doc_col(p), encontrar_doc_col(h)
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 TARJETA VIDA")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. FUNCIONES DE APOYO ---
def obtener_valor(df_row, posibles_nombres):
    """Busca un valor en la fila probando diferentes nombres de columna."""
    for nombre in posibles_nombres:
        if nombre.upper() in df_row.index:
            return str(df_row[nombre.upper()])
    return "No registrado"

def generar_pdf(paciente, historial_p):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "HISTORIA CLÍNICA - TARJETA VIDA", ln=True, align='C')
    pdf.ln(5)
    
    # Datos Paciente en PDF
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"PACIENTE: {obtener_valor(paciente, ['NOMBRE', 'NOMBRE COMPLETO'])}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Doc: {paciente['DOC_KEY']} | EPS: {obtener_valor(paciente, ['EPS'])} | RH: {obtener_valor(paciente, ['RH'])}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    
    # Evoluciones en PDF
    for _, fila in historial_p.iterrows():
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, f"FECHA: {fila.get('MARCA TEMPORAL', 'S/F')}", ln=True)
        pdf.set_font("Arial", '', 9)
        # Mostrar los campos principales de la evolución
        msg = f"MOTIVO: {obtener_valor(fila, ['MOTIVO DE LA CONSULTA'])}\nVALORACION: {obtener_valor(fila, ['VALORACION'])}\nMEDICAMENTOS: {obtener_valor(fila, ['MEDICAMENTOS'])}\n"
        pdf.multi_cell(0, 5, msg)
        pdf.cell(0, 2, "_"*80, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 BIENVENIDO A TARJETA VIDA")
    st.write("Seleccione una opción en el menú lateral para comenzar.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    st.info("Complete el formulario en Google Forms para registrar al paciente.")
    st.markdown("[Abrir Formulario de Registro](https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/viewform)")

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    busqueda = st.text_input("Ingrese el Documento del Paciente:").strip()
    
    if busqueda and df_p is not None:
        p_match = df_p[df_p["DOC_KEY"] == busqueda]
        
        if not p_match.empty:
            p = p_match.iloc[0]
            
            # --- TARJETA DEL PACIENTE ---
            st.success("Paciente Encontrado")
            with st.container():
                st.subheader(f"👤 {obtener_valor(p, ['NOMBRE', 'NOMBRE COMPLETO'])}")
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Documento:** {busqueda}")
                c2.write(f"**Edad:** {obtener_valor(p, ['EDAD'])}")
                c3.write(f"**RH:** {obtener_valor(p, ['RH'])}")
                
                c4, c5 = st.columns(2)
                c4.write(f"**EPS:** {obtener_valor(p, ['EPS'])}")
                c5.write(f"**Celular:** {obtener_valor(p, ['CELULAR', 'TELEFONO'])}")
                
                st.warning(f"🚨 **Emergencia:** {obtener_valor(p, ['NOMBRE CONTACTO EMERGENCIA'])} - {obtener_valor(p, ['TELEFONO CONTACTO EMERGENCIA'])}")

            # --- BOTÓN PDF ---
            if df_h is not None:
                h_p = df_h[df_h["DOC_KEY"] == busqueda].sort_index(ascending=False)
                if not h_p.empty:
                    st.download_button(
                        label="📥 Descargar Historia Clínica (PDF)",
                        data=generar_pdf(p, h_p),
                        file_name=f"HC_{busqueda}.pdf",
                        mime="application/pdf"
                    )

            # --- VISUALIZACIÓN DE EVOLUCIONES ---
            st.divider()
            st.subheader("📋 Evoluciones Recientes")
            if not h_p.empty:
                for _, fila in h_p.iterrows():
                    with st.expander(f"📅 {fila.get('MARCA TEMPORAL', 'Ver detalles')}"):
                        st.write(f"**Motivo:** {obtener_valor(fila, ['MOTIVO DE LA CONSULTA'])}")
                        st.write(f"**Valoración:** {obtener_valor(fila, ['VALORACION'])}")
                        st.write(f"**Medicamentos:** {obtener_valor(fila, ['MEDICAMENTOS'])}")
                        st.write(f"**Epicrisis:** {obtener_valor(fila, ['EPICRISIS'])}")
            else:
                st.info("Este paciente no tiene evoluciones registradas aún.")
        else:
            st.error("No se encontró ningún paciente con ese número de documento.")
