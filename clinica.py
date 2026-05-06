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
    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .evo-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #edf2f7; margin-bottom: 10px; padding-bottom: 5px; }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URL DEL LOGO ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"

# --- 4. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial")
        # Limpieza de nombres de columnas
        p.columns = p.columns.str.strip().str.upper()
        h.columns = h.columns.str.strip().str.upper()
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 5. FUNCIÓN PARA BUSCAR COLUMNAS DINÁMICAMENTE ---
def obtener_valor(df_row, keywords):
    """Busca en la fila una columna que contenga ciertas palabras clave"""
    for col in df_row.index:
        if all(word in col for word in keywords):
            return df_row[col]
    return "No registrado"

# --- 6. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 7. SECCIONES ---
if st.session_state.menu == "Registrar":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image(URL_LOGO, use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    # Formulario (omitiendo por brevedad, se mantiene igual que el anterior)
    # ... código de registro previo ...

elif st.session_state.menu == "Consulta":
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: st.image(URL_LOGO, width=150)
    st.markdown("<h1 style='text-align: center;'>Consulta e Historial</h1>", unsafe_allow_html=True)

    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # BUSQUEDA INTELIGENTE DE DATOS DE EMERGENCIA
            emer_nom = obtener_valor(p, ["NOMBRE", "EMERGENCIA"])
            emer_tel = obtener_valor(p, ["TELEFONO", "EMERGENCIA"]) or obtener_valor(p, ["TEL", "EMERGENCIA"])
            
            st.markdown(f"""
            <div class="medical-card">
                <h2 style="color: black !important;">👤 {p.get('NOMBRE', 'N/A')}</h2>
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0; color: black !important;"><b>Nombre:</b> {emer_nom}</p>
                    <p style="margin:0; color: black !important;"><b>Tel:</b> {emer_tel}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- HISTORIAL EN TARJETAS ---
            st.markdown("### 📅 Historial de Evoluciones")
            if df_h is not None:
                h_p = df_h[df_h["DOCUMENTO"] == id_bus].reset_index(drop=True)
                if h_p.empty: st.info("Sin registros.")
                else:
                    for i in range(len(h_p)-1, -1, -1):
                        fila = h_p.iloc[i]
                        st.markdown(f"""
                        <div class="evolution-card">
                            <div class="evo-header">
                                <span style="color: #2b6cb0; font-size: 1.1em;"><b>Evolución #{i+1}</b></span>
                                <span style="color: #718096; font-size: 0.85em;">🕒 {fila.get('MARCA DE TIEMPO', 'N/A')}</span>
                            </div>
                            <p style="margin: 5px 0;"><b>🩺 Tratamiento:</b> {fila.get('TRATAMIENTO', 'N/A')}</p>
                            <p style="margin: 5px 0;"><b>💊 Medicamentos:</b> {fila.get('MEDICAMENTOS', 'N/A')}</p>
                            <p style="margin: 5px 0;"><b>📋 Procedimientos:</b> {fila.get('PROCEDIMIENTOS', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            # ... formulario de nueva entrada ...
        else: st.error("❌ No encontrado.")
# ... sección Base de Datos ...
