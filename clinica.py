import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-left: 8px solid #10b981; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px; color: #1e293b;
    }
    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #e2e8f0; margin-bottom: 10px; color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- URLs ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        # Limpieza de Documentos
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

st.title("🩺 Evolución Médica")

id_bus = st.text_input("Documento del Paciente").strip()

if id_bus and df_p is not None:
    paciente = df_p[df_p["DOCUMENTO"] == id_bus]
    
    if not paciente.empty:
        p = paciente.iloc[0]
        st.markdown(f"""<div class="medical-card">
            <h3>👤 {p.get('NOMBRE', 'N/A')}</h3>
            <p>ID: {id_bus} | RH: {p.get('RH', 'N/A')} | EPS: {p.get('EPS', 'N/A')}</p>
        </div>""", unsafe_allow_html=True)

        # FORMULARIO DE EVOLUCIÓN (Solo los 9 campos del Formulario de Google)
        with st.expander("📝 REGISTRAR EVOLUCIÓN"):
            with st.form("evo_form", clear_on_submit=True):
                # Campo Documento (Oculto/Automático para vincular)
                
                # Campos según el orden y IDs de tu formulario
                diagnostico = st.text_area("Diagnóstico")
                tratamiento = st.text_input("Tratamiento")
                medicamentos = st.text_area("Medicamentos")
                procedimientos = st.text_area("Procedimientos")
                evolucion_clinica = st.text_area("Evolución Clínica")
                recomendaciones = st.text_area("Recomendaciones")
                notas_enfermeria = st.text_area("Notas de Enfermería")
                examenes = st.text_input("Exámenes")
                observaciones = st.text_input("Observaciones")

                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    payload = {
                        "entry.2019369477": id_bus,            # Documento
                        "entry.889985940": diagnostico,
                        "entry.611862537": tratamiento,
                        "entry.2016051626": medicamentos,
                        "entry.1088523869": procedimientos,
                        "entry.1275746503": evolucion_clinica,
                        "entry.882053172": recomendaciones,
                        "entry.949747647": notas_enfermeria,
                        "entry.616774918": examenes,
                        "entry.2091389798": observaciones
                    }
                    requests.post(URL_FORM_HISTORIAL, data=payload)
                    st.success("✅ Registrado")
                    st.cache_data.clear()
                    st.rerun()

        # VISUALIZACIÓN DEL HISTORIAL (Solo campos existentes en el Sheet)
        st.subheader("📋 Historial")
        h_p = df_h[df_h["DOCUMENTO"] == id_bus] if df_h is not None else pd.DataFrame()
        
        if not h_p.empty:
            for _, fila in h_p.sort_index(ascending=False).iterrows():
                st.markdown(f"""<div class="evo-card">
                    <small>📅 {fila.get('MARCA TEMPORAL', '')}</small><br>
                    <b>Diagnóstico:</b> {fila.get('DIAGNOSTICO', 'N/R')}<br>
                    <b>Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/R')}<br>
                    <b>Evolución:</b> {fila.get('EVOLUCION CLINICA', 'N/R')}
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Paciente no encontrado.")
