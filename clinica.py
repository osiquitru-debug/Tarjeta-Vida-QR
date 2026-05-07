import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
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

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def normalizar_texto(valor):
    if pd.isna(valor) or valor == "": return ""
    # Elimina decimales .0 y espacios en blanco para asegurar coincidencia
    return str(valor).split('.')[0].replace(" ", "").strip()

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Creamos la columna de búsqueda basada en la columna B (índice 1)
        p['BUSQUEDA_ID'] = p.iloc[:, 1].apply(normalizar_texto)
        h['BUSQUEDA_ID'] = h.iloc[:, 1].apply(normalizar_texto)
        
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
    st.write("Panel de gestión de historias clínicas.")

elif st.session_state.menu == "Registrar":
    st.title("REGISTRO DE PACIENTE")
    with st.form("f_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Numero Documento")
            edad = st.text_input("Edad")
        with col2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            e_nom = st.text_input("Contacto Emergencia")
            e_tel = st.text_input("Telefono Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": e_nom, "entry.2011749615": e_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("CONSULTA Y EVOLUCION")
    id_input = st.text_input("Documento del Paciente:").strip()
    id_clave = normalizar_texto(id_input)
    
    if id_clave and df_p is not None:
        resultado = df_p[df_p['BUSQUEDA_ID'] == id_clave]
        
        if not resultado.empty:
            p = resultado.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>PACIENTE: {p.iloc[2]}</h2>
                <p><b>ID:</b> {p.iloc[1]} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <p><b>EPS:</b> {p.iloc[5]}</p>
                <div class="emergency-box">EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("REGISTRAR EVOLUCION (10 CAMPOS)"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1=st.text_area("Valoracion"); v2=st.text_area("Motivo"); v3=st.text_input("Talla")
                        v4=st.text_input("Peso"); v5=st.text_input("Presion")
                    with c2:
                        v6=st.text_area("Antecedentes"); v7=st.text_area("Medicamentos")
                        v8=st.text_area("Laboratorios"); v9=st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EVOLUCION"):
                        e_pay = {
                            "entry.2019369477": id_clave, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_pay)
                        st.success("Evolucion guardada."); st.cache_data.clear(); st.rerun()

            st.subheader("HISTORIAL")
            h_res = df_h[df_h['BUSQUEDA_ID'] == id_clave].sort_index(ascending=False)
            if not h_res.empty:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"HC: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_res.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\n{'-'*30}")
                st.download_button("Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_clave}.pdf", "application/pdf")

                for _, r in h_res.iterrows():
                    st.markdown(f"""<div class="evo-card"><b>Fecha: {r.iloc[0]}</b><br>Motivo: {r.iloc[3]}</div>""", unsafe_allow_html=True)
        else:
            st.error("No se encuentra el paciente en la base de datos.")
