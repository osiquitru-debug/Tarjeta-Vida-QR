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
    /* Fondo y texto general */
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
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
        border-radius: 10px !important; 
        font-weight: bold !important; 
        border: 1px solid #7ed37e !important;
    }}
    
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 1px dashed #f43f5e; color: #b91c1c !important; font-weight: bold; margin-top: 10px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    }}
    .footer {{ 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        text-align: center; color: #555555 !important; font-size: 0.8em; padding: 10px;
        background-color: rgba(255,255,255,0.5);
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
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---

# Imagen sobre los títulos en todas las secciones
st.image(LOGO_URL, width=220)

if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
            cel = st.text_input("Celular")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alert = st.text_area("Condiciones Especiales (Alergias, Enfermedades de base)")
        st.subheader("🚨 Emergencia")
        enom = st.text_input("Nombre Contacto"); etel = st.text_input("Teléfono Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel, "entry.celular_id": cel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    id_buscado = st.text_input("Ingrese Documento").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>EDAD:</b> {p.get('EDAD')} | <b>RH:</b> {p.get('RH')}</p>
                <p><b>EPS:</b> {p.get('EPS')} | <b>CEL:</b> {p.get('CELULAR')}</p>
                <p><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELÉFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- PDF ---
            pdf = FPDF()
            pdf.add_page()
            try: pdf.image(LOGO_URL, 10, 8, 30)
            except: pass
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "Reporte Historia Clinica - Tarjeta Vida QR", ln=True, align='C')
            pdf.set_font("Arial", '', 10); pdf.cell(0, 7, f"Paciente: {p.get('NOMBRE')} | ID: {p.get('DOCUMENTO')}", ln=True)
            pdf.ln(5)

            if not h_p.empty:
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 7, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, 'L')
                    pdf.set_font("Arial", '', 9)
                    pdf.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\nVALORACION: {f.get('2. VALORACIÓN')}\nANTECEDENTES: {f.get('7. ANTECEDENTES MEDICOS')}\nMEDICAMENTOS: {f.get('8. MEDICAMENTOS')}\nLABS: {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}\nEPICRISIS: {f.get('10. EPICRISIS')}")
                    pdf.ln(3)

            st.download_button("📥 Descargar Reporte PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # --- NUEVA EVOLUCIÓN ---
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1: 
                        v_mot = st.text_area("3. Motivo"); v_val = st.text_area("2. Valoración"); v_ant = st.text_area("7. Antecedentes"); v_tal = st.text_input("4. Talla")
                    with c2:
                        v_pes = st.text_input("5. Peso"); v_pre = st.text_input("6. Presión"); v_med = st.text_area("8. Medicamentos"); v_lab = st.text_area("9. Laboratorios"); v_epi = st.text_area("10. Epicrisis")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        data_e = {"entry.2019369477": id_buscado, "entry.611862537": v_mot, "entry.1088523869": v_val, "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre, "entry.2016051626": v_med, "entry.616774918": v_epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_e)
                        st.success("✅ Guardado."); st.cache_data.clear(); st.rerun()

            # --- HISTORIAL EN PANTALLA ---
            st.subheader("📋 Evoluciones")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>💊 MEDICAMENTOS:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p><b>🔬 LABS:</b> {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}</p>
                        <p style='font-size:0.9em; color:#444; border-top:1px solid #eee; padding-top:5px;'>
                            <b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}
                        </p>
                    </div>""", unsafe_allow_html=True)
