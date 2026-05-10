import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64

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
    
    /* FLECHAS BLANCAS */
    [data-testid="stSidebarCollapseIcon"] svg, [data-testid="collapsedControl"] svg {{
        fill: #ffffff !important; color: #ffffff !important;
    }}

    /* DISEÑO CARNET DIGITAL (BASADO EN TU IMAGEN) */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 20px;
        padding: 25px;
        width: 100%;
        max-width: 450px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        font-family: 'Arial', sans-serif;
        color: #000000 !important;
    }}
    .carnet-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }}
    .carnet-body {{
        display: flex;
        gap: 20px;
    }}
    .carnet-info {{ flex: 2; }}
    .carnet-qr {{ flex: 1; text-align: center; }}
    .carnet-info p {{ margin: 3px 0; font-size: 14px; }}
    .carnet-info b {{ color: #000000; }}
    .label-emergencia {{
        background-color: #f43f5e;
        color: white !important;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        display: inline-block;
        margin-top: 10px;
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

# --- FUNCIONES AUXILIARES ---
def get_qr_base64(url):
    qr = segno.make(url)
    buff = io.BytesIO()
    qr.save(buff, kind='png', scale=5)
    return base64.b64encode(buff.getvalue()).decode()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA Y CARNET")
    params = st.query_params
    id_buscado = st.text_input("Ingrese Documento", value=params.get("id", "")).strip().replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Obtención de datos con lógica flexible
            def obtener_dato(df_row, claves):
                for col in df_row.index:
                    if all(c in col for c in claves): return df_row[col]
                return "No registra"

            nom_e = obtener_dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_e = obtener_dato(p, ["TEL", "CONTACTO", "EMERGENCIA"])
            alert = obtener_dato(p, ["CONDICIONES", "ESPECIALES"])
            
            # --- GENERACIÓN DEL CARNET VISUAL (ESTILO IMAGEN SUBIDA) ---
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_b64 = get_qr_base64(url_p)

            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header">
                    <img src="{LOGO_URL}" width="100">
                    <b style="font-size: 18px;">CARNET VIDA QR</b>
                </div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>PACIENTE:</b><br>{p.get('NOMBRE')}</p>
                        <p><b>ID:</b> {p.get('DOCUMENTO')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <p><b>ALERGIAS:</b> {alert[:50]}...</p>
                        <div class="label-emergencia">
                            📞 SOS: {nom_e}<br>{tel_e}
                        </div>
                    </div>
                    <div class="carnet-qr">
                        <img src="data:image/png;base64,{qr_b64}" width="110">
                        <p style="font-size: 10px; margin-top: 5px;">ESCANÉAME</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()

            # Botón de Descarga del Carnet como PDF
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55)) # Tamaño tarjeta de crédito
            pdf_c.add_page()
            pdf_c.set_fill_color(162, 210, 255) # Azul claro de la imagen
            pdf_c.rect(0, 0, 85, 55, 'F')
            pdf_c.set_font("Arial", 'B', 8)
            pdf_c.text(5, 10, "CARNET VIDA QR")
            pdf_c.set_font("Arial", '', 7)
            pdf_c.text(5, 20, f"PACIENTE: {p.get('NOMBRE')}")
            pdf_c.text(5, 25, f"ID: {p.get('DOCUMENTO')}")
            pdf_c.text(5, 30, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            pdf_c.text(5, 35, f"SOS: {nom_e}")
            pdf_c.text(5, 40, f"TEL: {tel_e}")
            
            # Inserción de QR en el PDF
            qr_pdf = segno.make(url_p)
            qr_img_buff = io.BytesIO()
            qr_pdf.save(qr_img_buff, kind='png', border=0)
            pdf_c.image(qr_img_buff, 55, 10, 25, 25)

            st.download_button("📥 Descargar Carnet Digital (PDF)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")

            # --- SECCIÓN DE HISTORIAL ---
            st.subheader("📋 Evoluciones Médicas")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
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
                        <p><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)

# (Se mantienen las secciones de Inicio y Registrar del código anterior)
elif st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.image(LOGO_URL, width=300)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
            cel = st.text_input("Celular")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alert = st.text_area("Condiciones Especiales")
        st.subheader("🚨 Emergencia")
        enom = st.text_input("Nombre Contacto"); etel = st.text_input("Teléfono Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("Paciente registrado."); st.cache_data.clear()
