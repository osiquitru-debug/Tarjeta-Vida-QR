import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    /* Casillas blancas con letras negras */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Títulos centrados */
    h1, h2, h3, label { text-align: center; color: #1a202c; }
    
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; text-align: left;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold; text-align: center;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS CON NORMALIZACIÓN (BÚSQUEDA ROBUSTA) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def normalizar_id(valor):
    """Limpia el documento de decimales y espacios para evitar errores de busqueda."""
    if pd.isna(valor) or valor == "": return ""
    return str(valor).split('.')[0].replace(" ", "").replace(",", "").strip()

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        # Forzar lectura como texto
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Crear llaves de busqueda normalizadas
        p['LLAVE'] = p.iloc[:, 1].apply(normalizar_id)
        h['LLAVE'] = h.iloc[:, 1].apply(normalizar_id)
        
        return p, h
    except:
        return None, None

df_p, df_h = cargar_tablas()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>MENU</h2>", unsafe_allow_html=True)
    if st.button("Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("Consulta / Evolucion", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("SISTEMA MEDICO TARJETA VIDA")
    st.info("Utilice el menú lateral para gestionar la información.")

elif st.session_state.menu == "Registrar":
    st.title("REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Numero de Documento")
            edad = st.text_input("Edad")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            c_nom = st.text_input("Nombre Contacto Emergencia")
            c_tel = st.text_input("Telefono Contacto Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Registrado correctamente."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("CONSULTA Y EVOLUCION")
    buscar_id = st.text_input("Ingrese Documento del Paciente:").strip()
    id_limpio = normalizar_id(buscar_id)
    
    if id_limpio and df_p is not None:
        p_match = df_p[df_p['LLAVE'] == id_limpio]
        
        if not p_match.empty:
            p = p_match.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>PACIENTE: {p.iloc[2]}</h2>
                <p><b>ID:</b> {p.iloc[1]} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <p><b>EPS:</b> {p.iloc[5]}</p>
                <div class="emergency-box">
                    EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("REGISTRAR NUEVA EVOLUCION"):
                with st.form("f_evo", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        v1 = st.text_area("1. Valoracion"); v2 = st.text_area("2. Motivo de Consulta")
                        v3 = st.text_input("3. Talla"); v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presion")
                    with col2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        h_pay = {
                            "entry.2019369477": id_limpio, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("Evolucion guardada."); st.cache_data.clear(); st.rerun()

            st.subheader("HISTORIAL MEDICO")
            h_p = df_h[df_h['LLAVE'] == id_limpio].sort_index(ascending=False)
            
            if not h_p.empty:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"HC: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_p.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\n{'-'*50}")
                
                st.download_button("Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_limpio}.pdf", "application/pdf")

                for _, r in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>Fecha: {r.iloc[0]}</small><br>
                        <b>Motivo:</b> {r.iloc[3]}<br>
                        <b>Valoracion:</b> {r.iloc[2]}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Sin registros previos.")
        else:
            st.error("Paciente no encontrado. Revise el numero en el Sheet.")
