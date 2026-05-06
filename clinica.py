import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica QR", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS BLINDADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    
    /* Forzamos que los textos generales no bloqueen a los específicos */
    label, h1, h2, h3, span { color: #000000 !important; }
    
    /* Contenedores de tarjetas */
    .medical-card {
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #b2f5ea !important; 
        border-left: 15px solid #4fd1c5 !important; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); 
        margin-bottom: 20px;
    }
    
    .condition-box {
        background-color: #fff9db !important; 
        padding: 12px; 
        border-radius: 10px; 
        border: 1px solid #fab005 !important; 
        margin: 10px 0;
    }

    .emergency-box { 
        background-color: #fff5f5 !important; 
        padding: 12px; 
        border-radius: 10px; 
        border: 2px dashed #f56565 !important; 
        margin-top: 10px; 
    }

    /* Sidebar y Botones */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; }
    div.stButton > button:first-child {
        background-color: #4fd1c5 !important; 
        color: #000000 !important; 
        border-radius: 12px; 
        font-weight: 900 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URLs Y RECURSOS ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"
URL_FORM_PACIENTES = "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse"
URL_FORM_HISTORIAL = "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse"

# --- 4. CARGA DE DATOS ---
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

def obtener_valor(df_row, keywords):
    for col in df_row.index:
        if all(word in col for word in keywords):
            return df_row[col]
    return "No registrado"

df_p, df_h = cargar_datos()

# --- 5. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"

# --- 6. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Registro de Paciente</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Número de Documento")
        condiciones = st.text_area("Condiciones Especiales (Alergias, etc.)")
        # ... (otros campos abreviados por espacio, mantén los tuyos)
        if st.form_submit_button("GUARDAR PACIENTE"):
            if nombre and cedula:
                payload = {
                    "entry.346175428": nombre, 
                    "entry.1302424820": cedula.strip(),
                    "entry.NUEVO_ID": condiciones # Reemplaza con tu ID real
                }
                requests.post(URL_FORM_PACIENTES, data=payload)
                st.success("✅ Registrado")
                st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            cond_val = obtener_valor(p, ["CONDICIONES", "ESPECIALES"]) or "Ninguna registrada"
            emer_nom = obtener_valor(p, ["NOMBRE", "EMERGENCIA"])
            emer_tel = obtener_valor(p, ["TEL", "EMERGENCIA"])

            # AQUÍ ESTÁ LA CORRECCIÓN CRÍTICA DE COLOR
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: #000000 !important; margin: 0;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p style="color: #4a5568 !important; margin: 0;"><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                
                <div class="condition-box">
                    <p style="color: #856404 !important; margin: 0; font-size: 0.9em; font-weight: 900 !important;">
                        ⚠️ CONDICIONES Y ALERGIAS:
                    </p>
                    <p style="color: #000000 !important; margin: 0; font-weight: 600 !important;">
                        {cond_val}
                    </p>
                </div>

                <p style="margin: 5px 0; color: #000000 !important;">
                    <b>EPS:</b> {p.get('EPS', 'N/A')} | <b>CEL:</b> {p.get('CELULAR', 'N/A')}
                </p>
                
                <div class="emergency-box">
                    <p style="color: #c53030 !important; margin: 0; font-weight: 900 !important;">
                        🚨 CONTACTO DE EMERGENCIA:
                    </p>
                    <p style="margin: 0; color: #000000 !important;"><b>Nombre:</b> {emer_nom}</p>
                    <p style="margin: 0; color: #000000 !important;"><b>Tel:</b> {emer_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
