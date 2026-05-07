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
    /* Fondo general y color de texto base */
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    
    /* Forzar texto negro en toda la app */
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{
        color: #000000 !important;
    }}

    /* Celdas de entrada: Fondo blanco, texto negro y borde gris */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Tarjetas de información */
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
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; color: gray !important; font-size: 0.8em; padding: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (CON NORMALIZACIÓN FORZADA) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        
        # NORMALIZACIÓN TOTAL: Quitamos espacios y pasamos a MAYÚSCULAS
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        
        # Identificamos las llaves de búsqueda
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        # En el historial la columna se llama "1. DOCUMENTO" -> Normalizada es "1. DOCUMENTO"
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        
        return p, h
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta Médica", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad"); eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        alertas = st.text_area("Condiciones Especiales / Alergias")
        st.subheader("🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre Referencia"); e_tel = st.text_input("Teléfono Referencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            # Enviar a Google Forms
            payload = {"entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": doc, "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh, "entry.1892763134": e_nom, "entry.2011749615": e_tel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_buscado = st.text_input("Documento del Paciente").strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            # TARJETA PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EDAD:</b> {p.get('EDAD')} años</p>
                <p><b>EPS:</b> {p.get('EPS')}</p>
                <p><b>⚠️ ALERTAS:</b> {p.get('CONDICIONES ESPECIALES (ALERGIAS, ENFERMEDADES DE BASE)')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)

            # HISTORIAL FILTRADO (Buscamos con las columnas normalizadas en mayúsculas)
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- GENERADOR DE PDF ---
            pdf = FPDF()
            pdf.add_page()
            try: pdf.image(LOGO_URL, 10, 8, 30)
            except: pass
            pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Tarjeta Vida QR", ln=True, align='C')
            pdf.set_font("Arial", 'I', 10); pdf.cell(0, 10, "Tu Informacion de Salud Siempre Contigo", ln=True, align='C')
            pdf.ln(15)
            
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "HISTORIA CLINICA", 1, 1, 'C')
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 7, f"Nombre: {p.get('NOMBRE')}", 0, 1)
            pdf.cell(0, 7, f"Documento: {p.get('DOCUMENTO')} | EPS: {p.get('EPS')}", 0, 1)
            pdf.ln(5)

            if not h_p.empty:
                for _, f in h_p.iterrows():
                    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 7, f"FECHA: {f.get('MARCA TEMPORAL')}", 0, 1)
                    pdf.set_font("Arial", '', 9)
                    pdf.multi_cell(0, 5, f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}")
                    pdf.multi_cell(0, 5, f"VALORACION: {f.get('2. VALORACIÓN')}")
                    pdf.cell(0, 5, f"SIGNOS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}", 0, 1)
                    pdf.multi_cell(0, 5, f"TRATAMIENTO: {f.get('8. MEDICAMENTOS')}")
                    pdf.multi_cell(0, 5, f"NOTAS: {f.get('9. EPICRISIS O NOTAS ADICIONALES')}")
                    pdf.ln(2); pdf.cell(0, 0, "", 'T', 1); pdf.ln(2)

            st.download_button("📥 Descargar Reporte PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # --- HISTORIAL EN PANTALLA ---
            st.subheader("📋 Evoluciones Recientes")
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                        <p style='margin:5px 0;'><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p style='margin:5px 0;'><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 Tensión:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style='margin:5px 0;'><b>💊 TRATAMIENTO:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p style='margin:5px 0; font-size:0.85em; color:#555;'><b>NOTAS:</b> {f.get('9. EPICRISIS O NOTAS ADICIONALES')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No se encontraron registros de evolución.")
        else:
            st.warning("Paciente no encontrado.")
