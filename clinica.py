import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
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
    .alerta-roja { color: #e53e3e; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (MANTENIENDO LÓGICA FUNCIONAL) ---
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
    except: return None, None

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
    st.subheader("Guadalupe, Huila")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    # ... (Mismo formulario anterior para no saturar)

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    busqueda = st.text_input("Documento").strip()
    id_buscado = busqueda.split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            st.markdown(f"""<div class="medical-card">
                <h2>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>EPS:</b> {p.get('EPS')}</p>
                <div class="emergency-box">🚨 {p.get('NOMBRE CONTACTO EMERGENCIA')}: {p.get('TELEFONO CONTACTO EMERGENCIA')}</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- MEJORA DE TARJETA DE EVOLUCIÓN ---
            st.subheader("📋 HISTORIAL DE EVOLUCIONES")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    # Lógica de Alerta de Presión
                    presion = str(f.get('6. PRESIÓN ARTERIAL'))
                    clase_presion = "alerta-roja" if "/" in presion and int(presion.split('/')[-1]) >= 140 else ""
                    
                    st.markdown(f"""
                    <div class="evo-card">
                        <div class="evo-header">
                            <span style="color:#4a5568; font-weight:bold;">📅 {f.get('MARCA TEMPORAL')}</span>
                            <span style="background:#f0fff4; color:#2f855a; padding:2px 8px; border-radius:15px; font-size:0.8em;">Registro Clínico</span>
                        </div>
                        
                        <div class="section-title">🩺 Motivo de Consulta</div>
                        <p style="margin-bottom:10px;">{f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        
                        <div class="section-title">🧠 Valoración y Hallazgos</div>
                        <p>{f.get('2. VALORACIÓN')}</p>
                        
                        <div class="grid-medidas">
                            <div><b>Talla:</b> {f.get('4. TALLA')} cm</div>
                            <div><b>Peso:</b> {f.get('5. PESO')} kg</div>
                            <div class="{clase_presion}"><b>P. Arterial:</b> {presion}</div>
                        </div>

                        <div class="section-title">📜 Antecedentes y Notas</div>
                        <p style="font-size:0.9em; color:#4a5568; border-left: 3px solid #cbd5e0; padding-left: 10px;">{f.get('7. ANTECEDENTES MEDICOS')}</p>
                        
                        <div class="section-title">💊 Tratamiento y Medicamentos</div>
                        <p style="background:#ebf8ff; padding:10px; border-radius:8px; border:1px solid #bee3f8; color:#2c5282;">{f.get('8. MEDICAMENTOS')}</p>
                        
                        <div class="section-title">📝 Epicrisis / Plan</div>
                        <p style="font-style: italic; color:#2d3748; background:#fffaf0; padding:10px; border-radius:8px;">{f.get('10. EPICRISIS')}</p>
                        
                        <div class="section-title">🧪 Laboratorios / Procedimientos</div>
                        <p style="font-size:0.85em;">{f.get('9. LABORATORIOS - PROCEDIMIENTOS')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Sin registros.")
        else: st.error("No encontrado.")
