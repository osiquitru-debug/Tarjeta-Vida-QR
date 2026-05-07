import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA ORIGINAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered")

st.markdown("""
    <style>
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0;
        margin-bottom: 10px; color: #2d3748;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargar pacientes e historial
        df_p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        df_h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        
        # Normalización estricta de DOC_KEY para búsqueda
        def preparar_df(df):
            # Buscamos la columna de documento (normalmente la segunda después de Marca Temporal)
            col_doc = df.columns[1] 
            df['DOC_KEY'] = df[col_doc].astype(str).str.split('.').str[0].str.strip()
            return df
            
        return preparar_df(df_p), preparar_df(df_h)
    except:
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
    st.title("BIENVENIDO A TARJETA VIDA")
    st.info("Sistema de Gestión de Historias Clínicas")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE NUEVO PACIENTE")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombres = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "RC", "CE"])
            n_doc = st.text_input("Número de Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_emergencia = st.text_input("Nombre Contacto Emergencia")
        t_emergencia = st.text_input("Teléfono Contacto Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            # Mapeo exacto a tu Google Form de Pacientes
            data_p = {
                "entry.346175428": nombres, "entry.1650757004": t_doc,
                "entry.1302424820": n_doc, "entry.1172011247": eps,
                "entry.162368130": rh, "entry.1645028456": c_emergencia,
                "entry.1500244670": t_emergencia
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=data_p)
            st.success("Paciente registrado exitosamente.")
            st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA Y EVOLUCIÓN")
    busqueda = st.text_input("Ingrese Documento del Paciente:").strip()
    
    if busqueda and df_p is not None:
        p_row = df_p[df_p["DOC_KEY"] == busqueda]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            # TARJETA COMPLETA
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.iloc[2]}</h2>
                <p><b>Documento:</b> {p.iloc[1]} ({p.iloc[3]}) | <b>Edad:</b> {p.iloc[4]}</p>
                <p><b>EPS:</b> {p.iloc[5]} | <b>RH:</b> {p.iloc[6]}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FORMULARIO EVOLUCIÓN (10 CAMPOS)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN MÉDICA"):
                with st.form("form_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo de consulta")
                        v3 = st.text_input("Talla"); v4 = st.text_input("Peso")
                    with c2:
                        v5 = st.text_input("Presión Arterial"); v6 = st.text_area("Antecedentes")
                        v7 = st.text_area("Medicamentos"); v8 = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        data_h = {
                            "entry.2019369477": busqueda, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.616774918": v8
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_h)
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            # HISTORIAL Y PDF
            st.subheader("📋 HISTORIAL")
            h_p = df_h[df_h["DOC_KEY"] == busqueda].sort_index(ascending=False)
            
            if not h_p.empty:
                # Generar PDF (Simple y funcional)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"HISTORIA: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_p.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nMOTIVO: {r.iloc[2]}\nVALORACION: {r.iloc[3]}\nEPICRISIS: {r.iloc[9]}\n{'-'*40}")
                
                st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{busqueda}.pdf", "application/pdf")

                for _, r in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {r.iloc[0]}</small><br>
                        <b>Motivo:</b> {r.iloc[2]}<br>
                        <b>Valoración:</b> {r.iloc[3]}<br>
                        <b>Medicamentos:</b> {r.iloc[8]}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay registros previos.")
        else:
            st.error("Paciente no encontrado.")
