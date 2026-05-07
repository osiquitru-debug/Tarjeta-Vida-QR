import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 10px; border-radius: 10px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
        text-align: center;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIONES DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def limpiar_id(txt):
    if pd.isna(txt): return ""
    return str(txt).split('.')[0].replace(" ", "").replace(",", "").strip()

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        # Normalizamos IDs para la búsqueda
        p['ID_KEY'] = p.iloc[:, 1].apply(limpiar_id)
        h['ID_KEY'] = h.iloc[:, 1].apply(limpiar_id)
        return p, h
    except:
        return None, None

df_p, df_h = cargar_tablas()

# --- 3. INTERFAZ ---
st.sidebar.title("🩺 Menú")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Registro", "Consulta"])

if opcion == "Inicio":
    st.title("Sistema Médico Tarjeta Vida")
    st.info("Seleccione una opción en el menú lateral para comenzar.")

elif opcion == "Registro":
    st.title("📝 Nuevo Paciente")
    with st.form("f_reg", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nombre")
            tipo = st.selectbox("Tipo", ["CC", "TI", "RC"])
            doc = st.text_input("Documento")
            edad = st.text_input("Edad")
        with col2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            enom = st.text_input("Contacto Emergencia")
            etel = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR"):
            data = {
                "entry.346175428": nom, "entry.1650757004": tipo, "entry.1302424820": doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": enom, "entry.2011749615": etel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=data)
            st.success("Registrado."); st.cache_data.clear()

elif opcion == "Consulta":
    st.title("🔍 Consulta")
    buscar = st.text_input("Documento del paciente:")
    id_ref = limpiar_id(buscar)
    
    if buscar and df_p is not None:
        p_res = df_p[df_p["ID_KEY"] == id_ref]
        
        if not p_res.empty:
            p = p_res.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.iloc[2]}</h3>
                <p><b>ID:</b> {p.iloc[1]} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <div class="emergency-box">🚨 {p.iloc[7]}: {p.iloc[8]}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("➕ Agregar Evolución"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1=st.text_area("Valoración"); v2=st.text_area("Motivo"); v3=st.text_input("Talla")
                    with c2:
                        v4=st.text_area("Antecedentes"); v5=st.text_area("Medicamentos"); v6=st.text_input("Peso")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        e_data = {
                            "entry.2019369477": id_ref, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v6, "entry.889985940": v4, "entry.2016051626": v5
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_data)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            st.subheader("Historial")
            h_res = df_h[df_h["ID_KEY"] == id_ref].sort_index(ascending=False)
            for _, r in h_res.iterrows():
                st.markdown(f"""<div class="evo-card"><b>📅 {r.iloc[0]}</b><br>{r.iloc[2]}</div>""", unsafe_allow_html=True)
        else:
            st.error("No encontrado. Revise el número en el Excel.")
