import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    
    /* Textos en negro absoluto */
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{ color: #000000 !important; }}

    /* Inputs: Fondo blanco y letra negra */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Botones Verde Menta */
    div.stButton > button {{
        background-color: #98FF98 !important; 
        color: #000000 !important; 
        border-radius: 12px !important; 
        font-weight: bold !important; 
        border: 1px solid #7ed37e !important;
        height: 3em !important;
        width: 100% !important;
    }}

    /* Tarjetas */
    .medical-card {{
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 25px;
    }}
    .emergency-box {{
        background-color: #ffe5d9; padding: 15px; border-radius: 10px;
        border: 2px dashed #f43f5e; color: #b91c1c !important; font-weight: bold; margin-top: 15px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 18px; border-radius: 12px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 15px;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 10px 0; padding: 10px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
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
        # Normalizar para búsqueda robusta
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("---")
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta Médica"): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
# IMAGEN SOBRE EL TÍTULO EN TODAS LAS VISTAS
st.image(LOGO_URL, width=180)

if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.info("Bienvenido al sistema de gestión clínica offline/online.")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Documento", ["CC", "TI", "CE", "RC"])
            ndoc = st.text_input("Número de Documento")
        with col2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        alertas = st.text_area("Condiciones Especiales (Alergias, Enfermedades de base)")
        st.subheader("🚨 Contacto de Emergencia")
        c_nom = st.text_input("Nombre de Referencia")
        c_tel = st.text_input("Teléfono de Referencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            # Mapeo según tu Google Form de Pacientes
            payload = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado exitosamente."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento del Paciente").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA COMPLETA
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p style='font-size:1.1em;'><b>ID:</b> {p.get('DOCUMENTO')} | <b>EDAD:</b> {p.get('EDAD')} años | <b>RH:</b> {p.get('RH')}</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p><b>⚠️ ALERTAS CRÍTICAS:</b><br>{p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 CONTACTO DE EMERGENCIA:<br>{p.get('NOMBRE CONTACTO EMERGENCIA')} — 📞 {p.get('TELÉFONO CONTACTO EMERGENCIA')}</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- PDF CON LOGO ARRIBA ---
            pdf = FPDF()
            pdf.add_page()
            try: pdf.image(LOGO_URL, 10, 8, 33)
            except: pass
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Reporte Tarjeta Vida QR", ln=True, align='C')
            pdf.ln(15)
            
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "INFORMACION GENERAL", 1, 1, 'L', 1)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 7, f"Paciente: {p.get('NOMBRE')}\nDocumento: {p.get('DOCUMENTO')} | RH: {p.get('RH')}\nAlertas: {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}")
            pdf.ln(5)

            if not h_p.empty:
                pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "HISTORIAL DE EVOLUCIONES", 1, 1, 'L', 1)
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 7, f"FECHA: {f.get('MARCA TEMPORAL')}", 0, 1)
                    pdf.set_font("Arial", '', 9)
                    pdf.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACION: {f.get('2. VALORACIÓN')}\nTRATAMIENTO: {f.get('8. MEDICAMENTOS')}\nNOTAS: {f.get('9. EPICRISIS O NOTAS ADICIONALES')}")
                    pdf.ln(2); pdf.cell(0, 0, "", 'T', 1); pdf.ln(2)

            st.download_button("📥 Descargar Historia Clínica (PDF)", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # --- NUEVA EVOLUCIÓN ---
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_mot = st.text_area("3. Motivo de Consulta")
                        e_val = st.text_area("2. Valoración")
                        e_tal = st.text_input("4. Talla (cm)")
                    with c2:
                        e_pes = st.text_input("5. Peso (kg)")
                        e_pre = st.text_input("6. Presión Arterial")
                        e_med = st.text_area("8. Medicamentos / Tratamiento")
                        e_not = st.text_area("9. Epicrisis / Notas")
                    
                    if st.form_submit_button("GUARDAR REGISTRO MÉDICO"):
                        data_evo = {
                            "entry.2019369477": id_buscado, "entry.611862537": e_mot, "entry.1088523869": e_val,
                            "entry.1275746503": e_tal, "entry.949747647": e_pes, "entry.2091389798": e_pre,
                            "entry.2016051626": e_med, "entry.616774918": e_not
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_evo)
                        st.success("✅ Evolución guardada."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL EN PANTALLA ---
            st.subheader("📋 Evoluciones Recientes")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 FECHA: {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')} cm</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')} kg</span>
                            <span><b>🩸 Tensión:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>💊 TRATAMIENTO:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p style='font-size:0.9em; color:#333; border-top:1px solid #eee; padding-top:5px;'>
                        <b>📝 NOTAS/EPICRISIS:</b><br>{f.get('9. EPICRISIS O NOTAS ADICIONALES')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No hay registros de evolución para este paciente.")
        else:
            st.error("Paciente no encontrado. Verifique el número de documento.")
