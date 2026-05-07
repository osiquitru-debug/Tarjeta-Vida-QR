import streamlit as st
import pd as pd
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN Y ESTÉTICA (CENTRADOS + CASILLAS BLANCAS) ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    
    /* Casillas blancas con letras negras */
    div[data-baseweb="input"], div[data-baseweb="textarea"], select, input, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Títulos y textos centrados */
    h1, h2, h3, p, label { color: #1a202c !important; text-align: center; }
    
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; text-align: left;
    }
    
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 8px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold; text-align: center;
    }

    .evo-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; border-left: 5px solid #63b3ed;
        margin-bottom: 10px; color: #2d3748; text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

# URLs de los formularios
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
# Nueva URL de historial basada en el enlace proporcionado
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        p.columns = [c.strip().upper() for c in p.columns]
        h.columns = [c.strip().upper() for c in h.columns]
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN Y LOGO SUPERIOR ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.markdown("<h3 style='text-align: center;'>MENÚ</h3>", unsafe_allow_html=True)
    if st.button("🏠 Inicio"): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución"): st.session_state.menu = "Consulta"

# Logo centrado arriba del título principal
c_l1, c_l2, c_l3 = st.columns([1,1,1])
with c_l2: st.image(URL_LOGO, width=120)

# --- 5. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 TARJETA VIDA")
    st.subheader("Gestión de Historiales Médicos")

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("form_reg", clear_on_submit=True):
        st.markdown("### Datos Personales")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de Documento", ["CC", "TI", "CE", "RC"])
            doc = st.text_input("Número de Documento")
        with c2:
            edad = st.text_input("Edad")
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        cel = st.text_input("Celular")
        condiciones = st.text_area("Condiciones especiales / Alergias")
        
        st.markdown("### Contacto de Emergencia")
        ec1, ec2 = st.columns(2)
        with ec1: e_nom = st.text_input("Nombre contacto emergencia")
        with ec2: e_tel = st.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            # Parámetros originales de registro
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": doc,
                "entry.1801154005": edad, "entry.1043165037": cel, "entry.1172011247": eps,
                "entry.162368130": rh, "entry.346363": condiciones, "entry.1892763134": e_nom, "entry.2011749615": e_tel
            }
            requests.post(URL_FORM_PACIENTES, data=payload)
            st.success("Paciente registrado correctamente.")
            st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA Y EVOLUCIÓN")
    id_bus = st.text_input("Ingrese Documento del Paciente").strip()
    
    if id_bus and df_p is not None:
        p_row = df_p[df_p["DOCUMENTO"] == id_bus]
        if not p_row.empty:
            p = p_row.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2>👤 {p.get('NOMBRE')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {p.get('NOMBRE CONTACTO EMERGENCIA')} - {p.get('TELEFONO CONTACTO EMERGENCIA')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("✍️ REGISTRAR EVOLUCIÓN (NUEVOS PARÁMETROS)"):
                with st.form("evo_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        v1 = st.text_area("1. Valoración")
                        v2 = st.text_area("2. Motivo de la Consulta")
                        v3 = st.text_input("3. Talla")
                        v4 = st.text_input("4. Peso")
                        v5 = st.text_input("5. Presión Arterial")
                    with col2:
                        v6 = st.text_area("6. Antecedentes Medicos")
                        v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios - Procedimientos")
                        v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("GUARDAR EN HISTORIAL"):
                        # Mapeo exacto según tu nuevo enlace proporcionado
                        data_h = {
                            "entry.2019369477": id_bus,    # Documento
                            "entry.1088523869": v1,        # Valoración
                            "entry.611862537": v2,         # Motivo
                            "entry.1275746503": v3,        # Talla
                            "entry.949747647": v4,         # Peso
                            "entry.2091389798": v5,        # Presión
                            "entry.889985940": v6,         # Antecedentes
                            "entry.2016051626": v7,        # Medicamentos
                            "entry.882053172": v8,         # Laboratorios
                            "entry.616774918": v9          # Epicrisis
                        }
                        requests.post(URL_FORM_HISTORIAL, data=data_h)
                        st.success("Evolución guardada correctamente.")
                        st.cache_data.clear()
                        st.rerun()

            st.subheader("📋 HISTORIAL CLÍNICO")
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus]
                if not h_p.empty:
                    for _, f in h_p.sort_index(ascending=False).iterrows():
                        st.markdown(f"""
                        <div class="evo-card">
                            <small>📅 {f.get('MARCA TEMPORAL', 'S/F')}</small><br>
                            <b>1. Valoración:</b> {f.get('VALORACION', 'N/R')}<br>
                            <b>2. Motivo:</b> {f.get('MOTIVO DE LA CONSULTA', 'N/R')}<br>
                            <b>3. Talla:</b> {f.get('TALLA')} | <b>4. Peso:</b> {f.get('PESO')} | <b>5. PA:</b> {f.get('PRESION ARTERIAL')}<br>
                            <b>6. Antecedentes:</b> {f.get('ANTECEDENTES MEDICOS', 'N/R')}<br>
                            <b>7. Medicamentos:</b> {f.get('MEDICAMENTOS', 'N/R')}<br>
                            <b>9. Epicrisis:</b> {f.get('EPICRISIS', 'N/R')}
                        </div>
                        """, unsafe_allow_html=True)
                else: st.info("No hay registros previos.")
