import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL MEJORADA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 12px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold; margin-top: 10px;
    }
    .evo-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e2e8f0; border-top: 5px solid #63b3ed;
        margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .evo-header { display: flex; justify-content: space-between; border-bottom: 1px solid #edf2f7; padding-bottom: 8px; margin-bottom: 12px; }
    .section-title { color: #2b6cb0; font-weight: bold; font-size: 0.85em; text-transform: uppercase; margin-top: 10px; margin-bottom: 2px; }
    .grid-medidas { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; background: #f8fafc; padding: 10px; border-radius: 8px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (SIN TOCAR LA LÓGICA FUNCIONAL) ---
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
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.title("🩺 MENÚ")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.title("🩺 TARJETA VIDA")
    st.subheader("Gestión Clínica - Guadalupe, Huila")
    st.info("Seleccione una opción en el menú lateral para comenzar.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("form_registro", clear_on_submit=True):
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
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA MÉDICA")
    busqueda_raw = st.text_input("Documento del Paciente").strip()
    id_buscado = busqueda_raw.split('.')[0].replace(" ", "").strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p style='margin:5px 0;'><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EDAD:</b> {p.get('EDAD')}</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p style='color:#e53e3e;'><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            if not h_p.empty:
                # Botón PDF (Mantenemos la descarga funcional)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"HISTORIAL: {p.get('NOMBRE')}", ln=True); pdf.ln(5)
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, f"FECHA: {f.get('MARCA TEMPORAL')}", ln=True)
                    pdf.set_font("Arial", size=9); pdf.multi_cell(0, 5, f"VALORACION: {f.get('2. VALORACIÓN')}\nMOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nMEDICAMENTOS: {f.get('8. MEDICAMENTOS')}\n\n")
                st.download_button("📥 Descargar PDF Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf", "application/pdf")

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v2 = st.text_area("2. Valoración"); v3 = st.text_area("3. Motivo Consulta")
                        v4 = st.text_input("4. Talla"); v5 = st.text_input("5. Peso")
                    with c2:
                        v6 = st.text_input("6. Presión Arterial"); v7 = st.text_area("7. Antecedentes")
                        v8 = st.text_area("8. Medicamentos"); v10 = st.text_area("10. Epicrisis")
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        e_payload = {
                            "entry.2019369477": id_buscado, "entry.1088523869": v2, "entry.611862537": v3,
                            "entry.1275746503": v4, "entry.949747647": v5, "entry.2091389798": v6,
                            "entry.889985940": v7, "entry.2016051626": v8, "entry.616774918": v10
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=e_payload)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # --- TARJETAS DE EVOLUCIÓN MEJORADAS ---
            st.subheader("📋 HISTORIAL DETALLADO")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <div class="evo-header">
                            <span style="color:#4a5568; font-weight:bold;">📅 {f.get('MARCA TEMPORAL')}</span>
                            <span style="background:#ebf8ff; color:#2b6cb0; padding:2px 8px; border-radius:15px; font-size:0.8em;">Consulta Médica</span>
                        </div>
                        
                        <div class="section-title">🩺 Motivo de Consulta</div>
                        <p style="margin-bottom:10px;">{f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        
                        <div class="section-title">🧠 Valoración y Hallazgos</div>
                        <p>{f.get('2. VALORACIÓN')}</p>
                        
                        <div class="grid-medidas">
                            <div><b>Talla:</b> {f.get('4. TALLA')}</div>
                            <div><b>Peso:</b> {f.get('5. PESO')}</div>
                            <div><b>P. Arterial:</b> {f.get('6. PRESIÓN ARTERIAL')}</div>
                        </div>

                        <div class="section-title">📜 Antecedentes / Notas Médicas</div>
                        <p style="font-size:0.9em; color:#4a5568;">{f.get('7. ANTECEDENTES MEDICOS')}</p>
                        
                        <div class="section-title">💊 Tratamiento y Medicamentos</div>
                        <p style="background:#f0fff4; padding:8px; border-radius:5px; border:1px solid #c6f6d5;">{f.get('8. MEDICAMENTOS')}</p>
                        
                        <div class="section-title">📝 Epicrisis Final</div>
                        <p style="font-style: italic; color:#2d3748;">{f.get('10. EPICRISIS')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Sin registros.")
        else: st.error("No encontrado.")
