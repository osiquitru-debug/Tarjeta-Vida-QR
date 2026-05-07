import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

# --- 2. CARGA DE DATOS (BÚSQUEDA BLINDADA) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def normalizar_id(valor):
    """Convierte cualquier ID a texto puro, quitando decimales y espacios."""
    if pd.isna(valor) or valor == "": return ""
    return str(valor).split('.')[0].replace(" ", "").strip()

@st.cache_data(ttl=1)
def cargar_tablas():
    try:
        # Forzamos lectura como texto
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # CREACIÓN DE LLAVES DE BÚSQUEDA (Columna B de tus sheets)
        p['ID_KEY'] = p.iloc[:, 1].apply(normalizar_id)
        h['ID_KEY'] = h.iloc[:, 1].apply(normalizar_id)
        
        return p, h
    except:
        return None, None

df_p, df_h = cargar_tablas()

# --- 3. NAVEGACIÓN (BOTONES ORIGINALES) ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("BIENVENIDO A TARJETA VIDA")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    with st.form("f_registro"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tipo = st.selectbox("Tipo Doc", ["CC", "TI", "RC", "CE"])
            doc = st.text_input("Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_nom = st.text_input("Contacto Emergencia")
        c_tel = st.text_input("Teléfono Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nom, "entry.1650757004": tipo, "entry.1302424820": doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Registrado correctamente."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_input = st.text_input("Documento del Paciente:").strip()
    id_busqueda = normalizar_id(id_input)
    
    if id_busqueda and df_p is not None:
        p_res = df_p[df_p["ID_KEY"] == id_busqueda]
        
        if not p_res.empty:
            p = p_res.iloc[0]
            # MOSTRAR DATOS
            st.write(f"### 👤 {p.iloc[2]}")
            st.write(f"**ID:** {p.iloc[1]} | **Edad:** {p.iloc[4]} | **RH:** {p.iloc[6]}")
            st.error(f"🚨 EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}")

            # FORMULARIO EVOLUCIÓN (10 CAMPOS)
            with st.expander("✍️ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        v1 = st.text_area("Valoración"); v2 = st.text_area("Motivo")
                        v3 = st.text_input("Talla"); v4 = st.text_input("Peso")
                    with col_b:
                        v5 = st.text_area("Antecedentes"); v6 = st.text_area("Medicamentos")
                        v7 = st.text_area("Laboratorios"); v8 = st.text_area("Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        h_payload = {
                            "entry.2019369477": id_busqueda, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.889985940": v5, 
                            "entry.2016051626": v6, "entry.882053172": v7, "entry.616774918": v8
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_payload)
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            # HISTORIAL Y PDF
            st.subheader("📋 HISTORIAL")
            h_res = df_h[df_h["ID_KEY"] == id_busqueda].sort_index(ascending=False)
            
            if not h_res.empty:
                # PDF simple
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"HISTORIA CLINICA: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_res.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\n{'-'*30}")
                st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_busqueda}.pdf", "application/pdf")

                for _, r in h_res.iterrows():
                    with st.container():
                        st.write(f"**Fecha:** {r.iloc[0]}")
                        st.write(f"*Valoración:* {r.iloc[2]}")
                        st.write("---")
            else:
                st.info("Sin evoluciones registradas.")
        else:
            st.error("No se encontró el paciente. Verifique el número en su Excel.")
