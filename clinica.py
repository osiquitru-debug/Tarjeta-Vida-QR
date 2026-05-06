import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica QR", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS PASTEL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }

    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; }

    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }

    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 15px; }
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS Y RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

@st.cache_data(ttl=1)
def cargar_datos():
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

# Función de búsqueda flexible para columnas
def buscar_dato(fila, palabras_clave):
    for col in fila.index:
        if all(palabra.upper() in col.upper() for palabra in palabras_clave):
            return fila[col]
    return "No registrado"

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Paciente</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        cedula = c1.text_input("Número de Documento")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c3, c4 = st.columns(2)
        eps = c3.text_input("EPS")
        alergias = st.text_input("Alergias / Contraindicaciones")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto")
        e_tel = st.text_input("Teléfono contacto")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, "entry.1302424820": cedula.strip(),
                    "entry.1172011247": eps, "entry.162368130": rh, 
                    "entry.346363": alergias, 
                    "entry.1892763134": e_nom, "entry.2011749615": e_tel
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Guardado correctamente.")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.markdown("<h1 style='text-align: center;'>Consulta Médica</h1>", unsafe_allow_html=True)
    id_bus = st.text_input("Ingrese Documento").strip()
    
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Recuperar datos con búsqueda flexible
            alergias_val = buscar_dato(p, ["ALERGIA"])
            emer_nom = buscar_dato(p, ["NOMBRE", "EMERGENCIA"])
            emer_tel = buscar_dato(p, ["TEL", "EMERGENCIA"])

            # TARJETA DEL PACIENTE
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="margin-bottom:10px;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>DOCUMENTO:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')}</p>
                <p><b>⚠️ ALERGIAS:</b> {alergias_val}</p>
                
                <div class="emergency-box">
                    <p style="color: #c53030; margin:0; font-size: 1.1em;"><b>🚨 CONTACTO DE EMERGENCIA</b></p>
                    <p style="margin:5px 0 0 0; color: black;"><b>Nombre:</b> {emer_nom}</p>
                    <p style="margin:2px 0 0 0; color: black;"><b>Teléfono:</b> {emer_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de impresión
            if st.button("🖨️ Imprimir Tarjeta"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

            # Historial
            st.markdown("---")
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus]
                if not h_p.empty:
                    st.write("### 📜 Historial de Evoluciones")
                    for _, fila in h_p.iloc[::-1].iterrows():
                        st.markdown(f"""
                        <div class="evolution-card">
                            <small>{fila.get('MARCA DE TIEMPO', '')}</small><br>
                            <b>Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/A')}<br>
                            <b>Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)

            with st.form("evo_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución")
                t = st.text_input("Tratamiento / Diagnóstico")
                m = st.text_area("Medicamentos / Observaciones")
                if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                    requests.post(URL_FORM_HISTORIAL, data={"entry.2019369477": id_bus, "entry.611862537": t, "entry.2016051626": m})
                    st.success("✅ Evolución guardada.")
                    st.cache_data.clear(); st.rerun()
        else: st.error("❌ Paciente no encontrado.")

else:
    st.subheader("📊 Base de Datos")
    if df_p is not None: st.dataframe(df_p, use_container_width=True)
