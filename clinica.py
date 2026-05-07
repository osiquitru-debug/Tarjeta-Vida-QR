import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
        margin-top: 15px; text-align: center;
    }
    .evo-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA Y NORMALIZACIÓN DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def normalizar_doc(valor):
    """Limpia el documento de decimales, espacios y puntos."""
    if pd.isna(valor): return ""
    # Convierte a string, quita el .0 si existe, y elimina espacios/puntos
    return str(valor).split('.')[0].replace(" ", "").replace(",", "").replace("-", "").strip()

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargar hojas como string para evitar que pandas convierta IDs en números
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Crear columna de búsqueda normalizada (usualmente es la columna B, índice 1)
        p['ID_BUSQUEDA'] = p.iloc[:, 1].apply(normalizar_doc)
        h['ID_BUSQUEDA'] = h.iloc[:, 1].apply(normalizar_doc)
        
        return p, h
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🩺 Menú Médico</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("Sistema de Gestión Tarjeta Vida")
    st.write("Bienvenido al panel de control médico.")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Nuevo Paciente")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de ID", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de ID")
            edad = st.text_input("Edad")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            c_nom = st.text_input("Contacto de Emergencia")
            c_tel = st.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE EN NUBE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    entrada_id = st.text_input("Ingrese Documento del Paciente:").strip()
    id_limpio = normalizar_doc(entrada_id)
    
    if id_limpio and df_p is not None:
        p_match = df_p[df_p["ID_BUSQUEDA"] == id_limpio]
        
        if not p_match.empty:
            p = p_match.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.iloc[2]}</h2>
                <p><b>ID:</b> {entrada_id} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <p><b>EPS:</b> {p.iloc[5]}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN (10 CAMPOS)"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo"); v3 = st.text_input("3. Talla")
                        v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión")
                    with c2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("💾 GUARDAR EVOLUCIÓN"):
                        h_pay = {
                            "entry.2019369477": id_limpio, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("✅ Evolución guardada exitosamente."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h["ID_BUSQUEDA"] == id_limpio].sort_index(ascending=False)
            if not h_p.empty:
                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"HC: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_p.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\nEPICRISIS: {r.iloc[10]}\n{'-'*50}")
                st.download_button("📥 Descargar PDF Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{id_limpio}.pdf", "application/pdf")

                for _, r in h_p.iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {r.iloc[0]}</small><br>
                    <b>Motivo:</b> {r.iloc[3]}<br><b>Valoración:</b> {r.iloc[2]}<br><b>Medicamentos:</b> {r.iloc[8]}</div>""", unsafe_allow_html=True)
            else: st.info("No se registran evoluciones para este paciente.")
        else:
            st.error("❌ El paciente no fue encontrado. Verifique que el documento en el Sheet no tenga caracteres extraños.")import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Tarjeta Vida | Gestión Médica", layout="centered", page_icon="🩺")

st.markdown("""
    <style>
    .stApp { background-color: #f0f7f4 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .medical-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #4fd1c5; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px; color: #1a202c;
    }
    .emergency-box {
        background-color: #fff5f5; padding: 15px; border-radius: 10px;
        border: 1px dashed #f56565; color: #c53030; font-weight: bold;
        margin-top: 15px; text-align: center;
    }
    .evo-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 5px solid #63b3ed; border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA Y NORMALIZACIÓN DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

def normalizar_doc(valor):
    """Limpia el documento de decimales, espacios y puntos."""
    if pd.isna(valor): return ""
    # Convierte a string, quita el .0 si existe, y elimina espacios/puntos
    return str(valor).split('.')[0].replace(" ", "").replace(",", "").replace("-", "").strip()

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        # Cargar hojas como string para evitar que pandas convierta IDs en números
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("")
        
        # Crear columna de búsqueda normalizada (usualmente es la columna B, índice 1)
        p['ID_BUSQUEDA'] = p.iloc[:, 1].apply(normalizar_doc)
        h['ID_BUSQUEDA'] = h.iloc[:, 1].apply(normalizar_doc)
        
        return p, h
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
if 'menu' not in st.session_state: st.session_state.menu = "Inicio"

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🩺 Menú Médico</h2>", unsafe_allow_html=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"
    if st.button("📝 Registrar Paciente", use_container_width=True): st.session_state.menu = "Registrar"
    if st.button("🔍 Consulta / Evolución", use_container_width=True): st.session_state.menu = "Consulta"

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("Sistema de Gestión Tarjeta Vida")
    st.write("Bienvenido al panel de control médico.")

