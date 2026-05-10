import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os  # Necesario para manejar el archivo temporal

# --- 1. CONFIGURACIÓN VISUAL Y ESTILOS ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{ color: #000000 !important; }}

    /* FLECHAS BLANCAS */
    [data-testid="stSidebarCollapseIcon"] svg, [data-testid="collapsedControl"] svg {{
        fill: #ffffff !important; color: #ffffff !important;
    }}

    /* DISEÑO CARNET DIGITAL (ESTILO IMAGEN "TARJETA QR") */
    .carnet-container {{
        background-color: #a2d2ff;
        border-radius: 20px;
        padding: 25px;
        width: 100%;
        max-width: 480px;
        margin: auto;
        border: 2px solid #ffffff;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        font-family: 'Arial', sans-serif;
    }}
    .carnet-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
    .carnet-body {{ display: flex; gap: 20px; }}
    .carnet-info {{ flex: 2; }}
    .carnet-qr {{ flex: 1; text-align: center; align-self: center; }}
    .carnet-info p {{ margin: 4px 0; font-size: 14px; line-height: 1.2; color: #000000 !important; }}
    .label-emergencia {{
        background-color: #f43f5e; color: white !important; padding: 6px 12px;
        border-radius: 8px; font-size: 13px; display: inline-block; margin-top: 10px;
        font-weight: bold; border: 1px solid #ffffff;
    }}

    /* ESTILOS EVOLUCIONES */
    .evo-card {{
        background-color: #ffffff; padding: 18px; border-radius: 12px;
        border-left: 8px solid #b7e4c7; margin-bottom: 15px; border-top: 1px solid #eee;
    }}
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; 
        margin: 10px 0; padding: 8px 0; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
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
if st.session_state.menu == "Inicio":
    st.image(LOGO_URL, width=280)
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")

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
        enom = st.text_input("Nombre Contacto Emergencia"); etel = st.text_input("Teléfono Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA")
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip().replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            nom_e = "No registra"; tel_e = "No registra"
            # Lógica para extraer datos de emergencia
            for col in p.index:
                if "NOMBRE" in col and "EMERGENCIA" in col: nom_e = p[col]
                if "TEL" in col and "EMERGENCIA" in col: tel_e = p[col]

            # Visualización Carnet
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_b64 = get_qr_base64(url_p)

            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header">
                    <img src="{LOGO_URL}" width="90">
                    <b style="font-size: 18px; color: #000;">TARJETA VIDA QR</b>
                </div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p><b>PACIENTE:</b><br>{p.get('NOMBRE')}</p>
                        <p><b>DOCUMENTO:</b> {p.get('DOCUMENTO')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <div class="label-emergencia">🚨 SOS: {nom_e}<br>TEL: {tel_e}</div>
                    </div>
                    <div class="carnet-qr">
                        <img src="data:image/png;base64,{qr_b64}" width="115">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            
            # --- SOLUCIÓN DEFINITIVA PARA EL PDF ---
            pdf_c = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf_c.add_page()
            pdf_c.set_fill_color(162, 210, 255)
            pdf_c.rect(0, 0, 85, 55, 'F')
            pdf_c.set_font("Arial", 'B', 10)
            pdf_c.text(5, 10, "TARJETA VIDA QR")
            pdf_c.set_font("Arial", '', 8)
            pdf_c.text(5, 20, f"PACIENTE: {p.get('NOMBRE')[:25]}")
            pdf_c.text(5, 25, f"ID: {p.get('DOCUMENTO')}")
            pdf_c.text(5, 30, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            pdf_c.set_text_color(200, 0, 0)
            pdf_c.text(5, 42, f"SOS: {nom_e[:20]}")
            pdf_c.text(5, 47, f"TEL: {tel_e}")
            
            # Guardar QR temporalmente como archivo físico para evitar el error .rfind
            temp_qr_path = f"temp_qr_{id_buscado}.png"
            qr_temp = segno.make(url_p)
            qr_temp.save(temp_qr_path, border=0)
            
            # Insertar imagen desde el archivo real
            pdf_c.image(temp_qr_path, x=55, y=12, w=25, h=25)
            
            # Mostrar botón de descarga
            st.download_button("📥 Descargar Tarjeta Digital", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            
            # Limpiar el archivo temporal
            if os.path.exists(temp_qr_path):
                os.remove(temp_qr_path)

            # --- SECCIÓN DE EVOLUCIONES (7 DE MAYO) ---
            st.divider()
            st.subheader("📋 HISTORIAL DETALLADO")
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1: v_mot = st.text_area("Motivo"); v_val = st.text_area("Valoración"); v_ant = st.text_area("Antecedentes"); v_tal = st.text_input("Talla")
                    with c2: v_pes = st.text_input("Peso"); v_pre = st.text_input("Presión Arterial"); v_med = st.text_area("Medicamentos"); v_lab = st.text_area("Laboratorios"); v_epi = st.text_area("Epicrisis")
                    if st.form_submit_button("GUARDAR"):
                        data_e = {"entry.2019369477": id_buscado, "entry.611862537": v_mot, "entry.1088523869": v_val, "entry.1275746503": v_tal, "entry.949747647": v_pes, "entry.2091389798": v_pre, "entry.2016051626": v_med, "entry.616774918": v_epi}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_e)
                        st.success("Guardado."); st.cache_data.clear(); st.rerun()

            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
