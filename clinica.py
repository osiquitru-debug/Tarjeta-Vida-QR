import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tarjeta Vida | Gestión Médica QR", 
    layout="centered", 
    page_icon="🩺"
)

# --- 2. DISEÑO CSS PASTEL (Mantenido y Reforzado) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fff4 !important; }
    label, p, h1, h2, h3, span { color: #000000 !important; font-weight: 600 !important; }
    
    /* Inputs y áreas de texto */
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }
    input, textarea { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #a2d2ff !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #f3e8ff !important; border-right: 2px solid #d8b4fe; }
    .stSidebar button { width: 100%; background-color: #ffffff !important; color: #000000 !important; border: 2px solid #d8b4fe !important; font-weight: bold !important; margin-bottom: 10px; }

    /* Botones de Guardar e Imprimir */
    div.stButton > button:first-child:not(.stSidebar button) {
        background-color: #4fd1c5 !important; color: #000000 !important; border-radius: 12px; font-weight: 900 !important; border: 2px solid #285e61; height: 3.5em; width: 100%;
    }

    /* Tarjetas de Paciente y Evolución */
    .medical-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #b2f5ea; border-left: 15px solid #4fd1c5; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    
    /* Nueva Tarjeta de ALERTA (Basada en tu diseño original) */
    .alert-card {
        background-color: #fff5f5; padding: 20px; border-radius: 15px; border: 2px solid #feb2b2; border-left: 15px solid #f56565; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(245, 101, 101, 0); }
        100% { box-shadow: 0 0 0 0px rgba(245, 101, 101, 0); }
    }

    .evolution-card {
        background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid #63b3ed; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .evo-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #edf2f7; margin-bottom: 10px; padding-bottom: 5px; }
    .emergency-box { background-color: #fff5f5; padding: 12px; border-radius: 10px; border: 2px dashed #f56565; margin-top: 10px; }

    /* Lógica de Impresión */
    @media print {
        .stSidebar, .stButton, .stTabs, div[data-testid="stForm"], header { display: none !important; }
        .stApp { background-color: white !important; }
        .medical-card, .alert-card { border: 2px solid #ccc !important; box-shadow: none !important; animation: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. URL Y CARGA (Mantenido) ---
ID_LOGO = "1k1ef0WvY-IXPJTajkPR6eukxj-qcraxH"
URL_LOGO = f"https://lh3.googleusercontent.com/d/{ID_LOGO}"
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

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

df_p, df_h = cargar_datos()

# --- 4. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Registrar"
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.markdown("---")
    if st.button("📝 Registrar Paciente"): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta e Historial"): st.session_state.menu = "Consulta"
    if st.button("📊 Base de Datos"): st.session_state.menu = "Base"

# --- 5. SECCIONES ---

if st.session_state.menu == "Registrar":
    st.markdown("<h1 style='text-align: center;'>Gestión Médica Tarjeta QR</h1>", unsafe_allow_html=True)
    with st.form("reg_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        c1, c2 = st.columns(2)
        cedula = c1.text_input("Número de Documento")
        rh = c2.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        c3, c4 = st.columns(2)
        eps = c3.text_input("EPS")
        cel = c4.text_input("Celular")
        alertas_input = st.text_area("⚠️ Alertas Médicas / Alergias")
        
        st.markdown("### 🚨 Contacto de Emergencia")
        e_nom = st.text_input("Nombre contacto emergencia")
        e_tel = st.text_input("Teléfono contacto emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE"):
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", 
                          data={"entry.346175428": nombre, "entry.1302424820": cedula, "entry.1172011247": eps, "entry.162368130": rh, "entry.1043165037": cel, "entry.346363": alertas_input, "entry.1892763134": e_nom, "entry.2011749615": e_tel})
            st.success("✅ Guardado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    id_bus = st.text_input("Ingrese Documento").strip()
    if id_bus and df_p is not None:
        paciente = df_p[df_p["DOCUMENTO"] == id_bus]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Lógica de Alertas (Busca en cualquier columna que diga ALERTA o CONDICION)
            condiciones = next((str(p[c]) for c in p.index if "ALERTA" in c or "CONDICION" in c or "ESPECIAL" in c), "")
            es_alerta = condiciones.lower() not in ['nan', '', 'ninguna', 'no', 'n/a']
            
            clase_estilo = "alert-card" if es_alerta else "medical-card"

            st.markdown(f"""
            <div class="{clase_estilo}">
                <h2 style="color: black !important;">{'⚠️' if es_alerta else '👤'} {p.get('NOMBRE', 'N/A')}</h2>
                {f'<p style="color: #c53030; font-weight: bold;">ALERTA MÉDICA: {condiciones}</p>' if es_alerta else ''}
                <p><b>ID:</b> {id_bus} | <b>RH:</b> {p.get('RH', 'N/A')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'N/A')} | <b>CEL:</b> {p.get('CELULAR', 'N/A')}</p>
                <div class="emergency-box">
                    <p style="color: red !important; margin:0;"><b>🚨 CONTACTO DE EMERGENCIA:</b></p>
                    <p style="margin:0; color: black !important;"><b>Nombre:</b> {p.get('NOMBRE DEL CONTACTO DE EMERGENCIA', 'N/A')}</p>
                    <p style="margin:0; color: black !important;"><b>Tel:</b> {p.get('TELÉFONO CONTACTO DE EMERGENCIA', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- BOTÓN PDF (Mantiene el estilo pero añade la función) ---
            if st.button("🖨️ Imprimir / Guardar PDF"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

            # Historial y Formulario de evolución se mantienen abajo...
            with st.form("h_form", clear_on_submit=True):
                st.write("### ✍️ Registrar Evolución")
                t, m = st.text_input("Tratamiento"), st.text_area("Medicamentos")
                if st.form_submit_button("GUARDAR EN HISTORIAL"):
                    requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", 
                                  data={"entry.2019369477": id_bus, "entry.611862537": t, "entry.2016051626": m})
                    st.success("✅ Guardado."); st.cache_data.clear(); st.rerun()

elif st.session_state.menu == "Base":
    st.subheader("📊 Base de Datos")
    t1, t2 = st.tabs(["Pacientes", "Historial"])
    if df_p is not None: t1.dataframe(df_p)
    if df_h is not None: t2.dataframe(df_h)
