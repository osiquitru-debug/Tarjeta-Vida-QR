import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

# --- 2. CSS AVANZADO (DISEÑO PASTEL + ALERTAS + IMPRESIÓN) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    
    /* Tarjeta Normal */
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; 
        border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    
    /* Tarjeta Alerta */
    .alert-card {
        background-color: #fff5f5; padding: 20px; border-radius: 15px; border: 2px solid #feb2b2; 
        border-left: 15px solid #f56565; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(245, 101, 101, 0); }
        100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); }
    }

    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }

    /* Estilo para Impresión */
    @media print {
        .stSidebar, .stButton, header, .stTabs, div[data-testid="stForm"] { display: none !important; }
        .stApp { background-color: white !important; }
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
        # Limpieza de Documento
        for df in [p, h]:
            if 'DOCUMENTO' in df.columns:
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.split('.').str[0].str.strip()
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# Función para buscar valores aunque el nombre de la columna varíe un poco
def buscar_columna(fila, palabras_clave):
    for col in fila.index:
        if any(p_clave in col for p_clave in palabras_clave):
            return str(fila[col])
    return "No registrado"

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Consulta"

with st.sidebar:
    st.title("🩺 Menú")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---
if st.session_state.menu == "Registrar":
    st.subheader("Registro de Paciente")
    # (Aquí iría tu formulario de registro estándar)
    st.info("Usa el formulario para enviar datos a Google Forms.")

elif st.session_state.menu == "Consulta":
    busqueda = st.text_input("Ingrese Documento del Paciente").strip()
    
    if busqueda and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == busqueda]
        
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Extraer datos con la nueva función flexible
            nombre = buscar_columna(p, ["NOMBRE"])
            rh = buscar_columna(p, ["RH"])
            eps = buscar_columna(p, ["EPS"])
            cel = buscar_columna(p, ["CELULAR", "TEL"])
            alertas = buscar_columna(p, ["CONDICIONES", "ALERTA", "ESPECIALES"])
            e_nom = buscar_columna(p, ["NOMBRE DEL CONTACTO", "EMERGENCIA"])
            e_tel = buscar_columna(p, ["TELÉFONO CONTACTO", "TEL_EMERGENCIA"])

            # Determinar si es alerta
            es_alerta = alertas.lower() not in ['nan', '', 'ninguna', 'no', 'n/a']
            clase = "alert-card" if es_alerta else "medical-card"

            # RENDERIZADO DE TARJETA
            st.markdown(f"""
                <div class="{clase}">
                    <h2 style="color: black !important;">{'⚠️' if es_alerta else '👤'} {nombre}</h2>
                    {f'<p style="color: #c53030; font-weight: bold;">ALERTA MÉDICA: {alertas}</p>' if es_alerta else ''}
                    <p><b>ID:</b> {busqueda} | <b>RH:</b> {rh}</p>
                    <p><b>EPS:</b> {eps} | <b>CEL:</b> {cel}</p>
                    <div class="emergency-box">
                        <p style="color: red !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                        <p style="margin:0; color: black !important;"><b>Nombre:</b> {e_nom}</p>
                        <p style="margin:0; color: black !important;"><b>Tel:</b> {e_tel}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Botón de Impresión
            if st.button("🖨️ Imprimir Tarjeta / Guardar PDF"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

        else: st.error("Paciente no encontrado.")

elif st.session_state.menu == "Base":
    st.subheader("Bases de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_p is not None: t1.dataframe(df_p)
    if df_h is not None: t2.dataframe(df_h)
