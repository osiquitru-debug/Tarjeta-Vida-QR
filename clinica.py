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
    
    /* Celdas blancas con letra negra */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
        color: #000000;
    }}
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 1px dashed #f43f5e; color: #b91c1c; font-weight: bold; margin-top: 10px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
        color: #000000;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; color: gray; font-size: 0.8em; padding: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (MANTENIENDO NOMBRES ORIGINALES) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargamos sin forzar mayúsculas para respetar los títulos del sheet
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        
        # Limpieza técnica de IDs para la búsqueda
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO")
    with st.form("f_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            ndoc = st.text_input("Documento")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        cesp = st.text_area("Condiciones Especiales / Alergias")
        
        st.subheader("🚨 Contacto de Emergencia")
        c1e, c2e = st.columns(2)
        with c1e: cnom = st.text_input("Nombre de Referencia")
        with c2e: ctel = st.text_input("Teléfono de Referencia")
        
        if st.form_submit_button("GUARDAR"):
            payload = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, 
                "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, 
                "entry.1892763134": cnom, "entry.2011749615": ctel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_buscado = st.text_input("Documento").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p['NOMBRE']}</h2>
                <p><b>ID:</b> {p['DOCUMENTO']} | <b>RH:</b> {p['RH']} | <b>EDAD:</b> {p['EDAD']}</p>
                <p><b>EPS:</b> {p['EPS']}</p>
                <p><b>⚠️ ALERTAS:</b> {p['CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)']}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p['NOMBRE CONTACTO EMERGENCIA']} ({p['TELEFONO CONTACTO EMERGENCIA']})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- PDF MEJORADO ---
            pdf = FPDF()
            pdf.add_page()
            try: pdf.image(LOGO_URL, 10, 8, 30)
            except: pass
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Tarjeta Vida QR", ln=True, align='C')
            pdf.set_font("Arial", 'I', 10); pdf.cell(0, 10, "Tu Informacion de Salud Siempre Contigo", ln=True, align='C')
            pdf.ln(10)
            
            # Ficha en PDF
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"PACIENTE: {p['NOMBRE']}", 1, 1, 'L')
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 7, f"Documento: {p['DOCUMENTO']} | RH: {p['RH']}", 0, 1)
            pdf.multi_cell(0, 7, f"Alertas: {p['CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)']}")
            pdf.ln(5)

            # Evoluciones en PDF con títulos exactos
            if not h_p.empty:
                pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "HISTORIAL DE EVOLUCIONES", 1, 1, 'C')
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 7, f"FECHA: {f['Marca temporal']}", 0, 1)
                    pdf.set_font("Arial", '', 9)
                    pdf.multi_cell(0, 5, f"MOTIVO: {f['3. MOTIVO DE LA CONSULTA']}")
                    pdf.multi_cell(0, 5, f"VALORACION: {f['2. VALORACIÓN']}")
                    pdf.cell(0, 5, f"MEDIDAS: Talla: {f['4. TALLA']} | Peso: {f['5. PESO']} | TA: {f['6. PRESIÓN ARTERIAL']}", 0, 1)
                    pdf.multi_cell(0, 5, f"TRATAMIENTO: {f['8. MEDICAMENTOS']}")
                    pdf.multi_cell(0, 5, f"NOTAS: {f['9. EPICRISIS O NOTAS ADICIONALES']}")
                    pdf.ln(2); pdf.cell(0, 0, "", 'T', 1); pdf.ln(2)

            st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # --- HISTORIAL EN PANTALLA ---
            st.subheader("📋 Evoluciones Recientes")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f['Marca temporal']}</small><br>
                        <p style='margin:5px 0;'><b>MOTIVO:</b> {f['3. MOTIVO DE LA CONSULTA']}</p>
                        <p style='margin:5px 0;'><b>VALORACIÓN:</b> {f['2. VALORACIÓN']}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f['4. TALLA']}</span>
                            <span><b>⚖️ Peso:</b> {f['5. PESO']}</span>
                            <span><b>🩸 Tensión:</b> {f['6. PRESIÓN ARTERIAL']}</span>
                        </div>
                        <p style='margin:5px 0;'><b>💊 TRATAMIENTO:</b> {f['8. MEDICAMENTOS']}</p>
                        <p style='margin:5px 0; font-size:0.85em; color:#555;'><b>NOTAS:</b> {f['9. EPICRISIS O NOTAS ADICIONALES']}</p>
                    </div>""", unsafe_allow_html=True)
