import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL (ESTILO PROFESIONAL) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# Enlace estable del logo
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4fafa !important; }}
    
    /* Formato Tarjeta Paciente */
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #22d3ee; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1e293b; text-align: left;
    }}
    /* Formato Alerta Emergencia */
    .emergency-box {{
        background-color: #fff1f2; padding: 12px; border-radius: 8px;
        border: 1px dashed #f43f5e; color: #9f1239; font-weight: bold; margin-top: 10px;
    }}
    /* Formato Tarjeta Evolución */
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 5px solid #0891b2;
        margin-bottom: 10px; color: #334155; text-align: left;
    }}
    .grid-medidas {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; font-size: 0.9em; }}
    
    div.stButton > button:first-child {{
        background-color: #0891b2; color: white; border: none; font-weight: bold;
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
        st.error(f"Error de sistema: {e}")
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
    st.image(LOGO_URL, width=250) # Imagen sobre el título
    st.title("🩺 TARJETA VIDA")
    st.write("### *Intelligence Healthcare Management*")
    st.write("Sistema de Historias Clínicas - Guadalupe, Huila")

elif st.session_state.menu == "Registrar":
    st.image(LOGO_URL, width=120) # Imagen sobre el título
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            tipo_doc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        c_esp = st.text_area("Condiciones Especiales / Alergias")
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre de Contacto")
        c_tel = st.text_input("Teléfono de Contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": tipo_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            try:
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
                st.success("Registrado correctamente."); st.cache_data.clear()
            except: st.error("Error al guardar.")

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120) # Imagen sobre el título
    st.title("🔍 CONSULTA MÉDICA")
    id_buscado_raw = st.text_input("Ingrese el Documento del Paciente").strip()
    id_buscado = id_buscado_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA DE PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>{p.get('TIPO DE DOCUMENTO')}:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EDAD:</b> {p.get('EDAD')}</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            # REGISTRO DE NUEVA EVOLUCIÓN
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        v_val = st.text_area("Valoración Física")
                        v_mot = st.text_area("Motivo de Consulta")
                        v_tal = st.text_input("Talla (cm)")
                        v_pes = st.text_input("Peso (kg)")
                    with col_e2:
                        v_pre = st.text_input("Presión Arterial")
                        v_ant = st.text_area("Antecedentes")
                        v_med = st.text_area("Medicamentos / Fórmula")
                        v_epi = st.text_area("Epicrisis / Notas")
                    
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        e_payload = {
                            "entry.2019369477": id_buscado, "entry.1088523869": v_val, "entry.611862537": v_mot,
                            "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre,
                            "entry.889985940": v_ant, "entry.2016051626": v_med, "entry.616774918": v_epi
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Evolución guardada."); st.cache_data.clear(); st.rerun()

            # HISTORIAL EN TARJETAS DE EVOLUCIÓN
            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                        <b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}<br>
                        <b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}<br>
                        <div class="grid-medidas">
                            <span>📏 Talla: {f.get('4. TALLA')}</span>
                            <span>⚖️ Peso: {f.get('5. PESO')}</span>
                            <span>🩸 P.A.: {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p>💊 <b>Tratamiento:</b> {f.get('8. MEDICAMENTOS')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Sin registros previos.")
        else:
            st.error("No se encontró el paciente.")
