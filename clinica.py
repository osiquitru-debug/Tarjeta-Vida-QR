import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    input, textarea, select { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, label { text-align: center; color: #1a202c; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; text-align: left;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Leemos las hojas. Si falla el nombre, cargará la principal.
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Función de limpieza segura para evitar el error 'strip'
        def limpiar(txt):
            return str(txt).split('.')[0].replace(" ", "").strip()
        
        # Aplicamos la limpieza a la columna de Documento (Columna B / Índice 1)
        p['ID_KEY'] = p.iloc[:, 1].apply(limpiar)
        h['ID_KEY'] = h.iloc[:, 1].apply(limpiar)
        
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.markdown("### MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 TARJETA VIDA")
    st.info("Sistema médico para Guadalupe, Huila.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    with st.form("f_reg", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        documento = st.text_input("Documento")
        if st.form_submit_button("GUARDAR"):
            payload = {"entry.346175428": nombre, "entry.1302424820": documento}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Registrado correctamente."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    busqueda = st.text_input("Número de Documento").strip()
    
    if busqueda and df_p is not None:
        # Limpiamos el input igual que la base de datos
        id_buscado = busqueda.split('.')[0].replace(" ", "")
        p_row = df_p[df_p['ID_KEY'] == id_buscado]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h3>👤 {p.iloc[2]}</h3>
                <p><b>ID:</b> {p.iloc[1]} | <b>RH:</b> {p.iloc[6]} | <b>EPS:</b> {p.iloc[5]}</p>
            </div>""", unsafe_allow_html=True)
            
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo")
                    if st.form_submit_button("GUARDAR"):
                        h_pay = {"entry.2019369477": id_buscado, "entry.1088523869": v1, "entry.611862537": v2}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.iloc[0]}</small><br>
                        <b>Motivo:</b> {f.iloc[3]}<br>
                        <b>Valoración:</b> {f.iloc[2]}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No hay evoluciones.")
        else:
            st.error("No se encontró el paciente.")
