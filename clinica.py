import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered")

# --- 2. CARGA DE DATOS (MÉTODO DE SEGURIDAD POSICIONAL) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Forzar la lectura de todas las columnas como texto para evitar errores con los documentos
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str)
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str)
        
        # Limpieza de nombres de columnas
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        # Crear llave de búsqueda DOC_KEY basada en la posición de la columna (evita KeyErrors)
        # En la hoja 'pacientes', el documento suele ser la columna índice 1 o 2
        def asignar_llave(df):
            for col in df.columns:
                if "DOC" in col or "CEDULA" in col or "ID" in col:
                    df['DOC_BUSQUEDA'] = df[col].str.split('.').str[0].str.strip()
                    return df
            # Si no encuentra el nombre, asume la segunda columna por defecto
            df['DOC_BUSQUEDA'] = df.iloc[:, 1].str.split('.').str[0].str.strip()
            return df

        return asignar_llave(p), asignar_llave(h)
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.title("SISTEMA TARJETA VIDA")
    st.write("Utilice el menú lateral para gestionar la información de salud.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("registro_paciente"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_emer = st.text_input("Contacto Emergencia")
        t_emer = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR DATOS"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc,
                "entry.1302424820": n_doc, "entry.1801154005": edad,
                "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_emer, "entry.2011749615": t_emer
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_busqueda = st.text_input("Documento del Paciente:").strip()
    
    if id_busqueda and df_p is not None:
        p_match = df_p[df_p["DOC_BUSQUEDA"] == id_busqueda]
        
        if not p_match.empty:
            p = p_match.iloc[0]
            # TARJETA DE PACIENTE (Uso de iloc para garantizar que carguen los datos sin importar el nombre de la columna)
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 8px solid #4fd1c5; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h2 style="color: #2d3748;">👤 {p.iloc[2]}</h2>
                <p style="color: #4a5568;"><b>ID:</b> {id_busqueda} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <p style="color: #4a5568;"><b>EPS:</b> {p.iloc[5]}</p>
                <div style="background-color: #fff5f5; padding: 10px; border-radius: 5px; color: #c53030; border: 1px dashed #f56565;">
                    🚨 EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # REGISTRO DE EVOLUCIÓN (10 CAMPOS - IDs Actualizados)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN MÉDICA"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo de Consulta")
                        v3 = st.text_input("3. Talla"); v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión")
                    with c2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        h_payload = {
                            "entry.2019369477": id_busqueda, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_payload)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # VISUALIZACIÓN DE HISTORIAL Y PDF
            st.subheader("📋 HISTORIAL MÉDICO")
            if df_h is not None:
                h_p = df_h[df_h["DOC_BUSQUEDA"] == id_busqueda].sort_index(ascending=False)
                
                if not h_p.empty:
                    # Generar PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, f"HISTORIAL CLINICO: {p.iloc[2]}", ln=True)
                    pdf.set_font("Arial", size=10)
                    for _, r in h_p.iterrows():
                        pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\nEPICRISIS: {r.iloc[10]}\n{'-'*50}")
                    
                    st.download_button("📥 DESCARGAR PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_busqueda}.pdf", "application/pdf")

                    for _, r in h_p.iterrows():
                        st.markdown(f"""
                        <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #63b3ed; margin-bottom: 10px; border: 1px solid #e2e8f0;">
                            <small>📅 {r.iloc[0]}</small><br>
                            <b>Valoración:</b> {r.iloc[2]}<br>
                            <b>Motivo:</b> {r.iloc[3]}<br>
                            <b>Medicamentos:</b> {r.iloc[8]}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No se encontraron evoluciones previas.")
        else:
            st.error("El paciente no existe en la base de datos.")
