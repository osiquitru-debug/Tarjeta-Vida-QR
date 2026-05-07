import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# --- 2. CARGA DE DATOS (Lógica Simplificada) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargamos las hojas como texto
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Creamos una clave de búsqueda quitando decimales y espacios
        p['ID_KEY'] = p.iloc[:, 1].apply(lambda x: str(x).split('.')[0].strip())
        h['ID_KEY'] = h.iloc[:, 1].apply(lambda x: str(x).split('.')[0].strip())
        
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("SISTEMA MÉDICO")
    st.write("Panel de control.")

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    busqueda = st.text_input("Número de Documento").strip()
    
    if busqueda and df_p is not None:
        # Limpiamos el input del usuario para comparar
        id_buscado = busqueda.split('.')[0].strip()
        p_row = df_p[df_p['ID_KEY'] == id_buscado]
        
        if not p_row.empty:
            p = p_row.iloc[0]
            st.success("Paciente encontrado")
            # Mostramos datos básicos por posición para evitar errores de nombre
            st.subheader(f"👤 {p.iloc[2]}") # Nombre
            st.write(f"**ID:** {p.iloc[1]} | **RH:** {p.iloc[6]} | **EPS:** {p.iloc[5]}")

            with st.expander("📝 REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo"):
                    v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo")
                    if st.form_submit_button("GUARDAR"):
                        h_pay = {"entry.2019369477": id_buscado, "entry.1088523869": v1, "entry.611862537": v2}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.info(f"📅 {f.iloc[0]} | Motivo: {f.iloc[3]} | Valoración: {f.iloc[2]}")
            else:
                st.write("No hay registros.")
        else:
            st.error("No se encontró el paciente.")
