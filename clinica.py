import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Enlace directo de la imagen
LOGO_URL = "https://drive.google.com/uc?export=download&id=1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"

st.markdown(f"""
    <style>
    /* Fondo general basado en el logo */
    .stApp {{ background-color: #f8fafc !important; }}
    
    /* Barra lateral con tono oscuro profesional */
    [data-testid="stSidebar"] {{
        background-color: #1e293b !important;
        color: white;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}

    /* Estilo de Tarjetas - Borde cian como el logo */
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #22d3ee; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1e293b; text-align: left;
    }}
    .emergency-box {{
        background-color: #fff1f2; padding: 12px; border-radius: 8px;
        border: 1px dashed #f43f5e; color: #9f1239; font-weight: bold; margin-top: 10px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 5px solid #0891b2;
        margin-bottom: 10px; color: #334155; text-align: left;
    }}
    .grid-medidas {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; font-size: 0.9em; }}
    
    /* Botones con el color turquesa del logo */
    div.stButton > button:first-child {{
        background-color: #0891b2; color: white; border: none;
    }}
    div.stButton > button:hover {{
        background-color: #0e7490; color: white; border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        def limpiar(txt): return str(txt).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except Exception as e:
        st.error(f"Error al cargar base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=220)
    st.title("🩺 TARJETA VIDA")
    st.subheader("Sistema de Historias Clínicas")
    st.write("Guadalupe, Huila")

elif st.session_state.menu == "Registrar":
    st.image(LOGO_URL, width=120)
    st.title("📝 REGISTRO DE NUEVO PACIENTE")
    with st.form("form_registro_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
            edad = st.text_input("Edad")
        with col2:
            celular = st.text_input("Celular")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c_especiales = st.text_area("Condiciones Especiales (Alergias, Enfermedades de base)")
        st.subheader("Contacto de Emergencia")
        c_nom = st.text_input("Nombre Contacto Emergencia")
        c_tel = st.text_input("Teléfono Contacto Emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel,
            }
            try:
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success(f"✅ Paciente {nombre} registrado."); st.cache_data.clear()
            except: st.error("Error al enviar datos.")

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120)
    st.title("🔍 CONSULTA MÉDICA")
    busqueda_raw = st.text_input("Ingrese el Documento del Paciente").strip()
    id_buscado = busqueda_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p style='margin:5px 0;'><b>{p.get('TIPO DE DOCUMENTO')}:</b> {p.get('DOCUMENTO')} | <b>EDAD:</b> {p.get('EDAD')}</p>
                <p><b>EPS:</b> {p.get('EPS')} | <b>RH:</b> {p.get('RH')}</p>
                <p><b>⚠️ CONDICIONES:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            if not h_p.empty:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "HISTORIAL CLINICO - TARJETA VIDA", ln=True, align='C')
                st.download_button(label="📥 Descargar Historial PDF", data=pdf.output(dest='S').encode('latin-1'), file_name=f"HC_{id_buscado}.pdf", mime="application/pdf")

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v2 = st.text_area("2. Valoración"); v3 = st.text_area("3. Motivo Consulta")
                        v4 = st.text_input("4. Talla"); v5 = st.text_input("5. Peso")
                    with c2:
                        v6 = st.text_input("6. Presión Arterial"); v7 = st.text_area("7. Antecedentes")
                        v8 = st.text_area("8. Medicamentos"); v10 = st.text_area("10. Epicrisis")
                    if st.form_submit_button("GUARDAR REGISTRO"):
                        e_payload = {
                            "entry.2019369477": id_buscado, "entry.1088523869": v2, "entry.611862537": v3,
                            "entry.1275746503": v4, "entry.949747647": v5, "entry.2091389798": v6,
                            "entry.889985940": v7, "entry.2016051626": v8, "entry.616774918": v10
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 HISTORIAL DE EVOLUCIONES")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 <b>FECHA:</b> {f.get('MARCA TEMPORAL')}</small><br>
                        <b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}<br>
                        <b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}<br>
                        <div class="grid-medidas">
                            <span>📏 <b>Talla:</b> {f.get('4. TALLA')}</span>
                            <span>⚖️ <b>Peso:</b> {f.get('5. PESO')}</span>
                            <span>🩸 <b>P.A.:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p>💊 <b>MEDICAMENTOS:</b> {f.get('8. MEDICAMENTOS')}</p>
                    </div>""", unsafe_allow_html=True)
            else: st.info("Sin evoluciones.")
        else: st.error(f"No se encontró el documento: {id_buscado}")