elif st.session_state.menu == "Registrar":
    st.title("📝 Registro de Nuevo Paciente")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Completo")
            t_doc = st.selectbox("Tipo de ID", ["CC", "TI", "CE", "RC"])
            n_doc = st.text_input("Número de ID")
            edad = st.text_input("Edad")
        with c2:
            eps = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            c_nom = st.text_input("Contacto de Emergencia")
            c_tel = st.text_input("Teléfono de Emergencia")
        
        if st.form_submit_button("GUARDAR PACIENTE EN NUBE"):
            payload = {
                "entry.346175428": nombre, "entry.1650757004": t_doc, "entry.1302424820": n_doc,
                "entry.1801154005": edad, "entry.1172011247": eps, "entry.162368130": rh,
                "entry.1892763134": c_nom, "entry.2011749615": c_tel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta y Evolución")
    entrada_id = st.text_input("Ingrese Documento del Paciente:").strip()
    id_limpio = normalizar_doc(entrada_id)
    
    if id_limpio and df_p is not None:
        p_match = df_p[df_p["ID_BUSQUEDA"] == id_limpio]
        
        if not p_match.empty:
            p = p_match.iloc[0]
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.iloc[2]}</h2>
                <p><b>ID:</b> {entrada_id} | <b>Edad:</b> {p.iloc[4]} | <b>RH:</b> {p.iloc[6]}</p>
                <p><b>EPS:</b> {p.iloc[5]}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {p.iloc[7]} - {p.iloc[8]}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("✍️ REGISTRAR NUEVA EVOLUCIÓN (10 CAMPOS)"):
                with st.form("evo_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        v1 = st.text_area("1. Valoración"); v2 = st.text_area("2. Motivo"); v3 = st.text_input("3. Talla")
                        v4 = st.text_input("4. Peso"); v5 = st.text_input("5. Presión")
                    with c2:
                        v6 = st.text_area("6. Antecedentes"); v7 = st.text_area("7. Medicamentos")
                        v8 = st.text_area("8. Laboratorios"); v9 = st.text_area("9. Epicrisis")
                    
                    if st.form_submit_button("💾 GUARDAR EVOLUCIÓN"):
                        h_pay = {
                            "entry.2019369477": id_limpio, "entry.1088523869": v1, "entry.611862537": v2,
                            "entry.1275746503": v3, "entry.949747647": v4, "entry.2091389798": v5,
                            "entry.889985940": v6, "entry.2016051626": v7, "entry.882053172": v8, "entry.616774918": v9
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=h_pay)
                        st.success("✅ Evolución guardada exitosamente."); st.cache_data.clear(); st.rerun()

            st.subheader("📋 Historial de Evoluciones")
            h_p = df_h[df_h["ID_BUSQUEDA"] == id_limpio].sort_index(ascending=False)
            if not h_p.empty:
                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"HC: {p.iloc[2]}", ln=True)
                pdf.set_font("Arial", size=10)
                for _, r in h_p.iterrows():
                    pdf.multi_cell(0, 5, f"FECHA: {r.iloc[0]}\nVALORACION: {r.iloc[2]}\nMOTIVO: {r.iloc[3]}\nEPICRISIS: {r.iloc[10]}\n{'-'*50}")
                st.download_button("📥 Descargar PDF Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{id_limpio}.pdf", "application/pdf")

                for _, r in h_p.iterrows():
                    st.markdown(f"""<div class="evo-card"><small>📅 {r.iloc[0]}</small><br>
                    <b>Motivo:</b> {r.iloc[3]}<br><b>Valoración:</b> {r.iloc[2]}<br><b>Medicamentos:</b> {r.iloc[8]}</div>""", unsafe_allow_html=True)
            else: st.info("No se registran evoluciones para este paciente.")
        else:
            st.error("❌ El paciente no fue encontrado. Verifique que el documento en el Sheet no tenga caracteres extraños.")
