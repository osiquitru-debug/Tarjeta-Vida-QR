import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA PROFESIONAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    
    /* Tarjeta de Paciente */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px; color: #1a202c;
    }
    
    /* Cuadro de Emergencia */
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
        margin-top: 15px; text-align: center;
    }
    
    /* Tarjetas de Evolución */
    .evo-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0;
        margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Estilo de Inputs */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: #ffffff !important; border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS CON DOBLE VALIDACIÓN ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registrado")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registrado")
        
        # Limpieza profunda de la columna de documento para evitar el error de búsqueda
        def limpiar_llave(df):
            # Buscamos la columna que contenga el documento (usualmente la segunda)
            col_doc = df.columns[1]
            df['DOC_KEY'] = df[col_doc].str.split('.').str[0].str.strip()
            return df
            
        return limpiar_llave(p), limpiar_llave(h)
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🩺 Tarjeta Vida</h1>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.title("Sistema Médico Tarjeta Vida")
    st.write("Bienvenido. Utilice el menú lateral para navegar.")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Paciente")
    with st.form("registro_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
            edad = st.text_input("Edad")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            c_emer = st.text_input("Nombre Contacto Emergencia")
            t_emer = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_emer, "entry.2011749615": t_emer
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado en la base de datos."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    busqueda = st.text_input("Ingrese el Documento del Paciente:").strip()
    
    if busqueda and df_p is not None:
        p_row = df_p[df_p["DOC_KEY"] == busqueda]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            # TARJETA ESTÉTICA DEL PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.iloc[2]}</h2>
                <p style='font-size: 1.1em;'><b>Documento:</b> {busqueda} | <b>Edad:</b> {p.iloc[4]} años | <b>RH:</b> {p.iloc[6]}</p>
                <p><b>EPS:</b> {p.iloc[5]}</p>
                <div class="emergency-box">
                    🚨 CONTACTO DE EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FORMULARIO DE EVOLUCIÓN (10 CAMPOS)
            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo de Consulta")
                        v3 = st.text_input("3. Talla"); v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión Arterial")
                    with c2:
                        v6 = st.text_area("6. Antecedentes Médicos"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios/Procedimientos"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("💾 GUARDAR EVOLUCIÓN"):
                        h_payload = {
                            "entry.2019369477": busqueda, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_payload)
                        st.success("✅ Evolución guardada."); st.cache_data.clear(); st.rerun()

            # HISTORIAL Y PDF
            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h["DOC_KEY"] == busqueda].sort_index(ascending=False)
            
            if not h_p.empty:
                # Botón PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"HISTORIA CLÍNICA: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_p.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACIÓN: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\nMEDICAMENTOS: {r.iloc[8]}\n{'-'*50}")
                
                st.download_button("📥 Descargar Historial Completo (PDF)", pdf.output(dest='S').encode('latin-1'), f"HC_{busqueda}.pdf", "application/pdf")

                for _, r in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small style='color: gray;'>📅 Fecha: {r.iloc[0]}</small><br>
                        <p style='margin-bottom:5px;'><b>Motivo:</b> {r.iloc[3]}</p>
                        <p style='margin-bottom:5px;'><b>Valoración:</b> {r.iloc[2]}</p>
                        <p style='margin-bottom:0;'><b>Medicamentos:</b> {r.iloc[8]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("El paciente no tiene evoluciones previas.")
        else:
            st.error("❌ Paciente no encontrado. Verifique que el número de documento sea correcto.")
