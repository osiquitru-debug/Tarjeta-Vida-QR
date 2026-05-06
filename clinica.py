import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. CSS DE ALTA PRECISIÓN ---
st.markdown("""
    <style>
    /* Fondo y reseteo de márgenes */
    .stApp { background-color: #f0fff4 !important; }
    
    /* Centrado absoluto del logo */
    .logo-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        padding: 10px 0 30px 0;
    }
    .logo-box img { width: 220px; }

    /* Texto en negro puro y fuerte */
    h1, h2, h3, p, label, .stMarkdown, span { 
        color: #000000 !important; 
        font-weight: 700 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* Tarjeta Estándar */
    .card-normal {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #b2f5ea;
        border-left: 15px solid #4fd1c5;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }

    /* Tarjeta Alerta Roja */
    .card-alert {
        background: #fff5f5;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #feb2b2;
        border-left: 15px solid #f56565;
        margin-bottom: 25px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.5); }
        70% { box-shadow: 0 0 0 15px rgba(245, 101, 101, 0); }
        100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); }
    }

    /* Historial */
    .evo-card {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #63b3ed;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
        border-left: 8px solid #63b3ed;
    }

    /* Botones cuadrados y grandes */
    .stButton>button {
        background-color: #4fd1c5 !important;
        color: #000000 !important;
        border: 2px solid #2d3748 !important;
        border-radius: 10px !important;
        height: 50px;
        font-size: 18px !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar():
    url = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
    try:
        p = pd.read_csv(f"{url}&sheet=pacientes")
        h = pd.read_csv(f"{url}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        # Normalizar documentos
        for d in [p, h]:
            if 'DOCUMENTO' in d.columns:
                d['DOCUMENTO'] = d['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).strip()
        return p, h
    except: return None, None

def crear_pdf(nombre, id, rh, datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"HISTORIAL: {nombre}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"ID: {id} | RH: {rh}", ln=True, align='C')
    pdf.ln(10)
    for i, r in datos.iterrows():
        pdf.multi_cell(0, 10, f"FECHA: {r.get('MARCA DE TIEMPO')}\nTRATAMIENTO: {r.get('TRATAMIENTO')}\n---")
    return pdf.output(dest='S').encode('latin-1', 'ignore')

df_p, df_h = cargar()
LOGO = "https://lh3.googleusercontent.com/d/1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"

# Logo 100% centrado
st.markdown(f'<div class="logo-box"><img src="{LOGO}"></div>', unsafe_allow_html=True)

# --- 4. NAVEGACIÓN ---
menu = st.sidebar.radio("MENÚ", ["CONSULTA", "NUEVO REGISTRO"])

if menu == "NUEVO REGISTRO":
    st.markdown("<h2 style='text-align: center;'>REGISTRO DE PACIENTE</h2>", unsafe_allow_html=True)
    with st.form("f1"):
        nom = st.text_input("NOMBRE COMPLETO")
        doc = st.text_input("DOCUMENTO")
        rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alert = st.text_area("CONDICIONES ESPECIALES (ALERTA)")
        enom = st.text_input("CONTACTO EMERGENCIA")
        etel = st.text_input("TELÉFONO EMERGENCIA")
        if st.form_submit_button("GUARDAR"):
            pay = {"entry.346175428": nom, "entry.1302424820": doc, "entry.162368130": rh, "entry.346363": alert, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=pay)
            st.success("REGISTRADO")

else:
    bus = st.text_input("BUSCAR DOCUMENTO").strip()
    if bus and df_p is not None:
        p = df_p[df_p["DOCUMENTO"] == bus]
        if not p.empty:
            p = p.iloc[0]
            # Lógica de alerta
            txt_alerta = str(p.get('CONDICIONES ESPECIALES', '')).strip()
            es_critico = len(txt_alerta) > 2 and txt_alerta.lower() != 'nan'
            
            clase = "card-alert" if es_critico else "card-normal"
            icono = "⚠️" if es_critico else "👤"

            st.markdown(f"""
                <div class="{clase}">
                    <h2 style="margin:0;">{icono} {p.get('NOMBRE')}</h2>
                    {f'<p style="color:#e53e3e; font-size:1.2em;">ALERTA: {txt_alerta}</p>' if es_critico else ''}
                    <p>ID: {bus} | RH: {p.get('RH')}</p>
                    <div style="background:#fee2e2; padding:10px; border-radius:8px; border:1px solid #f87171;">
                        <p style="margin:0; color:#991b1b;">EMERGENCIA: {p.get('NOMBRE DEL CONTACTO DE EMERGENCIA')}</p>
                        <p style="margin:0;">TEL: {p.get('TELÉFONO CONTACTO DE EMERGENCIA')}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Evoluciones
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == bus]
                if not h_p.empty:
                    st.download_button("PDF HISTORIAL", crear_pdf(p.get('NOMBRE'), bus, p.get('RH'), h_p), f"{bus}.pdf")
                
                with st.form("f2"):
                    tr = st.text_input("TRATAMIENTO")
                    md = st.text_area("MEDICAMENTOS")
                    if st.form_submit_button("AÑADIR EVOLUCIÓN"):
                        pay_h = {"entry.2019369477": bus, "entry.611862537": tr, "entry.2016051626": md}
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=pay_h)
                        st.rerun()

                for _, r in h_p.iloc[::-1].iterrows():
                    st.markdown(f"""
                        <div class="evo-card">
                            <p style="color:#2b6cb0;">FECHA: {r.get('MARCA DE TIEMPO')}</p>
                            <p>TRATAMIENTO: {r.get('TRATAMIENTO')}</p>
                            <p>MEDS: {r.get('MEDICAMENTOS')}</p>
                        </div>
                    """, unsafe_allow_html=True)
