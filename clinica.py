import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- 2. DISEÑO CSS (ESTÉTICO Y FUNCIONAL) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzar color negro en textos para máxima claridad */
    label, p, h1, h2, h3, span, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 600 !important; 
    }
    
    /* Centrado del logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
    }
    
    /* Tarjeta de Paciente NORMAL (Turquesa) */
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px; 
        border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 25px;
    }
    
    /* Tarjeta de Paciente CRÍTICA (Roja Pulsante) */
    .alert-card {
        background-color: #fff5f5; padding: 25px; border-radius: 15px; 
        border: 2px solid #feb2b2; border-left: 15px solid #f56565; 
        margin-bottom: 25px;
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(245, 101, 101, 0); }
        100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); }
    }

    /* Tarjetas de Historial (Azul) */
    .evolution-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 1px solid #e2e8f0; border-left: 10px solid #63b3ed; 
        margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
    }
    
    /* Caja de Emergencia */
    .emergency-box { 
        background-color: #fff5f5; padding: 15px; border-radius: 10px; 
        border: 2px dashed #f56565; margin-top: 15px; 
    }
    
    /* Botones Estilo Turquesa */
    div.stButton > button {
        background-color: #4fd1c5 !important; color: #000000 !important; 
        border-radius: 12px; font-weight: 900 !important; 
        border: 2px solid #285e61; width: 100%; transition: 0.3s;
        height: 3.5em;
    }
    div.stButton > button:hover { background-color: #38b2ac !important; transform: scale(1.01); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES TÉCNICAS ---
def crear_pdf(nombre, documento, rh, df_historial):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "HISTORIAL MEDICO - TARJETA VIDA", ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f" PACIENTE: {nombre}", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" DOCUMENTO: {documento}    |    RH: {rh}", ln=True)
    pdf.ln(10)
    
    for i, fila in df_historial.iterrows():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"FECHA: {fila.get('MARCA DE TIEMPO', 'N/A')}", ln=True)
        pdf.set_font("Arial", "", 10)
        contenido = f"TRATAMIENTO: {fila.get('TRATAMIENTO', 'N/A')}\nMEDICAMENTOS: {fila.get('MEDICAMENTOS', 'N/A')}\nPROCEDIMIENTOS: {fila.get('PROCEDIMIENTOS', 'N/A')}"
        pdf.multi_cell(0, 6, contenido)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

@st.cache_data(ttl=1)
def cargar_datos():
    URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

# --- 4. INTERFAZ ---
df_p, df_h = cargar_datos()
URL_LOGO = "https://lh3.googleusercontent.com/d/1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"

# Logo Centrado
st.markdown(f'<div class="logo-container"><img src="{URL_LOGO}" width="200"></div>', unsafe_allow_html=True)

if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.markdown("### Navegación")
    if st.button("🔍 Consulta de Pacientes"): st.session_state.menu = "Consulta"
    if st.button("📝 Registro Nuevo"): st.session_state.menu = "Registrar"

# SECCIÓN REGISTRO
if st.session_state.menu == "Registrar":
    st.markdown("<h2 style='text-align: center;'>Nuevo Registro</h2>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        doc = c1.text_input("Número de Documento")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alertas = st.text_area("⚠️ Alertas Médicas / Condiciones Especiales")
        st.markdown("### 🚨 Emergencia")
        enom = st.text_input("Contacto Emergencia")
        etel = st.text_input("Teléfono Emergencia")
        if st.form_submit_button("GUARDAR PACIENTE"):
            pay = {"entry.346175428": nombre, "entry.1302424820": doc.strip(), "entry.162368130": rh, "entry.346363": alertas, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=pay)
            st.success("✅ Registrado con éxito.")
            st.cache_data.clear()

# SECCIÓN CONSULTA
elif st.session_state.menu == "Consulta":
    bus = st.text_input("🔍 Buscar Documento...").strip()
    if bus and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == bus]
        if not pac.empty:
            p = pac.iloc[0]
            
            # Verificar si existe alerta
            alerta_info = str(p.get('CONDICIONES ESPECIALES', '')).strip()
            es_critico = alerta_info.lower() not in ['nan', '', 'ninguna', 'no']
            estilo = "alert-card" if es_critico else "medical-card"
            
            st.markdown(f"""
            <div class="{estilo}">
                <h2 style="margin:0;">{'⚠️' if es_critico else '👤'} {p.get('NOMBRE', 'N/A')}</h2>
                {f'<p style="color:#c53030; font-size:1.3em; margin-top:10px;"><b>ALERTA: {alerta_info}</b></p>' if es_critico else ''}
                <hr>
                <p><b>DOCUMENTO:</b> {bus}  |  <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0; font-size:1.1em;">{p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'N/A')} - {p.get('TELÉFONO CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == bus]
                if not h_p.empty:
                    pdf_b = crear_pdf(p.get('NOMBRE'), bus, p.get('RH'), h_p)
                    st.download_button("📥 DESCARGAR HISTORIAL PDF", data=pdf_b, file_name=f"Historial_{bus}.pdf", mime="application/pdf")
                
                with st.form("evo"):
                    st.markdown("### ✍️ Registrar Evolución")
                    tr = st.text_input("Tratamiento")
                    me = st.text_area("Medicamentos")
                    pr = st.text_area("Procedimientos")
                    if st.form_submit_button("GUARDAR"):
                        pay_h = {"entry.2019369477": bus, "entry.611862537": tr, "entry.2016051626": me, "entry.1088523869": pr}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay_h)
                        st.cache_data.clear()
                        st.rerun()

                st.markdown("### 📅 Evoluciones")
                for i in range(len(h_p)-1, -1, -1):
                    f = h_p.iloc[i]
                    st.markdown(f"""
                    <div class="evolution-card">
                        <p style="color: #2b6cb0;"><b>REGISTRO - {f.get('MARCA DE TIEMPO', 'N/A')}</b></p>
                        <p><b>🩺 TRATA:</b> {f.get('TRATAMIENTO', 'N/A')}</p>
                        <p><b>💊 MEDS:</b> {f.get('MEDICAMENTOS', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.error("❌ No encontrado.")
