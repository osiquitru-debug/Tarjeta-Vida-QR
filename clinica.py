import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN VISUAL DINÁMICA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

# Definición de colores según la sección activa
if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

# Fondo Menta para Registro y Consulta, Crema para el resto
if st.session_state.menu in ["Registrar", "Consulta"]:
    bg_color = "#D8F3DC"  # Verde menta pastel
else:
    bg_color = "#f0f7f4"  # Crema/Menta muy claro

st.markdown(f"""
    <style>
    /* Fondo dinámico de la aplicación */
    .stApp {{ 
        background-color: {bg_color} !important; 
        color: #000000 !important;
    }}
    
    /* MENÚ LATERAL - Palo de Rosa */
    [data-testid="stSidebar"] {{
        background-color: #E5B1B1 !important;
        border-right: 2px solid #d4a5a5;
    }}
    
    /* TEXTOS EN NEGRO ABSOLUTO */
    h1, h2, h3, p, span, label, li, .stMarkdown, [data-testid="stSidebar"] .stMarkdown {{
        color: #000000 !important;
        font-weight: 500;
    }}

    /* CAJAS DE ENTRADA BLANCAS */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stTextArea>div>div>textarea {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #94a3b8 !important;
    }}

    /* TARJETAS DE PACIENTE Y EVOLUCIÓN (Blancas) */
    .medical-card, .evo-card {{
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }}
    
    .medical-card {{ border-left: 12px solid #a2d2ff; }}
    .evo-card {{ border-left: 8px solid #b7e4c7; }}

    .emergency-box {{
        background-color: #ffe5d9; 
        padding: 15px; 
        border-radius: 12px;
        border: 2px dashed #f87171; 
        color: #b91c1c !important; 
        font-weight: bold; 
    }}

    /* BOTONES */
    div.stButton > button {{
        background-color: #84dcc6 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3em !important;
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
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>MENÚ</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): 
        st.session_state.menu = "Inicio"
        st.rerun()
    if st.button("📝 Registrar Paciente", use_container_width=True): 
        st.session_state.menu = "Registrar"
        st.rerun()
    if st.button("🔍 Consulta / Evolución", use_container_width=True): 
        st.session_state.menu = "Consulta"
        st.rerun()

# --- 4. VISTAS ---

if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 TARJETA VIDA")
    st.write("Gestión Clínica - Guadalupe, Huila.")

elif st.session_state.menu == "Registrar":
    st.image(LOGO_URL, width=120)
    st.title("📝 NUEVO REGISTRO")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            ndoc = st.text_input("Número")
        with c2:
            eda = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        esp = st.text_area("Condiciones Especiales")
        st.subheader("🚨 Contacto de Emergencia")
        cnom = st.text_input("Nombre Referencia")
        ctel = st.text_input("Teléfono Referencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc,
                "entry.1801154005": eda, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": cnom, "entry.2011749615": ctel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.image(LOGO_URL, width=120)
    st.title("🔍 HISTORIAL CLÍNICO")
    busqueda = st.text_input("Documento del Paciente").strip().split('.')[0].replace(" ", "")

    if busqueda and df_p is not None:
        pac = df_p[df_p['ID_KEY'] == busqueda]
        if not pac.empty:
            p = pac.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                <p><b>CC:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} ({p.get('TELEFONO CONTACTO EMERGENCIA')})</div>
            </div>""", unsafe_allow_html=True)
            
            # Exportar PDF
            pdf = FPDF()
            pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, f"HC: {p.get('NOMBRE')}", ln=True, align='C')
            st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{busqueda}.pdf")

            # Nueva Evolución
            with st.expander("➕ REGISTRAR EVOLUCIÓN"):
                with st.form("f_evo", clear_on_submit=True):
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        val = st.text_area("Valoración"); mot = st.text_area("Motivo")
                    with ce2:
                        tal = st.text_input("Talla"); pes = st.text_input("Peso"); pre = st.text_input("Presión")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        data = {"entry.2019369477": busqueda, "entry.1088523869": val, "entry.611862537": mot, "entry.1275746503": tal, "entry.949747647": pes, "entry.2091389798": pre}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            # Listado de evoluciones
            h_p = df_h[df_h['ID_KEY'] == busqueda].sort_index(ascending=False)
            for _, f in h_p.iterrows():
                st.markdown(f"""
                <div class="evo-card">
                    <small>📅 {f.get('MARCA TEMPORAL')}</small><br>
                    <b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}<br>
                    <b>PLAN:</b> {f.get('8. MEDICAMENTOS')}
                </div>""", unsafe_allow_html=True)
        else:
            st.error("Paciente no encontrado.")
