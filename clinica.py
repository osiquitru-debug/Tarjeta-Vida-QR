import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida", layout="centered", page_icon="🩺")

# --- 2. CSS + LÓGICA DE IMPRESIÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    .medical-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .alert-card { background-color: #fff5f5; padding: 20px; border-radius: 15px; border-left: 15px solid #f56565; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(245, 101, 101, 0); } 100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); } }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    
    /* Estilos específicos para cuando se imprime */
    @media print {
        .stSidebar, .stButton, .stTabs, div[data-testid="stForm"], header { display: none !important; }
        .stApp { background-color: white !important; }
        .medical-card, .alert-card { border: 2px solid #ccc !important; box-shadow: none !important; animation: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        if 'DOCUMENTO' in p.columns: p['DOCUMENTO'] = p['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        if 'DOCUMENTO' in h.columns: h['DOCUMENTO'] = h['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. MENÚ ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.title("🏥 Menú")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. LÓGICA DE SECCIONES ---

if st.session_state.menu == "Registrar":
    st.subheader("📝 Registro de Paciente")
    with st.form("f_reg", clear_on_submit=True):
        n = st.text_input("Nombre Completo")
        d = st.text_input("Documento")
        e = st.text_input("EPS")
        r = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c = st.text_input("Celular")
        al = st.text_area("Alertas Médicas / Alergias")
        en = st.text_input("Nombre Contacto Emergencia")
        et = st.text_input("Teléfono Contacto Emergencia")
        if st.form_submit_button("GUARDAR DATOS"):
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", 
                          data={"entry.346175428": n, "entry.1302424820": d, "entry.1172011247": e, "entry.162368130": r, "entry.1043165037": c, "entry.346363": al, "entry.1892763134": en, "entry.2011749615": et})
            st.success("✅ Paciente Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.subheader("🔍 Consulta de Historial")
    bus = st.text_input("Ingrese Documento del Paciente").strip()
    
    if bus and df_p is not None:
        pac = df_p[df_p["DOCUMENTO"] == bus]
        if not pac.empty:
            p = pac.iloc[0]
            
            # Extracción segura de columnas
            def get_col(keywords):
                for col in p.index:
                    if any(k in col for k in keywords): return str(p[col])
                return "N/A"

            nombre = get_col(["NOMBRE"])
            rh = get_col(["RH"])
            eps = get_col(["EPS"])
            cel = get_col(["CELULAR", "TEL"])
            alertas = get_col(["CONDICIONES", "ALERTA", "ESPECIALES"])
            e_nom = get_col(["NOMBRE DEL CONTACTO", "EMERGENCIA"])
            e_tel = get_col(["TELÉFONO CONTACTO", "TEL_EMERGENCIA"])

            tiene_alerta = alertas.lower() not in ['nan', '', 'ninguna', 'no', 'n/a']
            clase = "alert-card" if tiene_alerta else "medical-card"

            # --- TARJETA MÉDICA ---
            st.markdown(f"""
            <div class="{clase}" id="tarjeta-imprimir">
                <h2 style="color: black !important; margin-bottom: 5px;">{'⚠️' if tiene_alerta else '👤'} {nombre}</h2>
                {f'<p style="color: #c53030; font-weight: bold; font-size: 1.2em;">ALERTA MÉDICA: {alertas}</p>' if tiene_alerta else ''}
                
                <p style="color: black !important; margin: 2px 0;"><b>ID:</b> {bus} | <b>RH:</b> {rh}</p>
                <p style="color: black !important; margin: 2px 0;"><b>EPS:</b> {eps} | <b>CEL:</b> {cel}</p>
                
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 EN CASO DE EMERGENCIA LLAMAR A:</b></p>
                    <p style="margin:0; color: black !important;"><b>Nombre:</b> {e_nom}</p>
                    <p style="margin:0; color: black !important;"><b>Tel:</b> {e_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- BOTÓN DE IMPRESIÓN PDF ---
            if st.button("🖨️ Generar PDF / Imprimir Tarjeta"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

            # Formulario de Evolución
            with st.form("f_evo", clear_on_submit=True):
                st.write("---")
                st.markdown("### ✍️ Registrar Evolución Médica")
                tr = st.text_input("Tratamiento / Diagnóstico")
                me = st.text_area("Medicamentos recetados")
                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                  data={"entry.2019369477": bus, "entry.611862537": tr, "entry.2016051626": me})
                    st.success("✅ Evolución guardada"); st.cache_data.clear(); st.rerun()

            # Mostrar Historial
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == bus]
                if not h_p.empty:
                    st.write("### 📔 Historial de Evoluciones")
                    for i, row in h_p.iterrows():
                        st.markdown(f"""<div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #63b3ed; margin-bottom: 5px;">
                            <b>{row.get('MARCA DE TIEMPO', '')}</b><br>
                            {row.get('TRATAMIENTO', 'N/A')}
                        </div>""", unsafe_allow_html=True)
        else: st.error("❌ Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.subheader("📊 Bases de Datos del Sistema")
    t1, t2 = st.tabs(["📋 Lista de Pacientes", "📔 Historial Completo"])
    if df_p is not None: t1.dataframe(df_p, use_container_width=True)
    if df_h is not None: t2.dataframe(df_h, use_container_width=True)
